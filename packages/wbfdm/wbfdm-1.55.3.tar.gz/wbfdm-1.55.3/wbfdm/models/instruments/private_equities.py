from django.contrib.postgres.fields import ArrayField
from django.db import models
from wbcore.contrib.io.mixins import ImportMixin

from wbfdm.import_export.handlers.private_equities import DealImportHandler


class Deal(ImportMixin, models.Model):
    import_export_handler_class = DealImportHandler

    class Types(models.TextChoices):
        DEAL = "DEAL", "Deal"
        FUNDING = "FUNDING", "Funding"
        INVESTMENT = "INVESTMENT", "Investment"
        PORTFOLIO_EXIT = "PORTFOLIO_EXIT", "Portfolio Exit"

    type = models.CharField(
        default=Types.DEAL, choices=Types.choices, max_length=14, verbose_name="Type", help_text="The deal type"
    )
    external_id = models.CharField(max_length=64, blank=True, null=True)
    date = models.DateField()
    equity = models.ForeignKey(
        "wbfdm.Instrument",
        related_name="deals",
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(instrument_type__key="equity"),
    )
    transaction_amount = models.FloatField(help_text="Deal Size (in millions")
    investors = models.ManyToManyField(
        "wbfdm.Instrument",
        related_name="invested_deals",
        blank=True,
        verbose_name="Investors",
        help_text="Investors",
    )

    funding_round = models.CharField(max_length=128, verbose_name="Funding Round")
    funding_round_category = models.CharField(max_length=128, verbose_name="Funding Round Category")

    valuation = models.FloatField(
        verbose_name="Valuaton",
        blank=True,
        null=True,
        help_text="Valuation of the funded organization after this transaction (in Millions USD).",
    )
    valuation_estimated = models.BooleanField(
        default=False, verbose_name="Is valuation estimated", help_text="True if the valuation is an estimate"
    )
    valuation_source_type = models.CharField(
        max_length=24,
        blank=True,
        null=True,
        help_text="The source type of the valuation",
    )
    valuation_media_mention_source_urls = ArrayField(
        models.URLField(),
        blank=True,
        null=True,
        help_text="List of URLs used to source the valuation for the Media Mentions source type.",
    )
