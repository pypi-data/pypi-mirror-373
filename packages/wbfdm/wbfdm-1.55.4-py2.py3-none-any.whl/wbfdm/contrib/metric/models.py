from datetime import date as date_lib
from typing import Self, Type

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast, NullIf
from wbcore.models import WBModel

from .backends.base import AbstractBackend
from .dto import Metric, MetricKey
from .registry import backend_registry


class InstrumentMetric(models.Model):
    basket_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="instrument_metrics")
    basket_id = models.PositiveIntegerField()
    basket_repr = models.CharField(max_length=256)

    basket = GenericForeignKey("basket_content_type", "basket_id")

    instrument = models.ForeignKey(
        "wbfdm.Instrument",
        on_delete=models.CASCADE,
        related_name="metrics",
        null=True,
        blank=True,
        help_text="Instrument where this metric belongs to. If null, the metric is applicable to all instruments related to the basket",
    )
    date = models.DateField(
        verbose_name="Metric Date", null=True, blank=True, help_text="If date is null, the metric is considered static"
    )
    key = models.CharField(max_length=255, verbose_name="Metric Key")
    metrics = models.JSONField(default=dict, verbose_name="Metrics", encoder=DjangoJSONEncoder)

    parent_metric = models.ForeignKey(
        "self",
        related_name="dependent_metrics",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Parent Metric",
    )

    def save(self, *args, **kwargs):
        self.basket_repr = str(self.basket)
        super().save(*args, **kwargs)

    @classmethod
    def update_or_create_from_metric(cls, metric: Metric, parent_instrument_metric: Self | None = None):
        """
        Update or create an InstrumentMetric instance based on a given Metric DTO object.

        Args:
            metric (Metric): The DTO to base the creation or update on.
            parent_instrument_metric (Optional[InstrumentMetric]): The parent of the created/updated InstrumentMetric instance, if any. Defaults to None.

        Returns:
            None

        Side Effects:
            - Creates or updates an InstrumentMetric instance in the database.
            - Recursively creates or updates dependent InstrumentMetric instances.
        """
        base_metric, _ = InstrumentMetric.objects.update_or_create(
            basket_id=metric.basket_id,
            basket_content_type_id=metric.basket_content_type_id,
            instrument_id=metric.instrument_id,
            date=metric.date,
            key=metric.key,
            defaults={
                "metrics": metric.metrics,
                "parent_metric": parent_instrument_metric,
            },
        )
        for dependency_metric in metric.dependency_metrics:
            cls.update_or_create_from_metric(dependency_metric, parent_instrument_metric=base_metric)

    @classmethod
    def annotate_with_metrics(
        cls,
        queryset: models.QuerySet,
        metric_key: MetricKey,
        metric_basket_class: Type[WBModel],
        val_date: date_lib | None = None,
        basket_label: str = "id",
        instrument_label: str | None = None,
    ) -> models.QuerySet:
        """
        Annotate metrics to a queryset related to the given metric key and basket class.

        Args:
            queryset (models.QuerySet): The queryset to be annotated.
            metric_key (MetricKey): The metric key or MetricKey instance to use for annotation.
            metric_basket_class (Type[WBModel]): The basket class associated with the metric.
            val_date (date, optional): The date for the metrics. Defaults to None.
            basket_label (str, optional): The label to identify the basket in the subquery queryset. Defaults to "id".
            instrument_label (Union[str, None], optional): The label to identify the instrument in the subquery queryset, if any. Defaults to None.

        Returns:
            models.QuerySet: The annotated queryset with the metrics included. (with field keys as returned by MetricField.get_fields)

        Side Effects:
            - Annotates the given queryset with subqueries for the specified metrics.
        """

        backend_class: AbstractBackend = backend_registry[metric_key, metric_basket_class]

        content_type = ContentType.objects.get_for_model(backend_class.BASKET_MODEL_CLASS)
        subquery = InstrumentMetric.objects.filter(
            basket_content_type=content_type,
            basket_id=models.OuterRef(basket_label),
            key=metric_key.key,
            date=val_date,
        )
        if instrument_label:
            subquery = subquery.filter(instrument=models.OuterRef(instrument_label))
        queryset = queryset.annotate(
            **{
                k: models.Subquery(
                    subquery.annotate(
                        casted_metric=Cast(
                            NullIf(models.F("metrics__" + v), models.Value("null")),
                            output_field=models.FloatField(),
                        )
                    ).values("casted_metric")[:1]
                )
                for k, v in metric_key.subfields_filter_map.items()
            }
        )

        # annotate extra subfields
        queryset = queryset.annotate(
            **{
                f"{metric_key.key}_{extra_subfield.key}": models.Subquery(
                    subquery.annotate(
                        casted_metric=Cast(
                            KeyTextTransform(extra_subfield.key, "metrics"), output_field=extra_subfield.field_type()
                        ),
                    ).values("casted_metric")[:1]
                )
                for extra_subfield in metric_key.extra_subfields
            }
        )

        return queryset

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "metric:instrumentmetric"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "metric:instrumentmetricrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{key}} - {{date}} - {{basket_repr}}"

    class Meta:
        verbose_name = "Instrument Metric"
        verbose_name_plural = "Instrument Metrics"
        constraints = [
            models.UniqueConstraint(
                name="unique_instrument_metric",
                fields=["basket_content_type", "basket_id", "instrument", "date", "key"],
                nulls_distinct=False,
            )
        ]
        indexes = [
            models.Index(
                fields=["basket_content_type", "basket_id", "key", "date"],
            )
        ]
