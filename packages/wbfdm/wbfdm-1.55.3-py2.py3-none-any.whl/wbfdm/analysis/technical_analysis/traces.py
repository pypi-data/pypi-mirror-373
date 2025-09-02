from contextlib import suppress
from typing import TYPE_CHECKING, Iterable, TypeVar

import pandas as pd
from plotly import graph_objects as go

from ..utils import normalize_series

if TYPE_CHECKING:
    from wbfdm.analysis.technical_analysis.technical_analysis import TechnicalAnalysis


T = TypeVar("T", bound=go.Candlestick | go.Ohlc)


class TechnicalAnalysisTraceFactory:
    def __init__(self, ta: "TechnicalAnalysis"):
        self.ta = ta

    def _line_trace(
        self,
        key: str,
        prefix: str,
        base_series: pd.Series | None = None,
        percent_format: bool = False,
        line_options: dict | None = None,
        show_estimates: bool = False,
    ) -> go.Scatter:
        # Parametrization
        series = self.ta.df[key]

        # get the calculated time series. By default all value are considered non estimated
        calculated = pd.Series(False, index=self.ta.df.index)
        with suppress(KeyError, UserWarning):
            if show_estimates:
                calculated = self.ta.df["calculated"]

        if not (series := normalize_series(series, base_series=base_series)).empty:
            inception_date = series.loc[~calculated].index.min()
            real_series = series.loc[series.index >= inception_date]

            # Prepare chart options
            name = str(self.ta.instrument)
            line_options = line_options if line_options else {}
            text = []
            if base_series is not None and not base_series.empty:
                prefix = f"Normalized {prefix}"
            format_template = "{y:.2%}" if percent_format else "{y:.2f}"
            hovertemplate = "<b>" + prefix + "</b>: %" + format_template
            # If a base series is present, we add a line into the hover template to show the difference
            if base_series is not None and not base_series.empty:
                hovertemplate += "<br>∆ : %{text}"
                text = [format_template.format(y=y) for y in (real_series - base_series).dropna().values]

            yield go.Scatter(
                x=real_series.index,
                y=real_series,
                line=line_options,
                name=name,
                legendgroup=name,
                hovertemplate=hovertemplate,
                text=text,
            )
            # If data happens before the inception date, we consider them as estimated/backtesting data
            backtesting_series = series.loc[series.index < inception_date]
            if not backtesting_series.empty:
                yield go.Scatter(
                    x=backtesting_series.index,
                    y=backtesting_series,
                    line={**line_options, "dash": "dashdot"},
                    name="Estimated " + name,
                    legendgroup=name,
                )

    def _ohlc_trace(self, graph_object: type[T]) -> Iterable[T]:
        df = self.ta.df
        name = str(self.ta.instrument)
        yield graph_object(
            x=df["close"].index,
            close=df["close"].values,
            open=df["open"].values,
            high=df["high"].values,
            low=df["low"].values,
            name=name,
            legendgroup=name,
        )

    def performance_summary_trace(self, bar_options: dict | None = None, **kwargs) -> go.Bar:
        summaries = {
            "36 Months": self.ta.get_performance_months(months=36),
            "24 Months": self.ta.get_performance_months(months=24),
            "12 Months": self.ta.get_performance_months(months=12),
            "YTD": self.ta.get_performance_year_to_date(),
            "6 Months": self.ta.get_performance_months(months=6),
            "3 Months": self.ta.get_performance_months(months=3),
            "1 Months": self.ta.get_performance_months(months=1),
        }

        yield go.Bar(
            x=list(reversed(summaries.keys())),
            y=list(reversed(summaries.values())),
            text=list(map(lambda x: f"{x:.2%}", reversed(summaries.values()))),
            textposition="auto",
            marker=bar_options,
        )

    def volume_trace(self) -> go.Bar:
        df = self.ta.df
        df["color_volume"] = "green"
        df.loc[df.volume < 0, "color_volume"] = "red"
        bar_chart_name = "Inflow/Outflow" if self.ta.instrument.is_managed else "Volume"
        return go.Bar(
            x=df.index,
            y=df["volume"],
            name=bar_chart_name,
            hovertemplate="<b>" + bar_chart_name + "</b><br>%{x}<br>%{y:.4s}<extra></extra>",
            marker={"color": df.color_volume, "opacity": 0.4},
            yaxis="y2",
        )

    def close_trace(
        self,
        base_series: pd.Series | None = None,
        line_options: dict | None = None,
        show_estimates: bool = False,
        **kwargs,
    ) -> go.Scatter:
        yield from self._line_trace(
            "close", "Close", base_series=base_series, line_options=line_options, show_estimates=show_estimates
        )

    def sma_trace(
        self, window: int, base_series: pd.Series | None = None, line_options: dict | None = None, **kwargs
    ) -> go.Scatter:
        self.ta.add_sma(window)
        yield from self._line_trace(
            f"close_{window}_sma", f"SMA {window}", base_series=base_series, line_options=line_options
        )

    def return_trace(
        self, base_series: pd.Series | None = None, line_options: dict | None = None, **kwargs
    ) -> go.Scatter:
        self.ta.add_cumulative_return()
        yield from self._line_trace(
            "cum-ret", "Return", percent_format=True, base_series=base_series, line_options=line_options
        )

    def log_return_trace(
        self, base_series: pd.Series | None = None, line_options: dict | None = None, **kwargs
    ) -> go.Scatter:
        self.ta.add_cumulative_return("log")
        yield from self._line_trace(
            "cum-log-ret", "Log-Return", percent_format=True, base_series=base_series, line_options=line_options
        )

    def drawdown_trace(
        self, base_series: pd.Series | None = None, line_options: dict | None = None, **kwargs
    ) -> go.Scatter:
        self.ta.add_drawdown()
        yield from self._line_trace("drawdown", "Drawdown", base_series=base_series, line_options=line_options)

    def candlestick_trace(self, **kwargs) -> go.Candlestick:
        yield from self._ohlc_trace(go.Candlestick)

    def ohlc_trace(self, **kwargs) -> go.Ohlc:
        yield from self._ohlc_trace(go.Ohlc)
