from decimal import Decimal
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from django.contrib.messages import warning
from django.db.models import Case, Exists, F, FloatField, OuterRef, When, Window
from django.db.models.functions import Lead
from rest_framework import filters
from wbcore import viewsets
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.filters import DjangoFilterBackend
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.utils.date import get_date_interval_from_request
from wbcore.utils.figures import (
    get_default_timeserie_figure,
    get_hovertemplate_timeserie,
)
from wbcore.utils.strings import format_number

from wbfdm.analysis.financial_analysis.financial_statistics_analysis import (
    FinancialStatistics,
)
from wbfdm.filters.instrument_prices import (
    InstrumentPriceFilterSet,
    InstrumentPriceFinancialStatisticsChartFilterSet,
    InstrumentPriceFrequencyFilter,
    InstrumentPriceInstrumentFilterSet,
    InstrumentPriceSingleBenchmarkFilterSet,
)
from wbfdm.import_export.resources.instrument_prices import (
    InstrumentPriceExportResource,
)
from wbfdm.models import Instrument, InstrumentPrice
from wbfdm.serializers import (
    InstrumentPriceInstrumentModelSerializer,
    InstrumentPriceModelSerializer,
)
from wbfdm.viewsets.configs import (
    BestAndWorstReturnsInstrumentEndpointConfig,
    BestAndWorstReturnsInstrumentPandasDisplayConfig,
    BestAndWorstReturnsInstrumentTitleConfig,
    FinancialStatisticsInstrumentButtonConfig,
    FinancialStatisticsInstrumentEndpointConfig,
    FinancialStatisticsInstrumentPandasDisplayConfig,
    FinancialStatisticsInstrumentTitleConfig,
    InstrumentPriceButtonConfig,
    InstrumentPriceDisplayConfig,
    InstrumentPriceInstrumentButtonConfig,
    InstrumentPriceInstrumentDistributionReturnsChartEndpointConfig,
    InstrumentPriceInstrumentDistributionReturnsChartTitleConfig,
    InstrumentPriceInstrumentEndpointConfig,
    InstrumentPriceInstrumentTitleConfig,
    InstrumentPriceStatisticsInstrumentEndpointConfig,
    InstrumentPriceStatisticsInstrumentTitleConfig,
    InstrumentPriceTitleConfig,
)

from ..mixins import InstrumentMixin


class InstrumentPriceModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbfdm:price"
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    queryset = InstrumentPrice.objects.all()
    serializer_class = InstrumentPriceModelSerializer

    filterset_class = InstrumentPriceFilterSet
    ordering = ["-date"]
    ordering_fields = [
        "date",
        "gross_value",
        "daily_diff_gross_value",
        "net_value",
        "daily_diff_net_value",
        "market_capitalization",
        "sharpe_ratio",
        "correlation",
        "beta",
        "outstanding_shares_consolidated",
        "volume",
        "volume_50d",
    ]

    display_config_class = InstrumentPriceDisplayConfig
    title_config_class = InstrumentPriceTitleConfig
    button_config_class = InstrumentPriceButtonConfig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                real_price_exists=Exists(
                    InstrumentPrice.objects.filter(
                        instrument=OuterRef("instrument_id"), calculated=False, date=OuterRef("date")
                    )
                ),
                currency_symbol=F("instrument__currency__symbol"),
            )
            .annotate_base_data()
            .select_related("instrument")
        )


class InstrumentPriceInstrumentModelViewSet(InstrumentMixin, InstrumentPriceModelViewSet):
    IDENTIFIER = "wbfdm:instrument-price"

    title_config_class = InstrumentPriceInstrumentTitleConfig
    button_config_class = InstrumentPriceInstrumentButtonConfig
    endpoint_config_class = InstrumentPriceInstrumentEndpointConfig

    filterset_class = InstrumentPriceInstrumentFilterSet
    serializer_class = InstrumentPriceInstrumentModelSerializer
    IMPORT_ALLOWED = False

    def get_resource_class(self):
        return InstrumentPriceExportResource

    def get_aggregates(self, queryset, paginated_queryset):
        res = dict()
        if queryset.exists():
            if (first_net_value := queryset.earliest("date").net_value) and (
                last_net_value := queryset.latest("date").net_value
            ):
                diff_net = last_net_value / first_net_value - 1 if first_net_value != 0 else 0
                res["daily_diff_net_value"] = {"∆": format_number(diff_net)}
            if (first_gross_value := queryset.earliest("date").gross_value) and (
                last_gross_value := queryset.latest("date").gross_value
            ):
                diff_gross = last_gross_value / first_gross_value - 1 if first_gross_value != 0 else 0
                res["daily_diff_gross_value"] = {"∆": format_number(diff_gross)}
        return res

    def get_queryset(self):
        queryset = super().get_queryset().filter(instrument=self.instrument)
        if "calculated" not in self.request.GET:
            queryset = queryset.filter_only_valid_prices()
        return (
            queryset.annotate(
                last_net_value=Window(Lead("net_value"), order_by="-date"),
                last_gross_value=Window(Lead("gross_value"), order_by="-date"),
                daily_diff_net_value=Case(
                    When(last_net_value=0, then=None),
                    default=F("net_value") / F("last_net_value") - 1,
                    output_field=FloatField(),
                ),
                daily_diff_gross_value=Case(
                    When(last_gross_value=0, then=None),
                    default=F("gross_value") / F("last_gross_value") - 1,
                    output_field=FloatField(),
                ),
            )
            .select_related("instrument")
            .select_related("import_source")
        )


class InstrumentPriceInstrumentStatisticsChartView(InstrumentMixin, viewsets.ChartViewSet):
    IDENTIFIER = "wbfdm:instrument-statisticschart"
    queryset = InstrumentPrice.objects.all()

    title_config_class = InstrumentPriceStatisticsInstrumentTitleConfig
    endpoint_config_class = InstrumentPriceStatisticsInstrumentEndpointConfig

    def get_queryset(self):
        return InstrumentPrice.objects.filter(instrument=self.instrument, calculated=False)

    def get_plotly(self, queryset):
        fig = get_default_timeserie_figure()

        if self.instrument.related_instruments.count() > 0:
            reference = self.instrument.related_instruments.first().name_repr
            df = pd.DataFrame(queryset.values("date", "sharpe_ratio", "correlation", "beta")).replace(
                [np.inf, -np.inf], np.nan
            )

            if not df.empty:
                df = df.set_index("date").sort_index().dropna()
                if risk_instrument := self.instrument.primary_risk_instrument:
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df.sharpe_ratio,
                            mode="lines",
                            name=f"Sharpe Ratio ({risk_instrument.name_repr})",
                            hovertemplate=get_hovertemplate_timeserie(currency=""),
                        )
                    )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df.correlation,
                        mode="lines",
                        name=f"Correlation ({reference})",
                        hovertemplate=get_hovertemplate_timeserie(currency=""),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df.beta,
                        mode="lines",
                        name=f"Beta ({reference})",
                        hovertemplate=get_hovertemplate_timeserie(currency=""),
                    )
                )
        else:
            warning(
                self.request,
                "The chart is empty because there is no benchmark or risk free rate associated to this instrument",
                extra_tags="auto_close=0",
            )

        return fig


class FinancialStatisticsInstrumentPandasView(InstrumentMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbfdm:financialstatistics"

    LIST_DOCUMENTATION = "wbfdm/markdown/documentation/financial_statistics.md"

    queryset = InstrumentPrice.objects.all()
    endpoint_config_class = FinancialStatisticsInstrumentEndpointConfig
    title_config_class = FinancialStatisticsInstrumentTitleConfig
    display_config_class = FinancialStatisticsInstrumentPandasDisplayConfig
    button_config_class = FinancialStatisticsInstrumentButtonConfig
    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="financial", label="Financial"),
            pf.CharField(key="instrument_statistics", label="Instrument"),
            pf.CharField(key="benchmark_statistics", label="Benchmark"),
            pf.CharField(key="instrument_one_year", label="Instrument - One Year"),
            pf.CharField(key="benchmark_one_year", label="Benchmark - One Year"),
            pf.BooleanField(key="instrument_vs_benchmark", label="Instrument VS Benchmark"),
            pf.BooleanField(key="instrument_vs_benchmark_one_year", label="Instrument VS Benchmark - One Year"),
        )
    )

    filterset_class = InstrumentPriceSingleBenchmarkFilterSet
    search_fields = ("financial",)
    ordering_fields = (
        "financial" "instrument_statistics",
        "benchmark_statistics",
        "instrument_one_year",
        "benchmark_one_year",
    )

    def get_dataframe(self, request, queryset, **kwargs):
        starting_date, end_date = get_date_interval_from_request(request, exclude_weekend=True)

        if request.GET.get("benchmark", None):
            benchmark = Instrument.objects.get(id=request.GET["benchmark"])
        else:
            benchmark = self.instrument.primary_benchmark

        df = pd.DataFrame()

        instrument_prices = self.instrument.get_prices_df(from_date=starting_date, to_date=end_date)
        instrument_risk_free_rate_prices_df = (
            self.instrument.primary_risk_instrument.get_prices_df(from_date=starting_date, to_date=end_date)
            if self.instrument.primary_risk_instrument
            else pd.Series(dtype=float)
        )

        benchmark_prices = (
            benchmark.get_prices_df(from_date=starting_date, to_date=end_date) if benchmark else pd.Series(dtype=float)
        )
        benchmark_risk_free_rate_prices_df = (
            benchmark.primary_risk_instrument.get_prices_df(from_date=starting_date, to_date=end_date)
            if (benchmark and benchmark.primary_risk_instrument)
            else pd.Series(dtype=float)
        )

        if instrument_prices.empty or instrument_prices.shape[0] < 2:
            return df

        df["financial"] = [
            "Name",
            "Date From",
            "To Date",
            "Daily Mean Return",
            "Compound Annual Growth Rate",
            "Last Cumulative Return",
            "Ann. Volatility",
            "Beta",
            "Correlation",
            "Risk free rate",
            "Sharpe Ratio",
            "Maximum Drawdown",
            "Maximum Drawdown Date",
            "Longest Drawdown Period",
            "Last Maximum Drawdown",
            "Last Maximum Drawdown Date",
            "Value at Risk 1%",
            "Value at Risk 5%",
            "Value at Risk 10%",
            "Conditional Value at Risk 1%",
            "Conditional Value at Risk 5%",
            "Conditional Value at Risk 10%",
            "Skewness",
            "Excess Kurtosis",
            "Sortino Ratio",
            "Adj. Sortino Ratio",
            "Calmar Ratio",
            "Sterling Ratio",
            "Burke Ratio",
        ]

        def metric_string_adjusted(metric: [float, None], in_pct: bool = True):
            str_adj = ""
            if metric:
                str_adj = f"{round(metric * 100, 2)}%" if in_pct else f"{round(metric, 2)}"
            return str_adj

        def fill_df(
            _instrument_title: str,
            _instrument_statistics: FinancialStatistics,
            _benchmark_prices_df: pd.DataFrame,
            _risk_free_rate_prices_df: pd.DataFrame,
        ) -> list[Any]:
            return [
                _instrument_title,
                _instrument_statistics.start.strftime("%Y-%m-%d"),
                _instrument_statistics.end.strftime("%Y-%m-%d"),
                metric_string_adjusted(_instrument_statistics.get_mean_return()),
                metric_string_adjusted(_instrument_statistics.get_compound_annual_growth_rate()),
                metric_string_adjusted(_instrument_statistics.get_last_cumulative_return()),
                metric_string_adjusted(_instrument_statistics.get_volatility()),
                metric_string_adjusted(_instrument_statistics.get_beta(benchmark_prices_df=_benchmark_prices_df)),
                metric_string_adjusted(
                    _instrument_statistics.get_correlation(benchmark_prices_df=_benchmark_prices_df)
                ),
                metric_string_adjusted(_instrument_statistics.get_risk_free_rate(_risk_free_rate_prices_df)),
                metric_string_adjusted(
                    _instrument_statistics.get_sharpe_ratio(_risk_free_rate_prices_df), in_pct=False
                ),
                metric_string_adjusted(_instrument_statistics.get_maximum_drawdown()),
                _instrument_statistics.get_maximum_drawdown_date(),
                f"{_instrument_statistics.get_longest_drawdown_period()} days",
                metric_string_adjusted(_instrument_statistics.get_last_recent_maximum_drawdown()),
                _instrument_statistics.get_last_recent_maximum_drawdown_date(),
                metric_string_adjusted(_instrument_statistics.get_value_at_risk(alpha=0.01)),
                metric_string_adjusted(_instrument_statistics.get_value_at_risk(alpha=0.05)),
                metric_string_adjusted(_instrument_statistics.get_value_at_risk(alpha=0.1)),
                metric_string_adjusted(_instrument_statistics.get_conditional_value_at_risk(alpha=0.01)),
                metric_string_adjusted(_instrument_statistics.get_conditional_value_at_risk(alpha=0.05)),
                metric_string_adjusted(_instrument_statistics.get_conditional_value_at_risk(alpha=0.10)),
                metric_string_adjusted(_instrument_statistics.get_skewness(), in_pct=False),
                metric_string_adjusted(_instrument_statistics.get_excess_kurtosis(), in_pct=False),
                metric_string_adjusted(_instrument_statistics.get_sortino_ratio(), in_pct=False),
                metric_string_adjusted(_instrument_statistics.get_adjusted_sortino_ratio(), in_pct=False),
                metric_string_adjusted(_instrument_statistics.get_calmar_ratio(), in_pct=False),
                metric_string_adjusted(
                    _instrument_statistics.get_sterling_ratio(_risk_free_rate_prices_df), in_pct=False
                ),
                metric_string_adjusted(
                    _instrument_statistics.get_burke_ratio(_risk_free_rate_prices_df), in_pct=False
                ),
            ]

        df["instrument_statistics"] = fill_df(
            self.instrument.name,
            FinancialStatistics(instrument_prices),
            benchmark_prices,
            instrument_risk_free_rate_prices_df,
        )
        instrument_before_previous_year_date = max(
            instrument_prices.index[0], instrument_prices.index[-1] - relativedelta(years=1)
        )
        df["instrument_one_year"] = fill_df(
            self.instrument.name,
            FinancialStatistics(instrument_prices.truncate(before=instrument_before_previous_year_date)),
            benchmark_prices.truncate(before=instrument_before_previous_year_date),
            instrument_risk_free_rate_prices_df.truncate(before=instrument_before_previous_year_date),
        )

        if not benchmark_prices.empty:
            df["benchmark_statistics"] = fill_df(
                benchmark.name,
                FinancialStatistics(benchmark_prices),
                benchmark_prices,
                benchmark_risk_free_rate_prices_df,
            )
            benchmark_before_previous_year_date = max(
                benchmark_prices.index[0], benchmark_prices.index[-1] - relativedelta(years=1)
            )

            df["benchmark_one_year"] = fill_df(
                benchmark.name,
                FinancialStatistics(benchmark_prices.truncate(before=benchmark_before_previous_year_date)),
                benchmark_prices.truncate(before=benchmark_before_previous_year_date),
                benchmark_risk_free_rate_prices_df.truncate(before=benchmark_before_previous_year_date),
            )
            df["instrument_vs_benchmark"] = df[["instrument_statistics", "benchmark_statistics"]].apply(
                lambda x: x["instrument_statistics"] - x["benchmark_statistics"] > 0
                if type(x["instrument_statistics"]) in [float, Decimal]
                and type(x["benchmark_statistics"]) in [float, Decimal]
                else False,
                axis=1,
            )
            df["instrument_vs_benchmark_one_year"] = df[["instrument_one_year", "benchmark_one_year"]].apply(
                lambda x: x["instrument_one_year"] - x["benchmark_one_year"] > 0
                if type(x["instrument_one_year"]) in [float, Decimal]
                and type(x["benchmark_one_year"]) in [float, Decimal]
                else False,
                axis=1,
            )
        df["id"] = df.index
        return df

    def manipulate_dataframe(self, df):
        return df.where(pd.notnull(df), 0)


class InstrumentPriceInstrumentDistributionReturnsChartView(InstrumentMixin, viewsets.ChartViewSet):
    IDENTIFIER = "wbfdm:instrument-distributionreturnschart"
    queryset = InstrumentPrice.objects.all()

    title_config_class = InstrumentPriceInstrumentDistributionReturnsChartTitleConfig
    endpoint_config_class = InstrumentPriceInstrumentDistributionReturnsChartEndpointConfig
    filterset_class = InstrumentPriceFinancialStatisticsChartFilterSet

    def get_plotly(self, queryset):
        fig = go.Figure()

        def update_layout(text):
            fig.update_layout(
                title={"text": text, "y": 0, "x": 0.5, "xanchor": "center", "yanchor": "bottom"},
                yaxis_title="Density",
                xaxis_title="Returns in %",
                legend_title="Instruments",
            )

        if self.request.GET.get("benchmark", None):
            benchmark = Instrument.objects.get(id=self.request.GET["benchmark"])
        else:
            benchmark = self.instrument.primary_benchmark

        starting_date, end_date = get_date_interval_from_request(self.request, exclude_weekend=True)
        first_day_available_of_instrument = self.instrument.inception_date.strftime("%Y-%m-%d")
        instrument_prices = self.instrument.get_prices_df(from_date=starting_date, to_date=end_date)

        if instrument_prices.empty:
            update_layout(f"{self.instrument} has no data or not enough data")
            return fig
        if not starting_date:
            starting_date = instrument_prices.index[0]
        if not end_date:
            end_date = instrument_prices.index[-1]

        returns_df = pd.DataFrame()
        returns_df[self.instrument] = (
            self.instrument._compute_performance(instrument_prices, freq=self.request.GET.get("frequency"))[
                "performance"
            ]
            * 100
        )
        returns_df.columns = [f"{self.instrument} - #data:{len(returns_df[self.instrument].dropna())}"]
        import plotly.figure_factory as ff

        if returns_df.empty:
            return go.Figure()
        returns_df = returns_df.astype(float)
        fig = ff.create_distplot(
            [returns_df[c] for c in returns_df.columns],
            [f"{returns_df.columns[x]}" for x in range(len(returns_df.columns))],
            bin_size=0.3,
        )
        if not benchmark:
            update_layout(f"Inception Date -- {self.instrument.name}: {first_day_available_of_instrument}")
            return fig

        benchmark_prices = benchmark.get_prices_df(from_date=starting_date, to_date=end_date)
        if benchmark_prices.empty:
            update_layout(
                f"Inception Date -- {self.instrument.name}: {first_day_available_of_instrument}"
                f" // {benchmark} has no data"
            )
            return fig

        if starting_date < benchmark.inception_date:
            update_layout(
                f"Inception Date -- {self.instrument.name}: {first_day_available_of_instrument}"
                f" // {benchmark.name}: {benchmark.inception_date.strftime('%Y-%m-%d')}"
            )
            return fig
        returns_df[benchmark] = benchmark.extract_daily_performance_df(benchmark_prices)["performance"] * 100
        returns_df.columns = [
            returns_df.columns[0],
            f"{benchmark} - #data:{len(returns_df[benchmark].dropna())}",
        ]
        returns_df = returns_df.dropna()

        fig = ff.create_distplot(
            [returns_df[c] for c in returns_df.columns],
            [f"{returns_df.columns[x]}" for x in range(len(returns_df.columns))],
            bin_size=0.3,
        )
        update_layout(
            f"Inception Date -- {self.instrument.name}: {first_day_available_of_instrument}"
            f" // {benchmark.name}: {benchmark.inception_date.strftime('%Y-%m-%d')}"
        )
        return fig


class BestAndWorstReturnsInstrumentPandasView(InstrumentMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbfdm:bestandworstreturns"

    queryset = InstrumentPrice.objects.all()
    endpoint_config_class = BestAndWorstReturnsInstrumentEndpointConfig
    title_config_class = BestAndWorstReturnsInstrumentTitleConfig
    display_config_class = BestAndWorstReturnsInstrumentPandasDisplayConfig

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.DateField(key="date_best_returns", label="Date Best Returns"),
            pf.FloatField(key="best_returns", label="Best Returns", precision=3, percent=True),
            pf.DateField(key="date_worst_returns", label="Date Worst Returns"),
            pf.FloatField(key="worst_returns", label="Worst Returns", precision=3, percent=True),
        )
    )

    filterset_class = InstrumentPriceFrequencyFilter
    ordering_fields = ("date_best_returns" "best_returns", "date_worst_returns", "worst_returns")

    def get_dataframe(self, request, queryset, **kwargs):
        df_to_display = pd.DataFrame()
        from_date, to_date = get_date_interval_from_request(self.request, date_range_fieldname="date")
        if not (prices_df := self.instrument.get_prices_df(from_date=from_date, to_date=to_date)).empty:
            returns_df = FinancialStatistics(prices_df).get_best_and_worst_returns(freq=request.GET.get("frequency"))
            if not returns_df.empty and returns_df.shape[0] > 0:
                df_to_display["date_best_returns"] = returns_df["Date Best Return"].dt.strftime("%Y-%m-%d")
                df_to_display["best_returns"] = returns_df["Best Return"]
                df_to_display["date_worst_returns"] = returns_df["Date Worst Return"].dt.strftime("%Y-%m-%d")
                df_to_display["worst_returns"] = returns_df["Worst Return"]

            df_to_display["id"] = df_to_display.index
        return df_to_display
