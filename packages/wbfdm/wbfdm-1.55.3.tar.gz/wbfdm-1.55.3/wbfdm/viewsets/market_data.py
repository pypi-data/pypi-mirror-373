from contextlib import suppress
from datetime import date
from itertools import cycle

import plotly.express as px
from django.utils.functional import cached_property
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from wbcore import viewsets
from wbcore.utils.date import get_date_interval_from_request

from wbfdm.enums import Indicator, MarketDataChartType
from wbfdm.filters import MarketDataChartFilterSet
from wbfdm.models.instruments import Instrument

from .configs import MarketDataChartTitleConfig, PerformanceSummaryChartTitleConfig
from .mixins import InstrumentMixin


class PerformanceSummaryChartViewSet(InstrumentMixin, viewsets.TimeSeriesChartViewSet):
    queryset = Instrument.objects.all()
    title_config_class = PerformanceSummaryChartTitleConfig

    def get_queryset(self):
        return super().get_queryset().filter(id=self.instrument.id)

    def get_plotly(self, queryset):
        today = date.today()
        trace_factory = (
            queryset.first().technical_analysis(from_date=today.replace(year=today.year - 4)).trace_factory()
        )

        fig = go.Figure()
        for trace in trace_factory.performance_summary_trace(bar_options={"color": px.colors.qualitative.T10[0]}):
            fig.add_trace(trace)
        fig.update_layout(
            template="plotly_white",
            yaxis_tickformat="%",
        )
        return fig


class MarketDataChartViewSet(InstrumentMixin, viewsets.TimeSeriesChartViewSet):
    queryset = Instrument.objects.all()
    filterset_class = MarketDataChartFilterSet
    title_config_class = MarketDataChartTitleConfig

    CHART_MAPPING = {
        MarketDataChartType.CLOSE: "close_trace",
        MarketDataChartType.RETURN: "return_trace",
        MarketDataChartType.LOG_RETURN: "log_return_trace",
        MarketDataChartType.DRAWDOWN: "drawdown_trace",
        MarketDataChartType.CANDLESTICK: "candlestick_trace",
        MarketDataChartType.OHLC: "ohlc_trace",
    }
    BENCHMARK_CHART_MAPPING = {
        MarketDataChartType.CLOSE: "close_trace",
        MarketDataChartType.RETURN: "return_trace",
        MarketDataChartType.LOG_RETURN: "log_return_trace",
        MarketDataChartType.DRAWDOWN: "drawdown_trace",
        MarketDataChartType.CANDLESTICK: "close_trace",
        MarketDataChartType.OHLC: "close_trace",
    }
    STATISTIC_MAPPING = {
        MarketDataChartType.CLOSE: "close",
        MarketDataChartType.RETURN: "cum-ret",
        MarketDataChartType.LOG_RETURN: "cum-log-ret",
        MarketDataChartType.DRAWDOWN: "drawdown",
        MarketDataChartType.CANDLESTICK: "close",
        MarketDataChartType.OHLC: "close",
    }
    INDICATOR_MAPPING = {
        Indicator.SMA_50: 50,
        Indicator.SMA_100: 100,
        Indicator.SMA_120: 120,
        Indicator.SMA_200: 200,
    }

    def get_queryset(self):
        return super().get_queryset().filter(id=self.instrument.id)

    def get_benchmark_queryset(self):
        return Instrument.objects.filter(id__in=self.benchmarks_ids)

    @cached_property
    def benchmarks_ids(self) -> list[int]:
        if benchmarks_str := self.request.GET.get("benchmarks", None):
            return benchmarks_str.split(",")
        return []

    def get_parameters(self) -> list:
        return self.request.GET.get("parameters", "").split(";")

    def get_plotly(self, queryset):
        # Parametrization
        chart_type = MarketDataChartType(self.request.GET.get("chart_type", "close"))
        volume = self.request.GET.get("volume", "false") == "true"
        show_estimates = self.request.GET.get("show_estimates", "false") == "true"
        from_date, to_date = get_date_interval_from_request(self.request, date_range_fieldname="period")
        colors = cycle(px.colors.qualitative.T10)

        # Bootstrap chart
        fig = make_subplots(
            rows=2 if volume else 1,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_width=[0.2, 0.7] if volume else [1],
        )

        # Generate Chart for main timeseries
        ta = queryset.first().technical_analysis(from_date, to_date)
        factory = ta.trace_factory()
        for trace in getattr(factory, self.CHART_MAPPING[chart_type])(
            line_options=dict(color=next(colors)), show_estimates=show_estimates
        ):
            fig.add_trace(trace)

        # Generate Charts for all added benchmarks
        for benchmark in self.get_benchmark_queryset():
            _factory = benchmark.technical_benchmark_analysis(ta.df.index.min(), to_date).trace_factory()
            for trace in getattr(_factory, self.BENCHMARK_CHART_MAPPING[chart_type])(
                base_series=ta.df[self.STATISTIC_MAPPING[chart_type]],
                line_options=dict(color=next(colors)),
            ):
                fig.add_trace(trace)

        # Generate Charts for any selected indicators
        if indicators := self.request.GET.get("indicators", None):
            for indicator in indicators.split(","):
                for trace in factory.sma_trace(
                    self.INDICATOR_MAPPING[Indicator(indicator)], line_options=dict(color=next(colors))
                ):
                    fig.add_trace(trace)

        if volume:
            fig.add_trace(
                factory.volume_trace(),
                row=2,
                col=1,
            )

        fig.update_layout(
            template="plotly_white",
            legend=dict(x=0.02, y=0.98, bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0, r=0, t=0, b=40),
            xaxis_rangeslider_visible=False,
            showlegend=True,
            hovermode="x",
        )
        fig.update_xaxes(rangebreaks=[{"pattern": "day of week", "bounds": [6, 1]}])

        for i, d in enumerate(fig.data):
            with suppress(AttributeError, IndexError, ValueError):  # Either Candlestick or OHCL
                if (y := d.y[-1]) is not None:
                    text_value = (
                        f"{y:.2%}"
                        if chart_type in [MarketDataChartType.RETURN, MarketDataChartType.LOG_RETURN]
                        else f"{y:.1f}"
                    )
                    fig.add_scatter(
                        x=[d.x[-1]],
                        y=[y],
                        name=d.name,
                        mode="markers+text",
                        text=text_value,
                        textfont=dict(color=d.line.color),
                        textposition="middle right",
                        marker=dict(color=d.line.color, size=12, symbol="circle"),
                        legendgroup=d.name,
                        showlegend=False,
                    )
        return fig
