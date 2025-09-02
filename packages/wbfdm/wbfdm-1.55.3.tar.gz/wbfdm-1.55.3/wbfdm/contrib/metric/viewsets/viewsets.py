from django.db.models import Case, Exists, F, IntegerField, OuterRef, When
from wbcore import viewsets

from wbfdm.contrib.metric.filters import InstrumentMetricFilterSet
from wbfdm.contrib.metric.models import InstrumentMetric
from wbfdm.contrib.metric.serializers import (
    InstrumentMetricModelSerializer,
    InstrumentMetricRepresentationSerializer,
)
from wbfdm.contrib.metric.viewsets.configs import InstrumentMetricDisplayConfig


class InstrumentMetricRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering = ["-date"]
    ordering_fields = [
        "key",
        "date",
    ]
    filterset_class = InstrumentMetricFilterSet

    serializer_class = InstrumentMetricRepresentationSerializer
    queryset = InstrumentMetric.objects.all()


class InstrumentMetricViewSet(viewsets.ModelViewSet):
    queryset = InstrumentMetric.objects.select_related("basket_content_type", "instrument").annotate(
        has_children=Exists(InstrumentMetric.objects.filter(parent_metric=OuterRef("pk"))),
        _group_key=Case(When(has_children=True, then=F("id")), default=None, output_field=IntegerField()),
    )

    serializer_class = InstrumentMetricModelSerializer
    filterset_class = InstrumentMetricFilterSet

    display_config_class = InstrumentMetricDisplayConfig

    ordering = ["-date"]
    ordering_fields = [
        "key",
        "date",
    ]
    search_fields = ["key", "instrument__computed_str", "basket_repr"]
