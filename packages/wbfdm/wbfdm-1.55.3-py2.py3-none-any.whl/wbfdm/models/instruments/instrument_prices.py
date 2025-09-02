from contextlib import suppress
from decimal import Decimal

import pandas as pd
from celery import shared_task
from django.db import models, transaction
from django.db.models import (
    Case,
    DecimalField,
    Exists,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.models import DynamicDecimalField, DynamicFloatField, DynamicModel, WBModel
from wbcore.signals import pre_merge

from wbfdm.analysis.financial_analysis.financial_statistics_analysis import (
    FinancialStatistics,
)
from wbfdm.import_export.handlers.instrument_price import InstrumentPriceImportHandler

from .mixin.financials_computed import InstrumentPriceComputedMixin


class ValidPricesQueryset(QuerySet):
    def filter_only_valid_prices(self) -> QuerySet:
        """
        Filter the queryset to remove duplicate in case calculated and non-calculated prices are present for the same date/product/type
        """
        return self.annotate(
            real_price_exists=Exists(
                self.filter(
                    instrument=OuterRef("instrument"),
                    date=OuterRef("date"),
                    calculated=False,
                )
            )
        ).filter(Q(calculated=False) | (Q(real_price_exists=False) & Q(calculated=True)))

    def annotate_market_data(self):
        base_qs = ValidPricesQueryset(self.model, using=self._db)

        return self.annotate(
            currency_fx_rate_to_usd_rate=F("currency_fx_rate_to_usd__value"),
            calculated_outstanding_shares=Subquery(
                base_qs.filter(instrument=OuterRef("instrument"), calculated=True, date=OuterRef("date")).values(
                    "outstanding_shares"
                )[:1]
            ),
            internal_outstanding_shares=ExpressionWrapper(
                Case(  # Annotate the parent security if exists
                    When(
                        outstanding_shares__isnull=False,
                        then=F("outstanding_shares"),
                    ),
                    default=F("calculated_outstanding_shares"),
                ),
                output_field=DecimalField(max_digits=4),
            ),
            internal_market_capitalization=Case(
                When(
                    market_capitalization__isnull=True,
                    then=ExpressionWrapper(
                        F("internal_outstanding_shares") * F("net_value"),
                        output_field=DecimalField(max_digits=4),
                    ),
                ),
                default=ExpressionWrapper(F("market_capitalization"), output_field=DecimalField(max_digits=4)),
            ),
            internal_market_capitalization_usd=F("internal_market_capitalization") / F("currency_fx_rate_to_usd_rate"),
            calculated_volume=Subquery(
                base_qs.filter(instrument=OuterRef("instrument"), calculated=True, date=OuterRef("date")).values(
                    "volume"
                )[:1]
            ),
            internal_volume=ExpressionWrapper(
                Case(  # Annotate the parent security if exists
                    When(
                        volume__isnull=False,
                        then=F("volume"),
                    ),
                    default=F("calculated_volume"),
                ),
                output_field=models.FloatField(),
            ),
        )

    def annotate_base_data(self):
        return self.annotate(
            currency_fx_rate_to_usd_rate=F("currency_fx_rate_to_usd__value"),
            market_capitalization_usd=ExpressionWrapper(
                F("market_capitalization") / F("currency_fx_rate_to_usd_rate"), output_field=DecimalField(max_digits=4)
            ),
            net_value_usd=F("net_value") / F("currency_fx_rate_to_usd_rate"),
            gross_value_usd=F("gross_value") / F("currency_fx_rate_to_usd_rate"),
            volume_usd=ExpressionWrapper(
                F("volume") * F("net_value") / F("currency_fx_rate_to_usd_rate"), output_field=DecimalField()
            ),
            volume_50d_usd=ExpressionWrapper(
                F("volume_50d") * F("net_value") / F("currency_fx_rate_to_usd_rate"), output_field=DecimalField()
            ),
            volume_200d_usd=ExpressionWrapper(
                F("volume_200d") * F("net_value") / F("currency_fx_rate_to_usd_rate"), output_field=DecimalField()
            ),
        )

    def annotate_security_data(self):
        return self.annotate(
            security=Case(  # Annotate the parent security if exists
                When(instrument__parent__isnull=False, then=F("instrument__parent")),
                default=F("instrument"),
            ),
            security_instrument_type_key=Case(  # Annotate the parent security if exists
                When(
                    instrument__parent__isnull=False,
                    then=F("instrument__parent__instrument_type__key"),
                ),
                default=F("instrument__instrument_type__key"),
            ),
        )

    def annotate_all(self):
        return self.annotate_market_data().annotate_security_data().annotate_base_data()


class InstrumentPriceManager(models.Manager):
    def __init__(self, with_annotation: bool = False, *args, **kwargs):
        self.with_annotation = with_annotation
        super().__init__(*args, **kwargs)

    def get_queryset(self) -> ValidPricesQueryset:
        qs = ValidPricesQueryset(self.model)
        if self.with_annotation:
            qs = qs.annotate_all()
        return qs

    def filtered_by_instruments(self, instrument_queryset, *other_instruments):
        return self.filter(models.Q(instrument__in=instrument_queryset) | models.Q(instrument__in=other_instruments))

    def filter_only_valid_prices(self) -> QuerySet:
        return self.get_queryset().filter_only_valid_prices()

    def annotate_market_data(self) -> QuerySet:
        return self.get_queryset().annotate_market_data()

    def annotate_base_data(self) -> QuerySet:
        return self.get_queryset().annotate_base_data()

    def annotate_security_data(self) -> QuerySet:
        return self.get_queryset().annotate_security_data()

    def annotate_all(self) -> QuerySet:
        return self.get_queryset().annotate_all()


class AnnotatedInstrumentPriceManager(InstrumentPriceManager):
    def get_queryset(self):
        return super().get_queryset().annotate_market_data().annotate_base_data().annotate_security_data()


class InstrumentPrice(
    ImportMixin,
    InstrumentPriceComputedMixin,
    DynamicModel,
    WBModel,
):
    import_export_handler_class = InstrumentPriceImportHandler
    # Base fields
    instrument = models.ForeignKey(
        to="wbfdm.Instrument",
        related_name="prices",
        on_delete=models.PROTECT,
        limit_choices_to=models.Q(children__isnull=True),
        verbose_name="Instrument",
        blank=True,
        null=True,
    )
    date = models.DateField(verbose_name="Date")
    calculated = models.BooleanField(default=False, verbose_name="Is Calculated")

    net_value = models.DecimalField(max_digits=16, decimal_places=6, verbose_name="Value (Net)")
    gross_value = DynamicDecimalField(
        max_digits=16,
        decimal_places=6,
        verbose_name="Value (Gross)",
    )  # TODO: I think we need to remove this field that is not really used here.

    outstanding_shares = models.DecimalField(
        decimal_places=4,
        max_digits=16,
        blank=True,
        null=True,
        verbose_name="Outstanding Shares",
        help_text="The amount of outstanding share for this instrument",
    )
    outstanding_shares_consolidated = DynamicDecimalField(
        decimal_places=4,
        max_digits=16,
        verbose_name="Outstanding Shares (Consolidated)",
        help_text="The amount of outstanding share for this instrument",
    )
    ########################################################
    #                   ASSET STATISTICS                   #
    ########################################################

    volume = models.FloatField(
        default=0.0,
        verbose_name="Volume",
        help_text="The Volume of the Asset on the price date of the Asset.",
    )

    volume_50d = DynamicFloatField(
        verbose_name="Average Volume (50 Days)",
        help_text="The Average Volume of the Asset over the last 50 days from the price date of the Asset.",
    )

    volume_200d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Average Volume (200 Days)",
        help_text="The Average Volume of the Asset over the last 200 days from the price date of the Asset.",
    )
    market_capitalization = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Market Capitalization",
        help_text="The Market Capitalization of the Asset the price date of the Asset.",
    )
    market_capitalization_consolidated = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Market Capitalization (Consolidated)",
        help_text="the consolidated market value of a company in local currency.",
    )

    currency_fx_rate_to_usd = models.ForeignKey(
        to="currency.CurrencyFXRates",
        related_name="instrument_prices",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Instrument Currency Rate",
        help_text="Rate to between instrument currency and USD",
    )

    # Statistics
    lock_statistics = models.BooleanField(
        default=False,
        help_text="If True, a save will not override the beta, correlation and sharpe ratio",
    )
    sharpe_ratio = models.FloatField(blank=True, null=True, verbose_name="Sharpe Ratio")
    correlation = models.FloatField(blank=True, null=True, verbose_name="Correlation")
    beta = models.FloatField(blank=True, null=True, verbose_name="Beta")
    annualized_daily_volatility = models.FloatField(blank=True, null=True, verbose_name="Annualized Volatility")

    created = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    modified = models.DateTimeField(
        verbose_name="Modified",
        auto_now=True,
    )
    # custom_beta_180d = DynamicFloatField(verbose_name="Custom Beta (180 days)")
    # custom_beta_1y = DynamicFloatField(verbose_name="Custom Beta (1 Years)")
    # custom_beta_2y = DynamicFloatField(verbose_name="Custom Beta (2 Years)")
    # custom_beta_3y = DynamicFloatField(verbose_name="Custom Beta (3 Years)")
    # custom_beta_5y = DynamicFloatField(verbose_name="Custom Beta (4 Years)")
    #
    # # Performances fields
    # performance_1d = DynamicDecimalField(
    #     verbose_name="Performance 1D", help_text="Performance 1D", max_digits=16, decimal_places=6
    # )
    # performance_7d = DynamicDecimalField(
    #     verbose_name="Performance (1W)", help_text="Performance 7 days rolling", max_digits=16, decimal_places=6
    # )
    # performance_30d = DynamicDecimalField(
    #     verbose_name="Performance (1M)", help_text="Performance 30 days rolling", max_digits=16, decimal_places=6
    # )
    # performance_90d = DynamicDecimalField(
    #     verbose_name="Performance (1Q)", help_text="Performance 90 days rolling", max_digits=16, decimal_places=6
    # )
    # performance_365d = DynamicDecimalField(
    #     verbose_name="Performance (1Y)", help_text="Performance 365 days rolling", max_digits=16, decimal_places=6
    # )
    # performance_ytd = DynamicDecimalField(
    #     verbose_name="Performance (YTD)", help_text="Performance Year-to-date", max_digits=16, decimal_places=6
    # )
    # performance_inception = DynamicDecimalField(
    #     verbose_name="Performance (Inception)",
    #     help_text="Performance since inception",
    #     max_digits=16,
    #     decimal_places=6,
    # )

    objects = InstrumentPriceManager()
    annotated_objects = InstrumentPriceManager(with_annotation=True)

    class Meta:
        verbose_name = "Instrument Price"
        verbose_name_plural = "Instrument Prices"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(date__week_day__in=[1, 7]),
                name="%(app_label)s_%(class)s_weekday_constraint",
            ),
            models.UniqueConstraint(fields=["instrument", "date", "calculated"], name="unique_price"),
        ]
        indexes = [
            models.Index(
                name="fdm_instrumentprice_base_idx",
                fields=["calculated", "date", "instrument"],
            ),
            models.Index(
                name="fdm_instrumentprice_idx1",
                fields=["calculated", "instrument"],
            ),
            models.Index(
                name="fdm_instrumentprice_idx2",
                fields=["instrument"],
            ),
        ]

    @property
    def _net_value_usd(self):
        if self.currency_fx_rate_to_usd:
            return getattr(self, "net_value_usd", self.net_value * self.currency_fx_rate_to_usd.value)

    def save(self, *args, **kwargs):
        if not self.currency_fx_rate_to_usd:
            with suppress(CurrencyFXRates.DoesNotExist):
                self.currency_fx_rate_to_usd = CurrencyFXRates.objects.get(
                    date=self.date, currency=self.instrument.currency
                )

        if self.market_capitalization_consolidated is None:
            self.market_capitalization_consolidated = self.market_capitalization

        # if the instrument is of type cash, we enforce the net value to 1
        if self.instrument.is_cash or self.instrument.is_cash_equivalent:
            self.net_value = Decimal("1")
            self.gross_value = Decimal("1")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.instrument.name}: {self.net_value} {self.date:%d.%m.%Y}"

    @property
    def previous_price(self):
        """Returns the previous instrument prices if one exists or None

        Returns:
            instrument.InstrumentPrice | None -- Previous InstrumentPrice
        """
        try:
            return InstrumentPrice.objects.filter(
                instrument=self.instrument, date__lt=self.date, calculated=self.calculated
            ).latest("date")
        except InstrumentPrice.DoesNotExist:
            return None

    @property
    def next_price(self):
        """Returns the next instrument prices if one exists or None

        Returns:
            instrument.InstrumentPrice | None -- Next InstrumentPrice
        """
        try:
            return self.instrument.prices.filter(date__gt=self.date, calculated=self.calculated).earliest("date")
        except InstrumentPrice.DoesNotExist:
            return None

    @property
    def shares(self):
        """Returns the number of shares of a instrument

        The number of shares are the sum of all customer trades

        Returns:
            int -- Shares
        """
        return self.instrument.total_shares(self.date)

    @property
    def valid_outstanding_shares(self):
        prices = self.instrument.prices.filter(date=self.date, outstanding_shares__isnull=False).order_by("calculated")
        return prices.last().outstanding_shares if prices.exists() else self.shares

    @property
    def nominal_value(self):
        """Returns the nominal value of a instrument

        The nominal value is the number of current shares multiplied by the share price of a instrument

        Returns:
            int -- Nominal Value
        """
        return self.instrument.nominal_value(self.date)

    def fill_market_capitalization(self):
        if self.market_capitalization is None:
            with suppress(InstrumentPrice.DoesNotExist):
                self.market_capitalization = (
                    self.instrument.valuations.filter(date__lt=self.date, market_capitalization__isnull=False)
                    .latest("date")
                    .market_capitalization
                )

    def compute_and_update_statistics(self, min_period: int = 20):
        df = (
            pd.DataFrame(
                InstrumentPrice.objects.filter_only_valid_prices()
                .filter(instrument=self.instrument, date__lte=self.date)
                .values_list("date", "net_value", "volume"),
                columns=["date", "net_value", "volume"],
            )
            .set_index("date")
            .sort_index()
        )
        prices_df = df["net_value"]
        if not prices_df.empty and prices_df.shape[0] >= min_period:
            financial_statistics = FinancialStatistics(prices_df)
            min_date = prices_df.index.min()
            if risk_free_rate := self.instrument.primary_risk_instrument:
                risk_free_rate_df = (
                    pd.DataFrame(
                        risk_free_rate.valuations.filter(date__gte=min_date, date__lte=self.date).values_list(
                            "date", "net_value"
                        ),
                        columns=["date", "net_value"],
                    )
                    .set_index("date")
                    .sort_index()["net_value"]
                )
                if sharpe_ratio := financial_statistics.get_sharpe_ratio(risk_free_rate_df):
                    self.sharpe_ratio = sharpe_ratio
            if benchmark := self.instrument.primary_benchmark:
                benchmark_df = (
                    pd.DataFrame(
                        benchmark.valuations.filter(date__gte=min_date, date__lte=self.date).values_list(
                            "date", "net_value"
                        ),
                        columns=["date", "net_value"],
                    )
                    .set_index("date")
                    .sort_index()["net_value"]
                )
                if (beta := financial_statistics.get_beta(benchmark_df)) is not None:
                    self.beta = beta
                if (correlation := financial_statistics.get_correlation(benchmark_df)) is not None:
                    self.correlation = correlation

            self.annualized_daily_volatility = financial_statistics.get_annualized_daily_volatility()
        if not (volume_df := df["volume"]).empty:
            self.volume_50d = volume_df.tail(50).mean()
            self.volume_200d = volume_df.tail(200).mean()

    @classmethod
    def subquery_closest_value(
        cls,
        field_name,
        val_date=None,
        date_name="date",
        instrument_pk_name="instrument__pk",
        date_lookup="lte",
        order_by="-date",
        calculated_filter_value=False,
    ):
        index_filter_params = {}
        if calculated_filter_value is not None:
            index_filter_params["calculated"] = calculated_filter_value
        if not val_date and date_name:
            index_filter_params[f"date__{date_lookup}"] = models.OuterRef(date_name)
        elif val_date:
            index_filter_params[f"date__{date_lookup}"] = val_date
        index_filter_params["instrument"] = models.OuterRef(instrument_pk_name)
        qs = cls.objects.filter(**index_filter_params).filter(**{f"{field_name}__isnull": False})
        return models.Subquery(qs.order_by(order_by).values(field_name)[:1])

    @classmethod
    def annotate_sum_shares(cls, queryset, val_date, date_key="date"):
        """
        Efficient way to annotate sum of shares without destroying indexing
        """
        return queryset.annotate(
            sum_shares_calculated=InstrumentPrice.subquery_closest_value(
                "outstanding_shares",
                date_name=date_key,
                instrument_pk_name="pk",
                date_lookup="lte",
                order_by="-date",
                calculated_filter_value=True,
            ),  # We get the last price whose outstanding_shares is not none and date below date_key
            sum_shares_real=InstrumentPrice.subquery_closest_value(
                "outstanding_shares",
                val_date=val_date,
                date_name=date_key,
                instrument_pk_name="pk",
                date_lookup="exact",
                calculated_filter_value=False,
            ),
            sum_shares=Case(
                When(sum_shares_real__isnull=False, then=F("sum_shares_real")),
                When(sum_shares_calculated__isnull=False, then=F("sum_shares_calculated")),
                default=Value(Decimal(0)),
                output_field=DecimalField(),
            ),
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbfdm:price"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{instrument} {{date}}"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbfdm:price-list"


@receiver(post_save, sender="currency.CurrencyFXRates")
def rate_creation(sender, instance, created, raw, **kwargs):
    if not raw and created:
        transaction.on_commit(lambda: update_currency_fx_rate_from_created_rate.delay(instance.id))


@receiver(pre_merge, sender="wbfdm.Instrument")
def pre_merge_instrument(sender: models.Model, merged_object, main_object, **kwargs):
    """
    Simply reassign the prices of the merged instrument to the main instrument if they don't already exist for that day, otherwise simply delete them
    """
    merged_object.prices.annotate(
        already_exists=Exists(
            InstrumentPrice.objects.filter(
                calculated=OuterRef("calculated"), instrument=main_object, date=OuterRef("date")
            )
        )
    ).filter(already_exists=True).delete()
    merged_object.prices.update(instrument=main_object)


@shared_task(queue="portfolio")
def update_currency_fx_rate_from_created_rate(rate_id):
    currency_rate = CurrencyFXRates.objects.get(id=rate_id)
    for price in InstrumentPrice.objects.filter(
        instrument__currency=currency_rate.currency, date=currency_rate.date, currency_fx_rate_to_usd__isnull=True
    ):
        price.currency_fx_rate_to_usd = currency_rate
        price.save()
