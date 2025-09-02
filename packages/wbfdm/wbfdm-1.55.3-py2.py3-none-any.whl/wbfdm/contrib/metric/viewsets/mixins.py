from datetime import date
from typing import TYPE_CHECKING, Optional, Type

from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property
from wbcore import filters
from wbcore.metadata.metadata import WBCoreMetadata
from wbcore.utils.strings import get_aggregate_symbol

from wbfdm.contrib.metric.models import InstrumentMetric
from wbfdm.contrib.metric.registry import backend_registry
from wbfdm.contrib.metric.viewsets.configs.display import (
    InstrumentMetricPivotedListDisplayConfig,
)

from ..dto import MetricKey

if TYPE_CHECKING:
    from django.db.models import Model
    from wbcore.models import WBModel
    from wbcore.viewsets import ModelViewSet

    _Base = ModelViewSet
else:
    _Base = object


class InstrumentMetricMetaData(WBCoreMetadata):
    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)
        if "filter_fields" in metadata and view.METRIC_SHOW_FILTERS:
            view_metric_key_choices = backend_registry.get_choices(view.METRIC_KEYS)
            metric_show_filter_field = filters.BooleanFilter(
                default=view.METRIC_SHOW_BY_DEFAULT,
                field_name="metric_show_by_default",
                required=True,
                label="Show Metric Keys",
            )
            metric_show_by_default_rep, metric_show_by_default_lookup = metric_show_filter_field.get_representation(
                request, "metric_show_by_default", view
            )
            metadata["filter_fields"]["metric_show_by_default"] = metric_show_by_default_rep
            metadata["filter_fields"]["metric_show_by_default"]["lookup_expr"] = [metric_show_by_default_lookup]

            metric_keys_filter_field = filters.MultipleChoiceFilter(
                choices=view_metric_key_choices,
                field_name="metric_keys",
                required=True,
                label="Metric Keys",
                depends_on=[{"field": "metric_show_by_default", "options": {"activates_on": [True]}}],
                default=list(map(lambda x: x[0], view_metric_key_choices)),
            )
            metric_keys_rep, metric_keys_lookup = metric_keys_filter_field.get_representation(
                request, "metric_keys", view
            )
            metadata["filter_fields"]["metric_keys"] = metric_keys_rep
            metadata["filter_fields"]["metric_keys"]["lookup_expr"] = [metric_keys_lookup]

        return metadata


class InstrumentMetricMixin(_Base):
    """
    Mixin to register automatically a set of metrics defines in METRIC_KEYS into a particular view
    """

    METRIC_KEYS: tuple[MetricKey] | tuple[()] = ()  # The set of MetricKey to inject into the view
    METRIC_BASKET_LABEL: str = "id"  # The filter path of the basket in the queryset
    METRIC_INSTRUMENT_LABEL: str | None = None  # The filter path of the instrument in the queryset. (default to None)
    METRIC_WITH_PREFIXED_KEYS: bool = (
        False  # Set to True if prefixed metrics needs to be appended to the list of metric keys
    )
    METRIC_SHOW_AGGREGATES: bool = True  # set to False if no aggregation needs to be shown for the inserted metrics
    METRIC_SHOW_BY_DEFAULT: bool = True  # If false, the metric are hidden by default
    METRIC_SHOW_FILTERS: bool = False

    display_config_class = InstrumentMetricPivotedListDisplayConfig  # Default display class that automatically regised display Fields into the ListDisplay
    metadata_class = InstrumentMetricMetaData

    @property
    def metric_date(self) -> date | None:
        """
        Property to define at which date the metrics need to be fetched from. Expected to be override
        """
        return None

    @property
    def metric_basket(self) -> Optional["WBModel"]:
        """
        Property to define at for which basket the metrics need to be fetched from. Expected to be override
        """
        return None

    @property
    def metric_basket_class(self) -> Type["Model"]:
        """
        Define the basket class from which the metrics need to be fetched from.

        Default to `metric_basket.__class__` if `metric_basket`  is defined. Otherwise default to the viewset Model property.
        """
        metric_basket_class = self.metric_basket.__class__ if self.metric_basket else self.model
        if not metric_basket_class:
            raise ValueError("Metric Basket Class needs to be defined")
        return metric_basket_class

    @cached_property
    def metric_basket_content_type(self) -> ContentType:
        """
        cached property to store the related basket content type instance
        """
        return ContentType.objects.get_for_model(self.metric_basket_class)

    @property
    def metric_keys(self) -> tuple[MetricKey] | tuple[()]:
        """
        Property used to get the list of metric keys. Can be overridden to define custom logic based on the viewset attributes (e.g. request)
        """
        if self.request.GET.get("metric_show_by_default", "true") == "false":
            return ()
        metric_keys = getattr(self, "METRIC_KEYS", ())
        if metric_keys_filter_repr := self.request.GET.get("metric_keys"):
            metric_keys_filter = metric_keys_filter_repr.split(",")
            metric_keys = tuple(filter(lambda x: x.key in metric_keys_filter, metric_keys))
        return metric_keys

    @property
    def metric_instrument_label(self) -> str | None:
        """
        Property used to get the list of metric instrument label. Can be overridden to define custom logic based on the viewset attributes (e.g. request)
        """
        return getattr(self, "METRIC_INSTRUMENT_LABEL", None)

    @property
    def metric_basket_label(self) -> str:
        """
        Property used to get the list of metric basket label. Can be overridden to define custom logic based on the viewset attributes (e.g. request)
        """
        return getattr(self, "METRIC_BASKET_LABEL", "id")

    @cached_property
    def _metric_serializer_fields(self):
        """
        return the set of serializer fields necessary to display the related metric fields
        """
        extra_serializer_fields = {}
        for metric_key in self.metric_keys:
            metric_backend = backend_registry[metric_key, self.metric_basket_class](self.metric_date)
            extra_serializer_fields.update(
                metric_backend.get_serializer_fields(
                    with_prefixed_key=self.METRIC_WITH_PREFIXED_KEYS, metric_key=metric_key
                )
            )
        return extra_serializer_fields

    def get_ordering_fields(self) -> list[str]:
        """
        Inject the metric field keys as ordering fields
        """
        ordering_fields = list(super().get_ordering_fields())
        for metric_field in self._metric_serializer_fields.keys():
            ordering_fields.append(metric_field)
        return ordering_fields

    def get_queryset(self):
        """
        Annotate the metrics into the viewset queryset
        """
        base_qs = super().get_queryset()
        for metric_key in self.metric_keys:
            base_qs = InstrumentMetric.annotate_with_metrics(
                base_qs,
                metric_key,
                self.metric_basket_class,
                self.metric_date,
                basket_label=self.metric_basket_label,
                instrument_label=self.metric_instrument_label,
            )
        return base_qs

    def get_serializer(self, *args, **kwargs):
        """
        Unwrap defined serializer class and inject the metric fields into a new class
        """

        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())

        BaseMeta = serializer_class.Meta
        fields = list(getattr(BaseMeta, "fields", ()))
        read_only_fields = list(getattr(BaseMeta, "read_only_fields", ()))
        for extra_field in self._metric_serializer_fields.keys():
            fields.append(extra_field)
            read_only_fields.append(extra_field)

        Meta = type(str("Meta"), (BaseMeta,), {"fields": fields, "read_only_fields": read_only_fields})
        new_class = type(
            serializer_class.__name__,
            (serializer_class,),
            {
                "Meta": Meta,
                **self._metric_serializer_fields,
                "SERIALIZER_CLASS_FOR_REMOTE_ADDITIONAL_RESOURCES": serializer_class,
            },
        )

        return new_class(*args, **kwargs)

    def get_aggregates(self, queryset, paginated_queryset):
        """
        Automatically register the metric aggregation
        """
        aggregates = dict()
        if self.METRIC_SHOW_AGGREGATES:
            # we try to inject the instrument metric aggregates automatically
            keys_map = {key.key: key for key in self.metric_keys}
            if self.metric_basket and (ct := self.metric_basket_content_type):
                # for each "general" metric (i.e. without particular instrument attached), we add the raw subfield value as aggregates
                for metric in InstrumentMetric.objects.filter(
                    basket_id=self.metric_basket.id,
                    basket_content_type=ct,
                    date=self.metric_date,
                    key__in=keys_map.keys(),
                    instrument__isnull=True,
                ):
                    metric_key = keys_map[metric.key]
                    for subfield_key, subfield_filter in metric_key.subfields_filter_map.items():
                        if subfield_key in self._metric_serializer_fields and (
                            aggregate_fct := metric_key.subfields_map[subfield_key].aggregate
                        ):
                            aggregates[subfield_key] = {
                                get_aggregate_symbol(aggregate_fct.name): metric.metrics.get(subfield_filter)
                            }
            # for all the missings keys (not present in the aggregates already), we compute the aggregatation based on the aggregate function given by the MetricField class
            missing_aggregate_map = {}
            for metric_key in self.metric_keys:
                for field_key, field_filter in metric_key.subfields_filter_map.items():
                    if field_key in self._metric_serializer_fields.keys() and field_key not in aggregates:
                        missing_aggregate_map[field_key] = metric_key.subfields_map[field_key]
            missing_aggregate = queryset.aggregate(
                **{
                    "agg_" + subfield_key: subfield.aggregate(subfield_key)
                    for subfield_key, subfield in missing_aggregate_map.items()
                    if subfield.aggregate is not None
                }
            )
            for k, v in missing_aggregate.items():
                key = k.replace("agg_", "")
                aggregates[key] = {get_aggregate_symbol(missing_aggregate_map[key].aggregate.name): v}
        return aggregates
