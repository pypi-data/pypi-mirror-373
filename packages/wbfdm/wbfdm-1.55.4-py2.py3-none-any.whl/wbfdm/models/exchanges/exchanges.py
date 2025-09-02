from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from wbcore.models import WBModel


class ExchangeManager(models.Manager):
    def get_by_bbg(self, bbg):
        """
        If passed in a bbg ticker, we don't know whether it is a normal exchange code or a composite code.
        Therefore we return either the exchange where this code is the bbg_exchange_codes, or the exchange where this composite code
        exists, but only if it is the primary exchange
        """
        return self.get(Q(bbg_exchange_codes__contains=[bbg]) | (Q(bbg_composite=bbg) & Q(bbg_composite_primary=True)))


class Exchange(WBModel):
    source_id = models.CharField(max_length=64, null=True, blank=True)
    source = models.CharField(max_length=64, null=True, blank=True)
    name = models.CharField(
        max_length=265, null=True, blank=True, verbose_name="Exchange Name", help_text="Name of the Exchange."
    )

    opening_time = models.TimeField(
        blank=True, null=True, verbose_name="Exchange Opening time", help_text="The opening time of the exchange"
    )
    closing_time = models.TimeField(
        blank=True, null=True, verbose_name="Exchange Closing time", help_text="The closing time of the exchange"
    )

    mic_code = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name="MIC (ISO)",
        unique=True,
        help_text="Market Identifier Code.",
    )
    mic_name = models.CharField(
        max_length=126,
        null=True,
        blank=True,
        verbose_name="MIC (ISO) Name",
        help_text="Market Identifier Name.",
    )
    operating_mic_code = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name="Operating MIC Code",
        help_text="Operating Market Identifier Code.",
    )
    operating_mic_name = models.CharField(
        max_length=126,
        null=True,
        blank=True,
        verbose_name="Operating MIC Name",
        help_text="Operating Market Identifier Name.",
    )
    ########################################################
    #                       Bloomberg                      #
    ########################################################

    bbg_exchange_codes = ArrayField(
        models.CharField(
            max_length=4,
        ),
        blank=True,
        default=list,
        verbose_name="BBG Exchange Code",
        help_text="Bloomberg Exchange Code.",
    )

    bbg_composite_primary = models.BooleanField(
        default=False,
        verbose_name="BBG Primary composite",
        help_text="Indicates the primary exchange for this BBG Composite Code.",
    )

    bbg_composite = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name="BBG Composite Code",
        help_text="Bloomberg Composite Code.",
    )

    ########################################################
    #                   Reuters/Refinitiv                  #
    ########################################################

    refinitiv_identifier_code = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name="RIC Exchange Code",
        help_text="Reuters Exchange Code.",
    )
    refinitiv_mnemonic = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name="Refinitiv Mnemonic",
        help_text="Reuters Exchange Mnemonic Code.",
    )
    ########################################################
    #                      INFORMATION                     #
    ########################################################

    country = models.ForeignKey(
        to="geography.Geography",
        null=True,
        blank=True,
        limit_choices_to={"level": 1},
        on_delete=models.SET_NULL,
    )

    city = models.ForeignKey(
        to="geography.Geography",
        max_length=255,
        null=True,
        blank=True,
        limit_choices_to={"level": 3},
        related_name="city_exchanges",
        on_delete=models.SET_NULL,
        verbose_name="City",
        help_text="The city where this Exchange is located at.",
    )

    city = models.ForeignKey(
        "geography.Geography",
        null=True,
        blank=True,
        related_name="exchanges",
        verbose_name="City",
        on_delete=models.PROTECT,
        help_text="The city where this Exchange is located at.",
        limit_choices_to={"level": 3},
    )

    website = models.URLField(
        null=True,
        blank=True,
        verbose_name="Website",
        help_text="The Website of the Exchange",
    )

    comments = models.TextField(
        default="",
        blank=True,
        verbose_name="Comments",
        help_text="Any comments for this exchange",
    )
    apply_round_lot_size = models.BooleanField(
        default=True,
        verbose_name="Apply Round Lot Size",
        help_text="If False, the quotes linked to this instrument will ignore their round lot size (will be considered 1).",
    )
    last_updated = models.DateTimeField(auto_now=True)

    objects = ExchangeManager()

    @property
    def identifier_repr(self) -> str:
        if self.bbg_exchange_codes:
            return self.bbg_exchange_codes[0]
        if self.mic_code:
            return self.mic_code
        if self.operating_mic_code:
            return self.operating_mic_code
        if self.bbg_composite:
            return self.bbg_composite
        if self.refinitiv_identifier_code:
            return self.refinitiv_identifier_code
        if self.refinitiv_mnemonic:
            return self.refinitiv_mnemonic

    def __str__(self) -> str:
        repr = self.identifier_repr
        if self.name:
            repr = f"{self.name} - {self.identifier_repr}"
        elif self.mic_name:
            repr = f"{self.mic_name} - {self.identifier_repr}"
        return repr

    class Meta:
        verbose_name = _("Exchange")
        verbose_name_plural = _("Exchanges")
        indexes = [models.Index(fields=["source_id", "source"])]
        constraints = [
            models.UniqueConstraint(fields=["source", "source_id"], name="unique_exchange_source"),
        ]

    @classmethod
    def dict_to_model(cls, exchange_data):
        if isinstance(exchange_data, int):
            return Exchange.objects.filter(id=exchange_data).first()
        elif (bbg_code := exchange_data.get("bbg_exchange_codes", None)) or (
            bbg_code := exchange_data.get("bbg_exchange_code", None)
        ):
            return Exchange.objects.filter(bbg_exchange_codes__contains=[bbg_code]).first()
        elif mic_code := exchange_data.pop("exchange__mic_code", None):
            return Exchange.objects.filter(mic_code=mic_code).first()
        elif bbg_composite := exchange_data.pop("exchange__bbg_composite", None):
            return Exchange.objects.filter(bbg_composite=bbg_composite).first()

    @classmethod
    def get_endpoint_basename(cls):
        return "wbfdm:exchange"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbfdm:exchangerepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

    @property
    def time_zone(self):
        if self.city:
            return self.city.time_zone
