from contextlib import suppress

import pandas as pd
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.utils.date import get_date_interval_from_request
from wbcore.utils.strings import format_number

from wbfdm.filters import MonthlyPerformancesInstrumentFilterSet
from wbfdm.models.instruments import Instrument
from wbfdm.viewsets.configs import (
    MonthlyPerformancesInstrumentDisplayViewConfig,
    MonthlyPerformancesInstrumentEndpointConfig,
    MonthlyPerformancesInstrumentTitleConfig,
)

from ..mixins import InstrumentMixin


class MonthlyPerformancesInstrumentPandasViewSet(InstrumentMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbfdm:monthlyreturn"

    display_config_class = MonthlyPerformancesInstrumentDisplayViewConfig
    title_config_class = MonthlyPerformancesInstrumentTitleConfig
    endpoint_config_class = MonthlyPerformancesInstrumentEndpointConfig
    filterset_class = MonthlyPerformancesInstrumentFilterSet

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.YearField(key="year", label="Year"),
            pf.FloatField(key="1", label="January", precision=2, percent=True),
            pf.FloatField(key="2", label="February", precision=2, percent=True),
            pf.FloatField(key="3", label="March", precision=2, percent=True),
            pf.FloatField(key="4", label="April", precision=2, percent=True),
            pf.FloatField(key="5", label="May", precision=2, percent=True),
            pf.FloatField(key="6", label="June", precision=2, percent=True),
            pf.FloatField(key="7", label="July", precision=2, percent=True),
            pf.FloatField(key="8", label="August", precision=2, percent=True),
            pf.FloatField(key="9", label="September", precision=2, percent=True),
            pf.FloatField(key="10", label="October", precision=2, percent=True),
            pf.FloatField(key="11", label="November", precision=2, percent=True),
            pf.FloatField(key="12", label="December", precision=2, percent=True),
            pf.FloatField(key="annual", label="Yearly", precision=2, percent=True),
        )
    )

    queryset = Instrument.objects.all()
    ordering_fields = (
        "year",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "annual",
    )
    ordering = ["-year"]

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        annual_perfs = df.annual + 1
        total_perf = annual_perfs.product(axis=0, skipna=False) - 1
        return {"annual": {"Σ": format_number(total_perf)}}

    def get_dataframe(self, request, queryset, **kwargs):
        d1, d2 = get_date_interval_from_request(request, exclude_weekend=True, date_range_fieldname="period")
        df = pd.DataFrame()
        if d1 and d2:
            df, _ = self.instrument.get_monthly_return_summary(d1, d2)
            if not df.empty:
                df = df.pivot_table(index="year", columns=["month"], values="performance").rename_axis(None, axis=1)
                if benchmark_id := request.GET.get("benchmark", None):
                    with suppress(Instrument.DoesNotExist):
                        benchmark = Instrument.objects.get(id=benchmark_id)
                        df_benchmark, _ = benchmark.get_monthly_return_summary(d1, d2)
                        df_benchmark = df_benchmark.pivot_table(
                            index="year", columns=["month"], values="performance"
                        ).rename_axis(None, axis=1)
                        df = df - df_benchmark

                df = df.reset_index()
                df["id"] = df.index
                df.columns = df.columns.astype(str)
        return df
