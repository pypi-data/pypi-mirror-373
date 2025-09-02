import pandas as pd
from django.utils.functional import cached_property
from rest_framework.exceptions import ParseError
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.pandas.utils import override_number_to_percent
from wbcore.serializers.fields.types import DisplayMode

from wbfdm.analysis.financial_analysis.financial_metric_analysis import (
    financial_metric_estimate_analysis,
    financial_metric_growths,
)
from wbfdm.enums import Financial
from wbfdm.filters import GroupKeyFinancialsFilterSet
from wbfdm.models.instruments import Instrument
from wbfdm.viewsets.configs.display.statement_with_estimates import (
    StatementWithEstimatesDisplayViewConfig,
)
from wbfdm.viewsets.configs.endpoints.statements import StatementsEndpointViewConfig
from wbfdm.viewsets.configs.titles.statement_with_estimates import (
    StatementTitleViewConfig,
)

from ..mixins import InstrumentMixin


class FinancialMetricAnalysisPandasViewSet(InstrumentMixin, ExportPandasAPIViewSet):
    queryset = Instrument.objects.none()
    display_config_class = StatementWithEstimatesDisplayViewConfig
    endpoint_config_class = StatementsEndpointViewConfig
    title_config_class = StatementTitleViewConfig
    filterset_class = GroupKeyFinancialsFilterSet

    def get_queryset(self):
        return Instrument.objects.filter(id=self.instrument.id)

    def get_pandas_fields(self, request):
        return pf.PandasFields(
            fields=[
                *[pf.FloatField(key=field, label=field, display_mode=DisplayMode.SHORTENED) for field in self.columns],
                pf.PKField(key="id", label="ID"),
                pf.CharField(key="financial", label="Financial"),
                pf.JsonField(key="_overwrites", label="Overwrites"),
            ]
        )

    def get_dataframe(self, request, queryset, **kwargs):
        if group_keys := request.GET.get("group_keys"):
            try:
                financial = Financial(group_keys.lower())
            except ValueError:
                raise ParseError()
            df, self._estimate_mapping, self._columns = financial_metric_estimate_analysis(
                queryset.first().id, financial
            )
            empty_row = pd.Series([None], dtype="float64", name="empty_row")
            df_growth = financial_metric_growths(queryset.first().id, financial)

            df = pd.concat([df_growth, df, empty_row]).dropna(how="all")
            if "financial" in df.columns:
                override_number_to_percent(df, df["financial"].str.contains("(%)"))

            df = df.rename(columns={"index": "id"})
            return df

        return pd.DataFrame()

    @cached_property
    def columns(self):
        if not hasattr(self, "_columns"):
            self.get_dataframe(self.request, self.get_queryset())
        return self._columns

    @property
    def year_columns(self):
        yield from filter(lambda col: "Y" in col, self.columns)

    @property
    def interim_columns(self):
        yield from filter(lambda col: "Y" not in col, self.columns)

    @cached_property
    def estimate_mapping(self):
        if not hasattr(self, "_estimate_mapping"):
            self.get_dataframe(self.request, self.get_queryset())
        return self._estimate_mapping
