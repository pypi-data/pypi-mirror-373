from django.db import models
from wbcore.contrib.io.mixins import ImportMixin

from wbfdm.import_export.handlers.option import (
    OptionAggregateImportHandler,
    OptionImportHandler,
)


class BaseOptionAbstractModel(ImportMixin, models.Model):
    class Type(models.TextChoices):
        PUT = "PUT", "Put"
        CALL = "CALL", "Call"

    type = models.CharField(choices=Type.choices, max_length=6)
    date = models.DateField()
    instrument = models.ForeignKey(
        to="wbfdm.Instrument",
        related_name="%(class)s",
        on_delete=models.PROTECT,
        limit_choices_to=models.Q(children__isnull=True),
        verbose_name="Instrument",
    )

    # Option Metrics

    volume = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volume",
        help_text="Option Volume",
    )

    volume_5d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volume 5D",
        help_text="Option Volume (5D)",
    )

    volume_10d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volume 10D",
        help_text="Option Volume (10D)",
    )

    volume_20d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volume 20D",
        help_text="Option Volume (20D)",
    )

    volume_50d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volume 50D",
        help_text="Option Volume (50D)",
    )

    open_interest = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Open Interest",
        help_text="Open Interest",
    )
    open_interest_5d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Open Interest 5D",
        help_text="Option Open Interest (5D)",
    )
    open_interest_10d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Open Interest 10D",
        help_text="Option Open Interest (10D)",
    )
    open_interest_20d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Open Interest 20D",
        help_text="Option Open Interest (20D)",
    )
    open_interest_50d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Open Interest 50D",
        help_text="Option Open Interest (50D)",
    )

    volatility = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volatility",
    )

    volatility_30d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volatility (30D)",
    )

    volatility_60d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volatility (60D)",
    )

    volatility_90d = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Volatility (90D)",
    )

    class Meta:
        abstract = True


class OptionAggregate(BaseOptionAbstractModel):
    import_export_handler_class = OptionAggregateImportHandler

    class Meta:
        verbose_name = "Option Aggregate"
        verbose_name_plural = "Options Aggregates"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(date__week_day__in=[1, 7]),
                name="%(app_label)s_%(class)s_weekday_constraint",
            ),
            models.UniqueConstraint(fields=["instrument", "date", "type"], name="unique_option_aggregate"),
        ]
        indexes = [
            models.Index(
                fields=["instrument", "date", "type"],
            ),
            models.Index(
                fields=["instrument", "date"],
            ),
            models.Index(
                fields=["type"],
            ),
        ]


class Option(BaseOptionAbstractModel):
    import_export_handler_class = OptionImportHandler

    contract_identifier = models.CharField(verbose_name="Contract Name", max_length=255)
    strike = models.FloatField(verbose_name="Strike")
    expiration_date = models.DateField(verbose_name="Expiration Date")

    # EOD data
    open = models.FloatField(null=True, blank=True, verbose_name="Open")
    high = models.FloatField(null=True, blank=True, verbose_name="High")
    low = models.FloatField(null=True, blank=True, verbose_name="Low")
    close = models.FloatField(null=True, blank=True, verbose_name="Close")
    bid = models.FloatField(null=True, blank=True, verbose_name="Bid")
    ask = models.FloatField(null=True, blank=True, verbose_name="Ask")
    vwap = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Open Interest",
        help_text="Open Interest",
    )

    # Option risk metrics:

    risk_delta = models.FloatField(
        null=True, blank=True, verbose_name="Delta", help_text='Option risk metrics "Delta"'
    )
    risk_theta = models.FloatField(
        null=True, blank=True, verbose_name="Theta", help_text='Option risk metrics "Theta"'
    )
    risk_gamma = models.FloatField(
        null=True, blank=True, verbose_name="Gamma", help_text='Option risk metrics "Gamma"'
    )
    risk_vega = models.FloatField(null=True, blank=True, verbose_name="Vega", help_text='Option risk metrics "Vega"')
    risk_rho = models.FloatField(null=True, blank=True, verbose_name="Rho", help_text='Option risk metrics "Rho"')
    risk_lambda = models.FloatField(
        null=True, blank=True, verbose_name="Lambda", help_text='Option risk metrics "Lambda"'
    )
    risk_epsilon = models.FloatField(
        null=True, blank=True, verbose_name="Epsilon", help_text='Option risk metrics "Epsilon"'
    )
    risk_vomma = models.FloatField(
        null=True, blank=True, verbose_name="Vomma", help_text='Option risk metrics "Vomma"'
    )
    risk_vera = models.FloatField(null=True, blank=True, verbose_name="Vera", help_text='Option risk metrics "Vera"')
    risk_speed = models.FloatField(
        null=True, blank=True, verbose_name="Speed", help_text='Option risk metrics "Speed"'
    )
    risk_zomma = models.FloatField(
        null=True, blank=True, verbose_name="Zomma", help_text='Option risk metrics "Zomma"'
    )
    risk_color = models.FloatField(
        null=True, blank=True, verbose_name="Color", help_text='Option risk metrics "Color"'
    )
    risk_ultima = models.FloatField(
        null=True, blank=True, verbose_name="Ultima", help_text='Option risk metrics "Ultima"'
    )

    class Meta:
        verbose_name = "Option"
        verbose_name_plural = "Options"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(date__week_day__in=[1, 7]),
                name="%(app_label)s_%(class)s_weekday_constraint",
            ),
            models.UniqueConstraint(
                fields=["instrument", "contract_identifier", "date", "type"], name="unique_option"
            ),
        ]
        indexes = [
            models.Index(
                fields=["instrument", "date", "type"],
            ),
            models.Index(
                fields=["instrument", "date"],
            ),
            models.Index(
                fields=["type"],
            ),
        ]
