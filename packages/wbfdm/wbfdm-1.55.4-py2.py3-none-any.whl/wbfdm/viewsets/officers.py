from rest_framework.response import Response
from wbcore import viewsets

from wbfdm.models.instruments import Instrument
from wbfdm.serializers import OfficerSerializer
from wbfdm.viewsets.configs.display.officers import OfficerDisplayViewConfig
from wbfdm.viewsets.configs.titles.instruments import SubviewInstrumentTitleViewConfig

from .mixins import InstrumentMixin


class OfficerViewSet(InstrumentMixin, viewsets.ViewSet):
    IDENTIFIER = "wbfdm:instrument-officers"
    SUBVIEW_NAME = "Officers"
    display_config_class = OfficerDisplayViewConfig
    title_config_class = SubviewInstrumentTitleViewConfig
    serializer_class = OfficerSerializer
    permission_classes = []

    def list(self, request, instrument_id):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()
        serializer = serializer(queryset, many=True)
        return Response({"results": serializer.data})

    def get_queryset(self):
        queryset = Instrument.objects.filter(id=self.instrument.id)
        return queryset.dl.officers()
