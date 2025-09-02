from django.db.models import Case, Exists, F, IntegerField, OuterRef, When
from rest_framework.filters import OrderingFilter
from wbcore import viewsets
from wbcore.contrib.guardian.filters import ObjectPermissionsFilter
from wbcore.pagination import LimitOffsetPagination
from wbcore.viewsets.mixins import DjangoFilterBackend

from wbfdm.contrib.metric.backends.performances import PERFORMANCE_METRIC
from wbfdm.contrib.metric.backends.statistics import STATISTICS_METRIC
from wbfdm.contrib.metric.viewsets.mixins import InstrumentMetricMixin
from wbfdm.filters import InstrumentFilterSet
from wbfdm.import_export.resources.instruments import InstrumentResource
from wbfdm.models import Instrument, InstrumentType
from wbfdm.serializers import (
    InstrumentModelListSerializer,
    InstrumentModelSerializer,
    InstrumentRepresentationSerializer,
    InstrumentTypeRepresentationSerializer,
)

from ..configs import (
    ChildrenInstrumentModelViewConfig,
    InstrumentButtonViewConfig,
    InstrumentDisplayConfig,
    InstrumentEndpointConfig,
    InstrumentTitleConfig,
)
from ..mixins import InstrumentMixin
from .utils import InstrumentSearchFilter


class InstrumentTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = InstrumentType.objects.all()
    serializer_class = InstrumentTypeRepresentationSerializer
    search_fields = ("name", "key")


class InstrumentRepresentationViewSet(viewsets.RepresentationViewSet):
    filter_backends = (ObjectPermissionsFilter, DjangoFilterBackend, OrderingFilter, InstrumentSearchFilter)
    pagination_class = LimitOffsetPagination
    queryset = Instrument.objects.annotate_base_data().exclude(name="")
    serializer_class = InstrumentRepresentationSerializer
    search_fields = ("name", "name_repr", "isin", "ticker", "computed_str")

    filterset_class = InstrumentFilterSet
    ordering_fields = ("title", "ticker")
    ordering = ["name_repr"]


class InstrumentModelViewSet(InstrumentMetricMixin, viewsets.ModelViewSet):
    METRIC_KEYS = (PERFORMANCE_METRIC, STATISTICS_METRIC)
    METRIC_SHOW_AGGREGATES = False
    filter_backends = (ObjectPermissionsFilter, DjangoFilterBackend, OrderingFilter, InstrumentSearchFilter)

    queryset = Instrument.objects.annotate_all().exclude(name="")
    serializer_class = InstrumentModelListSerializer
    ordering_fields = (
        "instrument_type",
        "name_repr",
        "ticker",
        "isin",
        "country__name",
        "currency__key",
    )
    search_fields = (
        "name_repr",
        "name",
        "isin",
        "ticker",
        "computed_str",
        "refinitiv_identifier_code",
        "refinitiv_mnemonic_code",
    )
    ordering = ["name_repr"]

    def get_serializer_class(self):
        if self.get_action() in ["list", "list-metadata"]:
            return InstrumentModelListSerializer
        return InstrumentModelSerializer

    display_config_class = InstrumentDisplayConfig
    title_config_class = InstrumentTitleConfig
    button_config_class = InstrumentButtonViewConfig
    endpoint_config_class = InstrumentEndpointConfig
    filterset_class = InstrumentFilterSet

    def get_resource_class(self):
        return InstrumentResource

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("currency", "country", "instrument_type", "parent", "exchange")
            .prefetch_related("tags", "classifications")
        ).annotate(
            has_children=Exists(Instrument.objects.filter(parent=OuterRef("pk"))),
            _group_key=Case(When(has_children=True, then=F("id")), default=None, output_field=IntegerField()),
            currency_symbol=F("currency__symbol"),
        )
        return qs


class ChildrenInstrumentModelViewSet(InstrumentMixin, InstrumentModelViewSet):
    button_config_class = ChildrenInstrumentModelViewConfig
    ordering = ("-is_primary", "computed_str")

    def get_queryset(self):
        return super().get_queryset().filter(parent=self.instrument)
