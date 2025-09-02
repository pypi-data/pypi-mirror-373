from typing import Any, Self

from django.db import models

from wbfdm.enums import (
    ESGControveryFlag,
    ESGControverySeverity,
    ESGControveryStatus,
    ESGControveryType,
)
from wbfdm.models.instruments.instruments import Instrument


class Controversy(models.Model):
    external_id = models.CharField(max_length=512, unique=True)
    instrument = models.ForeignKey("wbfdm.Instrument", on_delete=models.CASCADE, limit_choices_to=models.Q(level=0))
    headline = models.TextField(verbose_name="Headline")
    description = models.TextField(verbose_name="Description")
    source = models.TextField(
        verbose_name="Source", null=True, blank=True
    )  # Source is usually a sentence but can be a whole text
    status = models.CharField(
        max_length=64,
        choices=ESGControveryStatus.choices,
        verbose_name="Status",
        default=ESGControveryStatus.ONGOING.value,
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=64,
        choices=ESGControveryType.choices,
        verbose_name="Type",
        default=ESGControveryType.STRUCTURAL.value,
        null=True,
        blank=True,
    )
    severity = models.CharField(
        max_length=64,
        choices=ESGControverySeverity.choices,
        verbose_name="Severity",
        default=ESGControverySeverity.MINOR.value,
        null=True,
        blank=True,
    )
    flag = models.CharField(
        max_length=64,
        choices=ESGControveryFlag.choices,
        verbose_name="Flag",
        default=ESGControveryFlag.GREEN.value,
        null=True,
        blank=True,
    )
    direct_involvement = models.BooleanField(default=True, verbose_name="Direct Involvement")
    company_response = models.CharField(max_length=512, null=True, blank=True)

    review = models.DateField(verbose_name="Reviewed")
    initiated = models.DateField(verbose_name="initiated", null=True, blank=True)

    @classmethod
    def sync_from_dataloader(cls, controversy: dict[str, Any]) -> Self:
        instrument = Instrument.objects.get(
            pk=controversy["instrument_id"]
        ).get_root()  # we link it only to root level

        return cls.objects.update_or_create(
            external_id=controversy["id"],
            defaults={
                "instrument": instrument,
                "headline": controversy["headline"],
                "description": controversy["narrative"],
                "source": controversy["source"],
                "direct_involvement": controversy.get("direct_involvement", True),
                "company_response": controversy["response"],
                "review": controversy["review"],
                "initiated": controversy["initiated"],
                "flag": controversy["flag"],
                "status": controversy["status"],
                "type": controversy["type"],
                "severity": controversy["assessment"],
            },
        )[0]
