import logging
import re
from contextlib import suppress
from datetime import date, timedelta
from typing import Any, Generator, Iterator, Self, TypeVar

import pandas as pd
from celery import shared_task
from colorfield.fields import ColorField
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models, transaction
from django.db.models import Q, Value
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from dynamic_preferences.registries import global_preferences_registry
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from pandas.tseries.offsets import BDay
from rest_framework.reverse import reverse
from slugify import slugify
from tqdm import tqdm
from wbcore.content_type.utils import get_ancestors_content_type
from wbcore.contrib.dataloader.models import Entity
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.contrib.io.models import ImportedObjectProviderRelationship
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.contrib.tags.models import TagModelMixin
from wbcore.models import WBModel
from wbcore.signals import pre_merge
from wbcore.utils.models import ComplexToStringMixin
from wbnews.models import News
from wbnews.signals import create_news_relationships

from wbfdm.analysis import TechnicalAnalysis
from wbfdm.contrib.internal.dataloaders.market_data import MarketDataDataloader
from wbfdm.contrib.metric.dispatch import compute_metrics
from wbfdm.import_export.handlers.instrument import InstrumentImportHandler
from wbfdm.models.instruments.llm.create_instrument_news_relationships import (
    run_company_extraction_llm,
)
from wbfdm.preferences import get_default_classification_group
from wbfdm.signals import (
    add_instrument_to_investable_universe,
    instrument_price_imported,
    investable_universe_updated,
)

from ...analysis.financial_analysis.change_point_detection import outlier_detection, statistical_change_point_detection
from ...dataloaders.proxies import InstrumentDataloaderProxy
from .instrument_relationships import RelatedInstrumentThroughModel
from .mixin.instruments import InstrumentPMSMixin
from .querysets import InstrumentQuerySet
from .utils import re_bloomberg, re_isin, re_mnemonic, re_ric

logger = logging.getLogger("pms")


class InstrumentManager(TreeManager):
    def __init__(self, with_annotation: bool = False, *args, **kwargs):
        self.with_annotation = with_annotation
        super().__init__(*args, **kwargs)

    def _custom_rebuild_helper(self, node, left, tree_id, nodes_to_update, level):
        right = left + 1

        for child in node.children.all():
            right = self._custom_rebuild_helper(
                node=child,
                left=right,
                tree_id=tree_id,
                nodes_to_update=nodes_to_update,
                level=level + 1,
            )

        setattr(node, self._rebuild_fields["left"], left)
        setattr(node, self._rebuild_fields["right"], right)
        setattr(node, self._rebuild_fields["level"], level)
        setattr(node, self._rebuild_fields["tree_id"], tree_id)
        nodes_to_update.append(node)

        return right + 1

    def rebuild(self, batch_size=1000, debug: bool = False, **filters) -> None:
        """
        We supercharge MPTT rebuild manager method to avoid loading all instrument into memory
        """
        self._find_out_rebuild_fields()

        parents = self._get_parents(**filters)
        tree_id = filters.get("tree_id", 1)
        nodes_to_update = []
        if debug:
            gen = tqdm(enumerate(parents), total=len(parents))
        else:
            gen = enumerate(parents)
        for index, parent in gen:
            self._custom_rebuild_helper(
                node=parent,
                left=1,
                tree_id=tree_id + index,
                nodes_to_update=nodes_to_update,
                level=0,
            )
            if len(nodes_to_update) >= batch_size:
                self.bulk_update(
                    nodes_to_update,
                    self._rebuild_fields.values(),
                )
                nodes_to_update = []

        self.bulk_update(
            nodes_to_update,
            self._rebuild_fields.values(),
        )

    def get_queryset(self) -> InstrumentQuerySet:
        qs = InstrumentQuerySet(self.model, using=self._db)
        if self.with_annotation:
            qs = qs.annotate_all()
        return qs

    def annotate_classification_for_group(
        self, classification_group, classification_height: int = 0, **kwargs
    ) -> models.QuerySet:
        return self.get_queryset().annotate_classification_for_group(
            classification_group, classification_height=classification_height, **kwargs
        )

    def annotate_base_data(self):
        return self.get_queryset().annotate_base_data()

    def annotate_all(self):
        return self.get_queryset().annotate_all()

    def filter_active_at_date(self, val_date: date):
        return self.get_queryset().filter_active_at_date(val_date)

    def get_instrument_prices_from_market_data(self, **kwargs):
        return self.get_queryset().get_instrument_prices_from_market_data(**kwargs)

    def get_returns_df(self, **kwargs) -> tuple[dict[date, dict[int, float]], pd.DataFrame]:
        return self.get_queryset().get_returns_df(**kwargs)


class SecurityInstrumentManager(InstrumentManager):
    def get_queryset(self) -> InstrumentQuerySet:
        return super().get_queryset().filter(is_security=True)


class ClassifiableInstrumentManager(InstrumentManager):
    def get_queryset(self) -> InstrumentQuerySet:
        return super().get_queryset().filter(instrument_type__is_classifiable=True, level=0)


class ActiveInstrumentManager(InstrumentManager):
    def get_queryset(self):
        return super().get_queryset().filter_active_at_date(date.today())


class InvestableUniverseManager(InstrumentManager):
    def get_queryset(self) -> InstrumentQuerySet:
        instrument_ids = set()
        for _, ids in add_instrument_to_investable_universe.send(sender=Instrument):
            instrument_ids.update(ids)
        return (
            super()
            .get_queryset()
            .annotate_base_data()
            .filter(is_investable=True)
            .filter(
                Q(is_investable_universe=True)
                | Q(
                    dependent_instruments_through__isnull=False
                )  # we consider instrument that are "related" to other instrument as within the investable universe by default
                | Q(id__in=instrument_ids)
                | Q(is_managed=True)
                | Q(
                    dl_parameters__market_data__path="wbfdm.contrib.internal.dataloaders.market_data.MarketDataDataloader"
                )
            )
        )


class InvestableInstrumentManager(InstrumentManager):
    def get_queryset(self) -> InstrumentQuerySet:
        return super().get_queryset().filter(children__isnull=True)


SelfInstrument = TypeVar("SelfInstrument", bound="Instrument")


class InstrumentType(models.Model):
    name = models.CharField(max_length=128, verbose_name="Name")
    short_name = models.CharField(max_length=128, verbose_name="Short Name")
    name_repr = models.CharField(max_length=128, verbose_name="Name (Representation)")
    key = models.CharField(max_length=32, verbose_name="Key", unique=True)
    description = models.TextField(verbose_name="Description", blank=True)

    is_classifiable = models.BooleanField(default=True, verbose_name="Classifiable")
    is_security = models.BooleanField(default=True, verbose_name="Security")

    @classmethod
    @property
    def PRODUCT(cls):
        return InstrumentType.objects.get_or_create(
            key="product", defaults={"name": "Product", "short_name": "Product"}
        )[0]

    @classmethod
    @property
    def EQUITY(cls):
        return InstrumentType.objects.get_or_create(key="equity", defaults={"name": "equity", "short_name": "equity"})[
            0
        ]

    @classmethod
    @property
    def INDEX(cls):
        return InstrumentType.objects.get_or_create(key="index", defaults={"name": "Index", "short_name": "Index"})[0]

    @classmethod
    @property
    def CASH(cls):
        return InstrumentType.objects.get_or_create(key="cash", defaults={"name": "Cash", "short_name": "Cash"})[0]

    @classmethod
    @property
    def CASHEQUIVALENT(cls):
        return InstrumentType.objects.get_or_create(
            key="cash_equivalent", defaults={"name": "Cash Equivalents", "short_name": "Cash Equivalents"}
        )[0]

    @classmethod
    @property
    def PRODUCT_GROUP(cls):
        return InstrumentType.objects.get_or_create(
            key="product_group", defaults={"name": "Product Group", "short_name": "Product Group"}
        )[0]

    def save(self, *args, **kwargs):
        if not self.short_name:
            self.short_name = self.name
        if not self.key:
            self.key = slugify(self.name, separator="_")
        if not self.name_repr:
            self.name_repr = self.name
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbfdm:instrumenttyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"


class Instrument(ComplexToStringMixin, TagModelMixin, ImportMixin, InstrumentPMSMixin, WBModel, Entity, MPTTModel):
    COMPUTED_STR_RECOMPUTE_PERIODICALLY: bool = False
    # COMPUTED_STR_RECOMPUTE_ON_SAVE: bool = False # I am commenting this out because we need computed str to be recomputed on save but do not know why this would be an issue

    import_export_handler_class = InstrumentImportHandler
    dl_proxy = InstrumentDataloaderProxy

    parent = TreeForeignKey(
        "self",
        related_name="children",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Parent Instrument",
    )
    name = models.CharField(max_length=512)
    description = models.TextField(default="", blank=True, null=True)
    instrument_type = models.ForeignKey(
        "wbfdm.InstrumentType", related_name="instruments", null=True, blank=True, on_delete=models.PROTECT
    )

    inception_date = models.DateField(null=True, blank=True)
    delisted_date = models.DateField(null=True, blank=True)
    last_valuation_date = models.DateField(
        null=True, blank=True, verbose_name="Last Valuation Date", help_text="Last Valuation Date"
    )
    last_price_date = models.DateField(
        null=True, blank=True, verbose_name="Last Price Date", help_text="Last Price Date"
    )
    # The report date fields store the actual dates when a report happens, not the end of a period.
    last_annual_report = models.DateField(null=True, blank=True)
    last_interim_report = models.DateField(null=True, blank=True)
    next_annual_report = models.DateField(null=True, blank=True)
    next_interim_report = models.DateField(null=True, blank=True)

    country = models.ForeignKey(
        to="geography.Geography",
        null=True,
        blank=True,
        limit_choices_to={"level": 1},
        on_delete=models.SET_NULL,
    )

    currency = models.ForeignKey(
        to="currency.Currency",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    exchange = models.ForeignKey(
        to="wbfdm.Exchange", null=True, blank=True, on_delete=models.PROTECT, related_name="instruments"
    )
    round_lot_size = models.IntegerField(
        default=1,
        verbose_name="Round Lot Size",
        help_text="A round lot (or board lot) is the normal unit of trading of a security.",
    )

    source_id = models.CharField(max_length=64, null=True, blank=True)
    source = models.CharField(max_length=64, null=True, blank=True)

    # Other fields from PMS
    founded_year = models.IntegerField(null=True, blank=True, verbose_name="Founded Year")
    identifier = models.CharField(
        max_length=255,
        verbose_name="Identifier",
        null=True,
        blank=True,
    )
    name_repr = models.CharField(max_length=255, null=True, blank=True, verbose_name="Name (Representation)")
    last_update = models.DateTimeField(auto_now=True, blank=True, null=True)
    alternative_names = ArrayField(models.CharField(blank=True, null=True, max_length=255), default=list, blank=True)
    isin = models.CharField(
        null=True,
        blank=True,
        max_length=12,
        verbose_name="ISIN",
        help_text="The ISIN provided by the bank.",
    )

    ticker = models.CharField(
        max_length=255,
        verbose_name="Ticker Bloomberg",
        help_text="The Bloomberg ticker without the exchange (e.g. AAPL)",
        blank=True,
        null=True,
    )

    old_isins = ArrayField(
        base_field=models.CharField(max_length=12),
        default=list,
        blank=True,
        verbose_name="Old ISINS",
        help_text="These old ISINs are stored for this instrument to retrieve it more easily later.",
    )
    sedol = models.CharField(
        max_length=255,
        verbose_name="SEDOL",
        help_text="Stock Exchange Daily Official List",
        blank=True,
        null=True,
    )

    valoren = models.CharField(
        max_length=255,
        verbose_name="Valoren Number",
        help_text="Valoren Number",
        blank=True,
        null=True,
    )

    cusip = models.CharField(
        max_length=255,
        verbose_name="CUSIP",
        help_text="CUSIP",
        blank=True,
        null=True,
    )

    refinitiv_ticker = models.CharField(
        max_length=255,
        verbose_name="Refinitiv Ticker",
        help_text="Refinitiv Refinitiv",
        blank=True,
        null=True,
    )
    refinitiv_identifier_code = models.CharField(
        max_length=255,
        verbose_name="RIC",
        help_text="Refinitiv Identifier Code",
        blank=True,
        null=True,
    )

    refinitiv_mnemonic_code = models.CharField(
        max_length=255,
        verbose_name="Refinitiv Datastream Mnemonic Code",
        help_text="Refinitiv Datastream Mnemonic Code",
        blank=True,
        null=True,
    )

    headquarter_address = models.CharField(
        max_length=512, blank=True, null=True, help_text="The company Headquarter address"
    )
    headquarter_city = models.ForeignKey(
        "geography.Geography",
        related_name="headquarters_of",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Headquarter City",
        help_text="The company's headquarter city",
        limit_choices_to={"level": 3},
    )
    employees = models.IntegerField(null=True, blank=True)

    primary_url = models.URLField(blank=True, null=True, help_text="The Company website url")
    additional_urls = ArrayField(models.URLField(blank=True, null=True), default=list, blank=True)

    related_instruments = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="benchmarks_of",
        through="wbfdm.RelatedInstrumentThroughModel",
        through_fields=("instrument", "related_instrument"),
        blank=True,
        verbose_name="The Related Instruments",
    )

    classifications = models.ManyToManyField(
        "wbfdm.Classification",
        through="wbfdm.InstrumentClassificationThroughModel",
        limit_choices_to=models.Q(level=models.F("group__max_depth")),
        related_name="instruments",
        blank=True,
        verbose_name="Classifications",
    )
    is_cash = models.BooleanField(default=False)
    is_cash_equivalent = models.BooleanField(default=False)
    issue_price = models.PositiveIntegerField(
        default=100,
        verbose_name="Issue Price",
        help_text="The initial issue price that is displayed on the factsheet",
    )
    base_color = ColorField(
        blank=True, null=True, max_length=64, default="#FF0000"
    )  # we need this field for pms breakdown.

    is_security = models.BooleanField(default=False)
    is_managed = models.BooleanField(default=False)
    is_primary = models.BooleanField(null=True, blank=True)
    is_investable_universe = models.BooleanField(
        default=False,
        verbose_name="In Investable Universe",
        help_text="If True, the instrument belongs to the investable universe",
    )

    search_vector = SearchVectorField(null=True)
    trigram_search_vector = models.CharField(max_length=1024, null=True, blank=True)

    objects = InstrumentManager()
    annotated_objects = InstrumentManager(with_annotation=True)
    active_objects = ActiveInstrumentManager()
    securities = SecurityInstrumentManager()
    classifiables = ClassifiableInstrumentManager()
    investables = InvestableInstrumentManager()
    investable_universe = InvestableUniverseManager()

    class Meta:
        verbose_name = "Instrument"
        verbose_name_plural = "Instruments"
        permissions = (("administrate_instrument", "Can administrate Instrument"),)
        constraints = [
            models.UniqueConstraint(fields=["source_id", "source"], name="unique_source"),
            models.UniqueConstraint(
                fields=["refinitiv_identifier_code"],
                name="unique_ric",
                condition=models.Q(is_security=True) & models.Q(delisted_date__isnull=True),
            ),
            models.UniqueConstraint(
                fields=["refinitiv_mnemonic_code"],
                name="unique_rmc",
                condition=models.Q(is_security=True) & models.Q(delisted_date__isnull=True),
            ),
            models.UniqueConstraint(
                fields=["isin"],
                name="unique_isin",
                condition=models.Q(is_security=True) & models.Q(delisted_date__isnull=True),
            ),
            models.UniqueConstraint(
                fields=["sedol"],
                name="unique_sedol",
                condition=models.Q(is_security=True) & models.Q(delisted_date__isnull=True),
            ),
            models.UniqueConstraint(
                fields=["valoren"],
                name="unique_valoren",
                condition=models.Q(is_security=True) & models.Q(delisted_date__isnull=True),
            ),
            models.UniqueConstraint(
                fields=["cusip"],
                name="unique_cusip",
                condition=models.Q(is_security=True) & models.Q(delisted_date__isnull=True),
            ),
            models.UniqueConstraint(
                fields=["parent", "is_primary"],
                name="unique_instrument_primary",
                condition=models.Q(is_primary=True) & models.Q(is_managed=False),
            ),
        ]
        indexes = [
            models.Index(fields=["parent"], name="instrument_parent_index"),
            models.Index(fields=["parent", "exchange", "isin"], name="instrument_children_index"),
            models.Index(fields=["is_investable_universe"], name="instrument_investible_index"),
            models.Index(fields=["is_security"], name="instrument_security_index"),
            models.Index(fields=["level"], name="instrument_level_index"),
            GinIndex(fields=["search_vector"], name="instrument_sv_gin_idx"),  # type: ignore
            GinIndex(
                fields=["trigram_search_vector"], opclasses=["gin_trgm_ops"], name="instrument_trigram_sv_gin_idx"
            ),  # type: ignore
        ]
        notification_types = [
            create_notification_type(
                code="wbfdm.instrument.notify",
                title="Instrument Notification",
                help_text="Sends a notification when there is an update about an instrument",
            )
        ]

    def get_tag_detail_endpoint(self):
        return reverse("wbfdm:instrument-detail", [self.id])

    def get_tag_representation(self):
        return self.computed_str

    @property
    @admin.display(description="Is Investable")
    def _is_investable(self):
        return getattr(self, "is_investable", not self.children.exists())

    @property
    @admin.display(description="Primary Benchmark")
    def primary_benchmark(self):
        if primary_through := RelatedInstrumentThroughModel.objects.filter(
            instrument=self, is_primary=True, related_type=RelatedInstrumentThroughModel.RelatedTypeChoices.BENCHMARK
        ).first():
            return primary_through.related_instrument
        return None

    @property
    @admin.display(description="Primary Peer")
    def primary_peer(self):
        if primary_through := RelatedInstrumentThroughModel.objects.filter(
            instrument=self, is_primary=True, related_type=RelatedInstrumentThroughModel.RelatedTypeChoices.PEER
        ).first():
            return primary_through.related_instrument
        return None

    @property
    @admin.display(description="Primary Risk Instrument")
    def primary_risk_instrument(self):
        if primary_through := RelatedInstrumentThroughModel.objects.filter(
            instrument=self,
            is_primary=True,
            related_type=RelatedInstrumentThroughModel.RelatedTypeChoices.RISK_INSTRUMENT,
        ).first():
            return primary_through.related_instrument
        return None

    @property
    @admin.display(description="Primary Classification")
    def primary_classification(self):
        if primary_classification := self.classifications.filter(group__is_primary=True).first():
            return primary_classification

    @property
    @admin.display(description="Favorite Classification")
    def favorite_classification(self):
        if favorite_classification := self.classifications.filter(group=get_default_classification_group()).first():
            return favorite_classification

    def get_primary_quote(self):
        if self.children.exists():
            # we try the primary children first, then the first children within the investable universe and we fallback to the first children otherwise
            try:
                instrument = self.children.get(is_primary=True)
            except Instrument.DoesNotExist:
                instrument = self.children.filter(is_investable_universe=True).first()
                if not instrument:
                    instrument = self.children.first()
            return instrument.get_primary_quote()
        return self

    @property
    def active(self) -> bool:
        today = date.today()
        return (
            self.inception_date
            and self.inception_date <= today
            and (not self.delisted_date or self.delisted_date > today)
        )

    @property
    def identifier_repr(self) -> str:
        identifiers = []
        if self.is_security:
            identifier_labels = ["ticker", "refinitiv_identifier_code", "refinitiv_mnemonic_code"]
        else:
            identifier_labels = ["refinitiv_mnemonic_code"]
        for label in identifier_labels:
            if v := getattr(self, label, None):
                identifiers.append(v)
                break
        if self.isin and self.is_security:
            identifiers.append(self.isin)

        return " - ".join(identifiers).replace(":", "-")

    @property
    def valuations(self):
        try:
            return self.prices.filter(calculated=False)
        except (
            ValueError
        ):  # ValueError because if this property is called before the instance has a primary key, it will fail
            return Instrument.objects.none()

    @property
    def security_instrument_type(self):
        while not self.instrument_type.is_security and self.parent:
            return self.parent.security_instrument_type
        return self.instrument_type

    def update_search_vectors(self):
        names = list(map(lambda x: Value(x), filter(None, [self.name, *self.alternative_names])))
        if names:
            isins = list(map(lambda x: Value(x), filter(None, [self.isin, *self.old_isins])))
            identifiers = list(
                map(
                    lambda x: Value(re.sub(r"[^a-zA-Z0-9]", "", x.lower())),
                    filter(
                        None,
                        [
                            self.ticker,
                            self.refinitiv_identifier_code,
                            self.refinitiv_mnemonic_code,
                            self.valoren,
                            self.sedol,
                        ],
                    ),
                )
            )
            self.search_vector = SearchVector(*names, weight="D")
            if identifiers:
                self.search_vector += SearchVector(*identifiers, weight="A")
            if isins:
                self.search_vector += SearchVector(*isins, weight="A")
            self.trigram_search_vector = f"{self.name} {' '.join(self.alternative_names)}".strip()

    def clean(self):
        if self.is_investable_universe and self.id and self.children.exists():
            raise ValidationError("An instrument in the investable universe cannot have children")
        return self

    def pre_save(self):
        if self.instrument_type:
            self.is_security = self.instrument_type.is_security
        if self.delisted_date:
            self.is_security = False
        if not self.name_repr:
            self.name_repr = self.name
        if not self.founded_year and self.inception_date:
            self.founded_year = self.inception_date.year
        if not self.inception_date:
            self.inception_date = date.today() - timedelta(days=1)
        if not self.founded_year:
            self.founded_year = self.inception_date.year
        if self.level is None:
            self.level = 0
            self.rght = 0
            self.lft = 0
            self.tree_id = 0

        # ensure all identifiers are stored in uppercase and do not contain any whitespace
        for identifier_key in ["isin", "refinitiv_mnemonic_code", "ticker", "sedol", "cusip", "identifier"]:
            if identifier := getattr(self, identifier_key, None):
                setattr(self, identifier_key, identifier.upper().replace(" ", ""))
        if self.refinitiv_identifier_code:
            self.refinitiv_identifier_code = self.refinitiv_identifier_code.replace(
                " ", ""
            )  # RIC cannot be uppercased because its symbology implies meaning for lowercase characters
        self.update_search_vectors()
        if self.is_primary and (parent := self.parent):
            # we have a unique constraint on parent. We take the time to make sure no other children is already primary = True (otherwise, update will fail)
            Instrument.objects.filter(parent=parent, is_primary=True).exclude(
                source=self.source, source_id=self.source_id
            ).update(is_primary=False)
        if not self.parent:
            self.is_primary = True
        if self.id and (not self.instrument_type or not self.currency) and self.children.count() == 1:
            child = self.children.first()
            if not self.instrument_type:
                self.instrument_type = child.instrument_type
            if not self.currency:
                self.currency = child.currency

    def save(self, *args, **kwargs):
        self.pre_save()
        if self.is_primary is None:
            self.is_primary = not self.parent or (self.exchange is not None and self.parent.exchange == self.exchange)
        super().save(*args, **kwargs)

    def get_compute_str(self):
        repr = self.name_repr or self.name or ""
        repr = repr.title()  # we follow bloomberg instrument representation format
        if self.instrument_type and self.is_security:
            repr += f" {self.instrument_type.short_name}"
        if self.is_security or not self.level == 0:
            if self.identifier_repr:
                repr += f" - {self.identifier_repr}"
            # if the object has an exchange and is not a security nor a company (a quote then), we append the exchange representation
            if self.exchange and self.parent is not None and not self.is_security:
                repr += f" ({str(self.exchange)})"
        return repr

    def compute_str(self):
        return self.get_compute_str()

    def is_active_at_date(self, today: date) -> bool:
        return (
            self.inception_date is not None
            and self.inception_date <= today
            and (not self.delisted_date or self.delisted_date > today)
        )

    def update_last_valuation_date(self):
        if self.valuations.exists():
            earliest_valuation = self.valuations.earliest("date")
            last_valuation = self.valuations.latest("date").date
            if not self.inception_date or (
                not earliest_valuation.calculated and self.inception_date > earliest_valuation.date
            ):
                self.inception_date = earliest_valuation.date
            if not self.last_valuation_date or last_valuation >= self.last_valuation_date:
                self.last_valuation_date = last_valuation
        if self.prices.exists():
            last_price = self.prices.latest("date").date
            if not self.last_price_date or last_price >= self.last_price_date:
                self.last_price_date = last_price
            self.save()
            compute_metrics(last_price, basket=self)

    def get_prices(self, only_instrument_price: bool = False, **kwargs) -> Iterator[dict[str, any]]:
        qs = Instrument.objects.filter(id=self.id)
        if "market_data" in self.dl_parameters and not only_instrument_price:
            return qs.dl.market_data(**kwargs)
        # if not dataloader is found, we default to the internal instrument price dataloader
        return MarketDataDataloader(qs).market_data(**kwargs)

    def get_classifable_ancestor(self, include_self: bool = True) -> Self:
        root = self.get_root()
        if root.instrument_type and root.instrument_type.is_classifiable:
            return root

    def get_security_ancestor(self, include_self: bool = True) -> Self:
        if include_self:
            parent = self
        else:
            parent = self.parent
        while parent:
            if parent.instrument_type and parent.instrument_type.is_security:
                return parent
            parent = parent.parent

    def merge(self, merged_instrument: SelfInstrument, dispatch: bool = True, override_fields_to_copy: bool = False):
        """
        This method handle the deletion of an instrument ("merged_instrument") in favor of another one (self).

        After handling all the instrument base logic reassignment, it calls a signal that all modules can implement in
        order to implement their own reassignment logic.

        The function is atomic, it either succeed or fail (i.e. If merged_instrument is deleted, the merge was succeesful)

        Args:
            merged_instrument: The Instrument that is supposed to be merged and deleted
        """
        if self == merged_instrument:
            return
        with transaction.atomic():  # We want this to either succeed fully or fail
            # Get the base
            if dispatch:
                pre_merge.send(
                    sender=Instrument, merged_object=merged_instrument, main_object=self
                )  # default signal dispatch for the Instrument class

                # if the self type is different than Instrument, it's a polymorphic call. We fire also the pre_merge signal with this child type
                if type(self) is not Instrument:  # noqa
                    pre_merge.send(sender=self.__class__, merged_object=merged_instrument, main_object=self)

                # We refresh the reference in case the underlying signal receivers modify these objects
                self.refresh_from_db()
                merged_instrument.refresh_from_db()

            # We delete finally the merged instrument. All unlikage should have been done in the signal receivers function
            merged_instrument.delete()

            # Finally, we copy the potentially missing field from merged instrument to self (Only if self.field is None)
            field_to_copy = [
                "founded_year",
                "inception_date",
                "delisted_date",
                "name",
                "name_repr",
                "description",
                "ticker",
                "country",
                "headquarter_address",
                "headquarter_city",
                "primary_url",
                "identifier",
                "currency",
                "isin",
                "sedol",
                "valoren",
                "refinitiv_ticker",
                "refinitiv_identifier_code",
                "refinitiv_mnemonic_code",
                "exchange",
                "source",
                "source_id",
                "employees",
                "last_annual_report",
                "last_interim_report",
                "next_annual_report",
                "next_interim_report",
                "parent",
            ]
            many_fields = [
                "alternative_names",
                "old_isins",
                "additional_urls",
            ]
            for field in field_to_copy:
                if (new_value := getattr(merged_instrument, field, None)) is not None and (
                    getattr(self, field, None) is None or override_fields_to_copy
                ):
                    setattr(self, field, new_value)
            for field in many_fields:
                current_values = getattr(self, field, [])
                new_values = getattr(merged_instrument, field, [])
                setattr(self, field, list(set(current_values + new_values)))
            self.save()

    def handle_backend_lookup(self, attribute: str, method: str):
        try:
            backend = self.lookups.get(**{attribute: True}).load_backend()
            return getattr(backend, method)()
        except ObjectDoesNotExist:
            return self.__class__.objects.none()

    def technical_analysis(self, from_date: date | None = None, to_date: date | None = None):
        return TechnicalAnalysis.init_full_from_instrument(self, from_date, to_date)

    def technical_benchmark_analysis(self, from_date: date | None = None, to_date: date | None = None):
        return TechnicalAnalysis.init_close_from_instrument(self, from_date, to_date)

    def import_prices(self, start: date | None = None, end: date | None = None, **kwargs):
        if not self.is_leaf_node():
            raise ValueError("Cannot import price on a non-leaf node")
        if not start:
            start = (
                self.inception_date
                if self.inception_date
                else global_preferences_registry.manager()["wbfdm__default_start_date_historical_import"]
            )
        if not end:
            end = (
                date.today() - BDay(1)
            ).date()  # we don't import today price in case the dataloader returns duplicates (e.g. DSWS)

        # we detect when was the last date price imported before start and switch the start date from there
        with suppress(ObjectDoesNotExist):
            start = self.prices.filter(date__lte=start).latest("date").date
        # Import instrument prices
        objs = list(self.__class__.objects.filter(id=self.id).get_instrument_prices_from_market_data(start, end))
        self.bulk_save_instrument_prices(objs)
        # compute daily statistics & performances
        self.update_last_valuation_date()
        instrument_price_imported.send(sender=Instrument, instrument=self, start=start, end=end)

    @classmethod
    def parse_content_for_identifiers(cls, content: str) -> Generator[dict[str, Any], None, None]:
        for ric in re_ric(content):
            yield {"refinitiv_identifier_code": ric}
        for isin in re_isin(content):
            yield {"isin": isin}
        for ticker in re_bloomberg(content):
            yield {"ticker": ticker}
        for mnemonic in re_mnemonic(content):
            yield {"refinitiv_mnemonic_code": mnemonic}

    @classmethod
    def get_endpoint_basename(cls):
        return "wbfdm:instrument"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbfdm:instrumentrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{computed_str}}"


@shared_task(queue="portfolio")
def import_prices_as_task(instrument_id, **kwargs):
    instrument = Instrument.objects.get(id=instrument_id)
    instrument.import_prices(**kwargs)


@receiver(pre_delete, sender="wbfdm.Instrument")
def pre_delete_instrument(sender, instance, **kwargs):
    ImportedObjectProviderRelationship.objects.filter(
        content_type__in=get_ancestors_content_type(ContentType.objects.get_for_model(instance)), object_id=instance.id
    ).delete()


@receiver(pre_save, sender="wbfdm.Instrument")
def pre_save_instrument(sender, instance, raw, **kwargs):
    if not raw:
        pre_instance = None
        if instance.id:
            pre_instance = sender.objects.get(id=instance.id)
        # Remove duplicates if existings
        instance.old_isins = list(set(instance.old_isins))
        if pre_instance:
            if (
                pre_instance.isin
                and instance.isin
                and pre_instance.isin != instance.isin
                and pre_instance.isin not in instance.old_isins
            ):
                instance.old_isins = [*instance.old_isins, pre_instance.isin]
            if pre_instance.name_repr != instance.name_repr:
                # if a family member get is name representation updated, we update it for the whole family
                pre_instance.get_family().update(name_repr=instance.name_repr)

        # the instrument was manually included into the investable universe, in that case, we need to fetch the price
        if (
            instance.is_leaf_node()
            and (not pre_instance or not pre_instance.is_investable_universe)
            and instance.is_investable_universe
        ):
            import_prices_as_task.apply_async(
                (instance.id,), {"clear": True}, countdown=15
            )  # we need to introduce a countdown to avoid racing condition where save resumed after shared task picked up its instance reference.


@receiver(post_save, sender="wbfdm.Classification")
def ensure_classification_0_height(sender, instance, created, raw, **kwargs):
    # Ensure that if a leaf classification becomes non-leaf, then all instruments linked to it are updated automatically
    # with the new leaf classiciation
    if not raw and instance.parent and instance.height == 0:
        for instrument in Instrument.objects.filter(classifications=instance.parent):
            instrument.classifications.remove(instance.parent)
            instrument.classifications.add(instance)


@receiver(post_delete, sender="wbfdm.InstrumentPrice")
def post_delete_valuation(sender, instance, **kwargs):
    if not instance.calculated and instance.instrument.last_valuation_date == instance.date:
        instance.instrument.update_last_valuation_date()


class CashManager(InstrumentManager):
    def get_queryset(self) -> InstrumentQuerySet:
        return super().get_queryset().filter(instrument_type=InstrumentType.CASH)


class Cash(Instrument):
    objects = CashManager()

    def save(self, *args, **kwargs):
        self.is_cash = True
        self.dl_parameters["market_data"] = {
            "path": "wbfdm.contrib.internal.dataloaders.market_data.MarketDataDataloader"
        }

        super().save(*args, **kwargs)

    class Meta:
        proxy = True


@receiver(post_save, sender="currency.Currency")
def create_cash_from_currency(sender, instance, created, raw, **kwargs):
    if created:
        Cash.objects.get_or_create(
            instrument_type=InstrumentType.CASH, currency=instance, defaults={"name": f"Cash {instance.key}"}
        )


class EquityManager(InstrumentManager):
    def get_queryset(self) -> InstrumentQuerySet:
        return super().get_queryset().filter(instrument_type__key="equity")


class Equity(Instrument):
    objects = EquityManager()

    class Meta:
        proxy = True


@receiver(create_news_relationships, sender="wbnews.News")
def get_news_relationships_for_instruments_task(sender: type, instance: "News", **kwargs) -> shared_task:
    return run_company_extraction_llm.s(instance.title, instance.description, instance.summary)


@shared_task(queue="pms")
def detect_and_correct_financial_timeseries(
    max_days_interval: int | None = None,
    check_date: date | None = None,
    with_pelt: bool = False,
    detect_only: bool = False,
    full_reimport: bool = False,
    debug: bool = False,
):
    """Detects and corrects anomalies in financial time series data for instruments.

    Analyzes price data using statistical methods to identify outliers and change points,
    then triggers price reimport for affected date ranges when corrections are needed.

    Args:
        max_days_interval: Maximum lookback window in days for analysis (None = all history)
        check_date: Reference date for analysis (defaults to current date)
        with_pelt: Enable Pelt's change point detection alongside basic z-score outlier detection
        detect_only: Run detection without performing data correction/reimport
        full_reimport: Reimport entire price history when corruption detected (requires max_days_interval=None)
        debug: Show progress bar during instrument processing

    """
    if not check_date:
        check_date = date.today()
    gen = (
        Instrument.investable_universe.filter(is_managed=False)
        .filter_active_at_date(check_date)
        .exclude(source="dsws")
    )
    if debug:
        gen = tqdm(gen, total=gen.count())
    for instrument in gen:
        prices = instrument.valuations.all()
        if max_days_interval:
            prices = prices.filter(date__gte=check_date - timedelta(days=max_days_interval))
        # construct the price timeseries
        prices_series = (
            pd.DataFrame(
                prices.filter_only_valid_prices().values_list("date", "net_value"), columns=["date", "net_value"]
            )
            .set_index("date")["net_value"]
            .astype(float)
            .sort_index()
        )
        if not prices_series.empty:
            outliers = outlier_detection(prices_series).index.tolist()
            # if pelt enable, add the outliers found by the PELT model
            if with_pelt:
                outliers.extend(statistical_change_point_detection(prices_series).index.tolist())
            if outliers:
                logger.info(f"Abnormal change point detected for {instrument} at {outliers}.")
                if not detect_only:
                    # for a full reimport, we delete the whole existing price series and reimport since inception
                    if full_reimport and not max_days_interval:
                        start_import_date = instrument.inception_date
                        end_import_date = check_date
                        instrument.prices.filter(assets__isnull=True).delete()
                    else:
                        start_import_date = min(outliers) - timedelta(days=7)
                        end_import_date = max(outliers) + timedelta(days=7)
                    logger.info(f"Reimporting price from {start_import_date} to {end_import_date}...")
                    instrument.import_prices(start=start_import_date, end=end_import_date)


@receiver(investable_universe_updated, sender="wbfdm.Instrument")
def investable_universe_change_point_detection(*args, end_date: date | None = None, **kwargs):
    detect_and_correct_financial_timeseries.delay(check_date=end_date, max_days_interval=365)
