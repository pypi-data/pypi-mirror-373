from contextlib import suppress

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wbcore import viewsets
from wbcore.utils.date import get_date_interval_from_request

from wbfdm.analysis.financial_analysis.financial_ratio_analysis import (
    FinancialRatio,
    get_financial_ratios,
)
from wbfdm.filters import FinancialRatioFilterSet
from wbfdm.models.instruments import Instrument

from ..configs import ValuationRatioChartTitleConfig
from ..mixins import InstrumentMixin


class ValuationRatioChartViewSet(InstrumentMixin, viewsets.TimeSeriesChartViewSet):
    queryset = Instrument.objects.all()
    filterset_class = FinancialRatioFilterSet
    title_config_class = ValuationRatioChartTitleConfig

    def get_queryset(self):
        return super().get_queryset().filter(id=self.instrument.id)

    def get_plotly(self, queryset):
        pd.options.plotting.backend = "plotly"

        ratios = [FinancialRatio.PE, FinancialRatio.PS, FinancialRatio.PB, FinancialRatio.PFCF]
        ttm = False if self.request.GET.get("ttm", "true") == "false" else True
        start, end = get_date_interval_from_request(self.request, date_range_fieldname="period")

        df = get_financial_ratios(
            self.instrument.id,
            ratios,
            from_date=start,
            to_date=end,
            ttm=ttm,
        )
        fig = go.Figure()
        colors = iter(px.colors.qualitative.T10)

        for ratio, color in zip(ratios, colors):
            with suppress(AttributeError):
                series = getattr(df, ratio.value)

                fig.add_trace(
                    go.Scatter(
                        x=series.index,
                        y=series,
                        line=dict(color=color),
                        name=f"{ratio.label} {'TTM' if ttm else 'FTM'}",
                        legendgroup=f"{ratio.label} {'TTM' if ttm else 'FTM'}",
                        visible="legendonly" if ratio != FinancialRatio.PE else True,
                    ),
                )

        # fig = df.plot()
        fig.update_layout(
            template="plotly_white",
            legend=dict(x=0.02, y=0.98, bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True,
        )

        for i, d in enumerate(fig.data):
            with suppress(AttributeError, IndexError, TypeError, OverflowError):
                if (v := d.y[-1]) and not np.isnan(v):
                    fig.add_scatter(
                        x=[d.x[-1]],
                        y=[v],
                        name=d.name,
                        mode="markers+text",
                        text=round(v),
                        textfont=dict(color=d.line.color),
                        textposition="middle right",
                        marker=dict(color=d.line.color, size=12, symbol="circle"),
                        legendgroup=d.name,
                        showlegend=False,
                        visible="legendonly" if i != 0 else True,
                    )

        return fig
