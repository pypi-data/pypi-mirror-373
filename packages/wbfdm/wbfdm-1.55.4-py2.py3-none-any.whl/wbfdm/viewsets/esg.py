import pandas as pd
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf

from wbfdm.enums import ESG
from wbfdm.models.instruments import Instrument
from wbfdm.serializers import InstrumentControversySerializer
from wbfdm.viewsets.configs import (
    InstrumentESGControversiesEndpointViewConfig,
    InstrumentESGControversiesTitleViewConfig,
    InstrumentESGControversyDisplayViewConfig,
    InstrumentESGPAIDisplayViewConfig,
    InstrumentESGPAIEndpointViewConfig,
    InstrumentESGPAITitleViewConfig,
)

from .mixins import InstrumentMixin


class InstrumentESGControversiesViewSet(InstrumentMixin, viewsets.ViewSet):
    IDENTIFIER = "wbfdm:instrument-controversy"
    display_config_class = InstrumentESGControversyDisplayViewConfig
    title_config_class = InstrumentESGControversiesTitleViewConfig
    endpoint_config_class = InstrumentESGControversiesEndpointViewConfig
    serializer_class = InstrumentControversySerializer
    queryset = Instrument.objects.none()
    permission_classes = []

    def list(self, request, instrument_id):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()
        serializer = serializer(queryset, many=True)
        return Response({"results": serializer.data})

    def get_queryset(self):
        return sorted(
            Instrument.objects.filter(id=self.instrument.id).dl.esg_controversies(),
            key=lambda x: (x["review"] is None, x["review"]),
            reverse=True,
        )


class InstrumentESGPAIViewSet(InstrumentMixin, ExportPandasAPIViewSet):
    queryset = Instrument.objects.none()
    display_config_class = InstrumentESGPAIDisplayViewConfig
    endpoint_config_class = InstrumentESGPAIEndpointViewConfig
    title_config_class = InstrumentESGPAITitleViewConfig

    def get_queryset(self):
        return Instrument.objects.filter(id=self.instrument.id)

    def get_pandas_fields(self, request):
        return pf.PandasFields(
            fields=[
                pf.PKField(key="index", label="ID"),
                pf.IntegerField(key="section", label="Section"),
                pf.TextField(key="asi", label="Adverse sustainability indicator"),
                pf.TextField(key="metric", label="Metric"),
                pf.TextField(key="factor", label="Factor"),
                pf.FloatField(key="value", label="Value"),
            ]
        )

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame(queryset.dl.esg(values=list(ESG))).reset_index()
        if not df.empty:
            ESG_mapping = ESG.mapping()
            df[["section", "asi", "metric", "factor"]] = pd.DataFrame(
                df.factor_code.map(ESG_mapping).tolist(), index=df.index
            )
        return df
