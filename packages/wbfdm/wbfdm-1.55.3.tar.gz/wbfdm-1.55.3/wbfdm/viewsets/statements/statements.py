import pandas as pd
from django.utils.functional import cached_property
from wbcore.cache.decorators import cache_table
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.serializers.fields.types import DisplayMode
from wbcore.utils.date import get_next_day_timedelta

from wbfdm.enums import DataType, PeriodType, StatementType
from wbfdm.filters import StatementFilter
from wbfdm.models.instruments import Instrument
from wbfdm.utils import rename_period_index_level_to_repr
from wbfdm.viewsets.configs.display.statements import StatementDisplayViewConfig
from wbfdm.viewsets.configs.endpoints.statements import StatementsEndpointViewConfig
from wbfdm.viewsets.configs.titles.statement_with_estimates import (
    StatementTitleViewConfig,
)

from ..mixins import InstrumentMixin


@cache_table(
    timeout=lambda view: get_next_day_timedelta(),
    key_prefix=lambda view: f"_{view.instrument.id}_{view.financial_analysis_key}_{view.data_type_key}",
)
class StatementPandasViewSet(InstrumentMixin, ExportPandasAPIViewSet):
    queryset = Instrument.objects.none()
    display_config_class = StatementDisplayViewConfig
    endpoint_config_class = StatementsEndpointViewConfig
    title_config_class = StatementTitleViewConfig
    filterset_class = StatementFilter

    financial_analysis_mapping = {
        "income-statement": (StatementType.INCOME_STATEMENT, "Income Statement"),
        "balance-sheet": (StatementType.BALANCE_SHEET, "Balance Sheet"),
        "cash-flow-statement": (StatementType.CASHFLOW_STATEMENT, "Cashflow Statement"),
    }

    @cached_property
    def data_type_key(self) -> str:
        return self.request.GET.get("data_type", "standardized")

    @cached_property
    def financial_analysis_key(self) -> str:
        return self.kwargs.get("statement", "income-statement")

    def get_queryset(self):
        return Instrument.objects.filter(id=self.instrument.id)

    def get_pandas_fields(self, request):
        return pf.PandasFields(
            fields=[
                pf.PKField(key="external_ordering", label="ID"),
                pf.CharField(key="external_code", label="Code"),
                pf.CharField(key="external_description", label="Description"),
                pf.SparklineField(key="progress", label="Yearly Trend", dimension="double"),
                *[
                    pf.FloatField(key=field, label=field, display_mode=DisplayMode.SHORTENED)
                    for field in self.columns
                    if field not in ["external_ordering", "external_code", "external_description", "progress"]
                ],
            ]
        )

    def get_dataframe(self, request, queryset, **kwargs):
        financial_analysis = self.financial_analysis_mapping.get(self.financial_analysis_key)[0]
        df = pd.DataFrame(
            Instrument.objects.filter(id=self.instrument.id).dl.statements(
                statement_type=financial_analysis,
                data_type=DataType(self.data_type_key),
                period_type=PeriodType.ALL,
            )
        )
        if not df.empty:
            df = df.pivot_table(
                index=["year", "interim", "period_type"],
                columns=["external_ordering", "external_code", "external_description"],
                values=["value"],
                aggfunc="first",
            )

            df = rename_period_index_level_to_repr(df)
            df = df.set_index([[f"{index[0]}-{index[1]}" for index in df.index]])
            df = df.T.reset_index()
        return df

    def manipulate_dataframe(self, df):
        if not df.empty:
            if year_cols := [col for col in df.columns if isinstance(col, str) and "Y" in col]:
                df["progress"] = df[year_cols].fillna(0).apply(lambda x: list(x.to_dict().items()), axis=1)
        return df

    @cached_property
    def columns(self):
        return self.df.columns

    @cached_property
    def year_columns(self):
        year_columns = list(map(lambda x: int(x.replace("-Y", "")), filter(lambda col: "Y" in col, self.columns)))
        year_columns.sort(reverse=True)
        return year_columns

    @cached_property
    def interim_columns(self):
        return list(filter(lambda col: "Y" not in col, self.columns))
