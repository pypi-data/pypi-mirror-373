from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from rest_framework.reverse import reverse
from wbcore.contrib.tags.models import TagModelMixin
from wbcore.models import WBModel
from wbcore.signals import pre_merge


class InstrumentClassificationRelatedInstrument(models.Model):
    class Type(models.TextChoices):
        PARTNER = "PARTNER", "Partner"
        SUPPLIER = "SUPPLIER", "Supplier"
        PEER = "PEER", "Peer"
        COMPETITOR = "COMPETITOR", "Competitor"
        BIGGEST_THREAT = "BIGGEST_THREAT", "Biggest Threat"
        CUSTOMER = "CUSTOMER", "Customer"

    related_instrument_type = models.CharField(max_length=16, choices=Type.choices, null=True, blank=True)
    classified_instrument = models.ForeignKey(
        to="wbfdm.InstrumentClassificationThroughModel",
        related_name="classification_instrument_relationships",
        on_delete=models.CASCADE,
    )
    related_instrument = models.ForeignKey(
        to="wbfdm.Instrument",
        limit_choices_to=(models.Q(instrument_type__is_classifiable=True) & models.Q(level=0)),
        related_name="instrument_classification_related",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.classified_instrument} {self.related_instrument}"


class InstrumentClassificationThroughModel(TagModelMixin, models.Model):
    instrument = models.ForeignKey(
        "wbfdm.Instrument",
        on_delete=models.CASCADE,
        related_name="classifications_through",
        limit_choices_to=(models.Q(instrument_type__is_classifiable=True) & models.Q(level=0)),
    )
    classification = models.ForeignKey(
        "wbfdm.Classification",
        on_delete=models.CASCADE,
        related_name="instruments_through",
    )
    is_favorite = models.BooleanField(default=False)
    reason = models.TextField(default="", blank=True, verbose_name="Reason for the choice")
    pure_player = models.BooleanField(default=False, help_text="Pure Players Companies", verbose_name="Pure Player")
    top_player = models.BooleanField(default=False, help_text="Top Players Companies", verbose_name="Top Player")
    percent_of_revenue = models.DecimalField(
        decimal_places=4,
        max_digits=5,
        null=True,
        blank=True,
        verbose_name="% of revenue",
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    related_instruments = models.ManyToManyField(
        to="wbfdm.Instrument",
        limit_choices_to=(models.Q(instrument_type__is_classifiable=True) & models.Q(level=0)),
        through=InstrumentClassificationRelatedInstrument,
        through_fields=("classified_instrument", "related_instrument"),
        blank=True,
    )

    def get_tag_detail_endpoint(self):
        return reverse("wbfdm:classifiedinstrument-detail", [self.id])

    def get_tag_representation(self):
        return f"{self.instrument} - {self.classification}"

    class Meta:
        constraints = [
            models.UniqueConstraint(name="unique_classifiedinstruments", fields=["instrument", "classification"])
        ]

    def __str__(self) -> str:
        return f"{self.instrument} {self.classification}"

    def save(self, *args, **kwargs):
        if self.pure_player and not self.percent_of_revenue:
            self.percent_of_revenue = 1
        return super().save(*args, **kwargs)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbfdm:instrumentclassificationrelationship"


class InstrumentFavoriteGroup(WBModel):
    name = models.CharField(max_length=256)
    instruments = models.ManyToManyField(
        "wbfdm.Instrument",
        related_name="favorite_groups",
        blank=True,
        verbose_name="Favorite Instruments Group",
        limit_choices_to=models.Q(children__isnull=True),
    )
    owner = models.ForeignKey(
        "directory.Person", on_delete=models.CASCADE, blank=True, null=True, related_name="favorite_instruments_groups"
    )
    public = models.BooleanField(default=False, help_text="If set to True, this group will be available to everyone.")
    primary = models.BooleanField(
        default=False,
        help_text="If set to True, this group will be set as default filter for instrument based viewset (Only one primary group allowed).",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.primary:
            InstrumentFavoriteGroup.objects.filter(owner=self.owner, primary=True).exclude(id=self.id).update(
                primary=False
            )
        return super().save(*args, **kwargs)

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbfdm:favoritegroup-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}} - (Public: {{public}})"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbfdm:favoritegroup"


class RelatedInstrumentThroughModel(models.Model):
    class RelatedTypeChoices(models.TextChoices):
        BENCHMARK = "BENCHMARK", "Benchmark"
        PEER = "PEER", "Peer"
        RISK_INSTRUMENT = "RISK_INSTRUMENT", "Risk Instrument"
        TRACKER = "TRACKER", "Tracker"

    instrument = models.ForeignKey(
        "wbfdm.Instrument",
        on_delete=models.CASCADE,
        related_name="related_instruments_through",
        limit_choices_to=models.Q(children__isnull=True),
    )
    related_instrument = models.ForeignKey(
        "wbfdm.Instrument",
        on_delete=models.CASCADE,
        related_name="dependent_instruments_through",
        limit_choices_to=models.Q(children__isnull=True),
    )
    is_primary = models.BooleanField(default=False)
    related_type = models.CharField(
        max_length=32, default=RelatedTypeChoices.BENCHMARK, choices=RelatedTypeChoices.choices
    )

    class Meta:
        unique_together = ("instrument", "related_instrument", "is_primary", "related_type")

    def save(self, *args, **kwargs):
        qs = RelatedInstrumentThroughModel.objects.filter(
            instrument=self.instrument, related_type=self.related_type, is_primary=True
        ).exclude(id=self.id)
        if self.is_primary:
            qs.update(is_primary=False)
        elif not qs.exists():
            self.is_primary = True
        return super().save(*args, **kwargs)


@receiver(m2m_changed, sender="wbfdm.RelatedInstrumentThroughModel")
def add_related_instrument(sender, instance, action, pk_set, **kwargs):
    if action == "post_add" and pk_set:
        for related_instrument_id in pk_set:
            through = RelatedInstrumentThroughModel.objects.filter(
                instrument=instance.id, related_instrument=related_instrument_id
            ).first()
            through.save()
    if action == "post_remove" and pk_set:
        qs = RelatedInstrumentThroughModel.objects.filter(instrument=instance, related_type=instance.related_type)
        if not qs.filter(is_primary=True).exists():
            instance = qs.first()
            instance.is_primary = True
            instance.save()


@receiver(m2m_changed, sender="wbfdm.InstrumentClassificationThroughModel")
def add_classification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add" and pk_set:
        for classification_id in pk_set:
            if through := InstrumentClassificationThroughModel.objects.filter(
                instrument=instance.id, classification=classification_id
            ).first():
                through.save()


@receiver(pre_merge, sender="wbfdm.Instrument")
def pre_merge_instrument(sender: models.Model, merged_object, main_object, **kwargs):
    """
    Reassign all merged instrument preferred classification relationship to the main instrument
    """
    # For every favorite group where the merged instrument is present, we remove it and assign the main instrument instad
    for favorite_group in InstrumentFavoriteGroup.objects.filter(instruments=merged_object):
        favorite_group.instruments.remove(merged_object)
        favorite_group.instruments.add(main_object)

    # For all related instruments relationship of the merged instrument, we reassign them to the main instrument if they don't exist yet. The relationship is then deleted.
    for through in RelatedInstrumentThroughModel.objects.filter(instrument=merged_object):
        RelatedInstrumentThroughModel.objects.get_or_create(
            instrument=main_object,
            related_instrument=through.related_instrument,
            is_primary=through.is_primary,
            related_type=through.related_type,
        )
        through.delete()
    # We also reassign the reverse related instrument relationship where the merged instrument is the related instrument.
    for through in RelatedInstrumentThroughModel.objects.filter(related_instrument=merged_object):
        RelatedInstrumentThroughModel.objects.get_or_create(
            instrument=through.instrument,
            related_instrument=main_object,
            is_primary=through.is_primary,
            related_type=through.related_type,
        )
        through.delete()

    # For all classification relationships of the merged instrument, we reassign them to the main instrument if they don't exist yet. The relationship is then deleted.
    for through in InstrumentClassificationThroughModel.objects.filter(instrument=merged_object):
        new_rel, created = InstrumentClassificationThroughModel.objects.get_or_create(
            instrument=main_object,
            classification=through.classification,
            defaults={
                "is_favorite": through.is_favorite,
                "reason": through.reason,
                "pure_player": through.pure_player,
                "top_player": through.top_player,
                "percent_of_revenue": through.percent_of_revenue,
            },
        )
        for related_instrument in through.related_instruments.all():
            if related_instrument not in new_rel.related_instruments.all():
                new_rel.related_instruments.add(related_instrument)
        through.delete()

    # We also reassign the reverse classification relationship where the merged instrument is the related instrument.
    for through in InstrumentClassificationThroughModel.objects.filter(related_instruments=merged_object):
        through.related_instruments.remove(merged_object)
        through.related_instruments.add(main_object)
