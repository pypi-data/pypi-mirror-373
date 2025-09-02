from reversion.views import RevisionMixin
from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbfdm.models.instruments.instrument_lists import (
    InstrumentList,
    InstrumentListThroughModel,
)
from wbfdm.serializers.instruments.instrument_lists import (
    InstrumentListModelSerializer,
    InstrumentListRepresentationSerializer,
    InstrumentListThroughModelSerializer,
)

from ..configs.display.instrument_lists import (
    InstrumentListDisplayConfig,
    InstrumentListThroughModelDisplayConfig,
)
from ..configs.endpoints.instrument_lists import (
    InstrumentListThroughModelEndpointConfig,
    InstrumentListThroughModelInstrumentEndpointConfig,
    InstrumentListThroughModelInstrumentListEndpointConfig,
)
from ..mixins import InstrumentMixin


class InstrumentListRepresentationModelViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    search_fields = ["name"]
    queryset = InstrumentList.objects.all()
    serializer_class = InstrumentListRepresentationSerializer


class InstrumentListModelViewSet(InternalUserPermissionMixin, RevisionMixin, viewsets.ModelViewSet):
    queryset = InstrumentList.objects.all()
    serializer_class = InstrumentListModelSerializer

    display_config_class = InstrumentListDisplayConfig
    ordering = ("name",)


class InstrumentListThroughModelViewSet(InternalUserPermissionMixin, RevisionMixin, viewsets.ModelViewSet):
    queryset = InstrumentListThroughModel.objects.select_related("instrument", "instrument_list")
    serializer_class = InstrumentListThroughModelSerializer
    endpoint_config_class = InstrumentListThroughModelEndpointConfig

    filterset_fields = {
        "instrument_list": ["exact"],
        "instrument": ["exact"],
        "from_date": ["gte", "lte"],
        "to_date": ["gte", "lte"],
        "validated": ["exact"],
    }
    display_config_class = InstrumentListThroughModelDisplayConfig
    search_fields = ["instrument__name_repr", "instrument_str"]
    ordering_fields = [
        "instrument_list__name",
        "instrument__name",
        "instrument_str",
        "from_date",
        "to_date",
        "validated",
    ]


class InstrumentListThroughModelInstrumentListViewSet(InstrumentListThroughModelViewSet):
    endpoint_config_class = InstrumentListThroughModelInstrumentListEndpointConfig
    ordering = ["instrument__name"]

    def get_queryset(self):
        return super().get_queryset().filter(instrument_list=self.kwargs["instrument_list_id"])


class InstrumentListThroughModelInstrumentViewSet(InstrumentMixin, InstrumentListThroughModelViewSet):
    endpoint_config_class = InstrumentListThroughModelInstrumentEndpointConfig
    ordering = ["instrument_list__name"]

    def get_queryset(self):
        return super().get_queryset().filter(instrument__in=self.instrument.get_family())
