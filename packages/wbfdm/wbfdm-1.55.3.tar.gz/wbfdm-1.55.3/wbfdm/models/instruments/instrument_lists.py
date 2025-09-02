from django.db import models
from slugify import slugify
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.models import WBModel
from wbcore.utils.models import ComplexToStringMixin

from wbfdm.import_export.handlers.instrument_list import InstrumentListImportHandler
from wbfdm.models.instruments.instruments import Instrument


class InstrumentListThroughModel(ImportMixin, ComplexToStringMixin):
    import_export_handler_class = InstrumentListImportHandler
    """
    This model is not a Through model from a programming point of view, however it allows to link instrument list to
    instruments.
    """

    instrument_str = models.CharField(max_length=256)
    instrument = models.ForeignKey(
        to="wbfdm.Instrument",
        null=True,
        blank=True,
        limit_choices_to=models.Q(is_security=True),
        on_delete=models.SET_NULL,
    )
    instrument_list = models.ForeignKey(
        to="wbfdm.InstrumentList",
        on_delete=models.CASCADE,
    )

    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    comment = models.TextField(default="", blank=True)
    validated = models.BooleanField(default=False)

    def compute_str(self) -> str:
        """
        Method to compute the string representation of the instance. It will save the string value to the computed_str
        field.

        Returns:
            The string representation of the instance.
        """
        if self.instrument and self.instrument.name_repr:
            return f"{self.instrument.name_repr} - {self.instrument_list.name}"
        return f"{self.instrument_str} - {self.instrument_list.name}"

    class Meta:
        verbose_name = "Instrument in Instrument List"
        constraints = [
            models.UniqueConstraint(fields=["instrument", "instrument_list"], name="unique_instrument_per_list")
        ]

        notification_types = [
            create_notification_type(
                "wbfdm.instrument_list_add",
                "Instrument added to Instrument List",
                "A notification when an instrument gets added to a list.",
                True,
                True,
                True,
            ),
        ]


class InstrumentList(WBModel):
    class InstrumentListType(models.TextChoices):
        WATCH = "WATCH", "Watch List"
        EXCLUSION = "EXCLUSION", "Exclusion List"

    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255, unique=True, blank=True)
    instrument_list_type = models.CharField(max_length=32, choices=InstrumentListType.choices, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def instruments(self) -> models.QuerySet[Instrument]:
        """
        Returns a QuerySet of Instrument objects associated with the current instrument list.

        This property filters the Instrument objects based on the related InstrumentListThroughModel
        and returns only those Instruments where the foreign key is not null.

        Returns:
            models.QuerySet[Instrument]: A QuerySet of Instrument objects.
        """
        return Instrument.objects.filter(
            id__in=(
                InstrumentListThroughModel.objects.filter(instrument_list=self, instrument__isnull=False).values(
                    "instrument"
                )
            )
        )

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = slugify(f"{self.name}-{self.id}")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Instrument List"
        verbose_name_plural = "Instrument Lists"
        permissions = (("administrate_instrumentlist", "Can administrate Instrument List"),)

    @classmethod
    def get_endpoint_basename(cls):
        return "wbfdm:instrumentlist"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbfdm:instrumentlistrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"
