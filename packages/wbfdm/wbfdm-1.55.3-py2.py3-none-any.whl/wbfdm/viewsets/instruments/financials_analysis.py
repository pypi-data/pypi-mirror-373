from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wbcore import viewsets
from wbcore.utils.date import get_date_interval_from_request

from wbfdm.figures.financials import FinancialsChartGenerator
from wbfdm.figures.financials.financial_analysis_charts import (
    FinancialAnalysisGenerator,
    PeriodChoices,
    VariableChoices,
)
from wbfdm.filters import (
    EarningsAnalysisFilterSet,
    FinancialAnalysisFilterSet,
    FinancialAnalysisValuationRatiosFilterSet,
)
from wbfdm.models import Instrument
from wbfdm.viewsets.configs import (
    CashFlowAnalysisInstrumentBarChartEndpointConfig,
    CashFlowAnalysisInstrumentBarChartTitle,
    CashFlowAnalysisInstrumentTableChartEndpointConfig,
    CashFlowAnalysisInstrumentTableChartTitle,
    EarningsInstrumentChartEndpointConfig,
    EarningsInstrumentChartTitle,
    FinancialAnalysisGeneratorTitleConfig,
    FinancialsGraphInstrumentChartEndpointConfig,
    FinancialsGraphInstrumentChartTitle,
    NetDebtAndEbitdaInstrumentChartEndpointConfig,
    NetDebtAndEbitdaInstrumentChartTitle,
    ProfitabilityRatiosInstrumentChartEndpointConfig,
    ProfitabilityRatiosInstrumentChartTitle,
    SummaryTableInstrumentChartEndpointConfig,
    SummaryTableInstrumentChartTitle,
)

from ..mixins import InstrumentMixin


class SummaryTableInstrumentChartViewSet(InstrumentMixin, viewsets.ChartViewSet):
    queryset = Instrument.objects.all()
    title_config_class = SummaryTableInstrumentChartTitle
    endpoint_config_class = SummaryTableInstrumentChartEndpointConfig
    filterset_class = FinancialAnalysisFilterSet

    def get_queryset(self):
        return Instrument.objects.filter(id=self.instrument.id)

    def get_plotly(self, queryset):
        instrument = queryset.first()
        instance_generator = FinancialsChartGenerator(instrument=instrument)
        fig = instance_generator.summary_table_chart()
        return fig


class FinancialsGraphInstrumentChartViewSet(SummaryTableInstrumentChartViewSet):
    title_config_class = FinancialsGraphInstrumentChartTitle
    endpoint_config_class = FinancialsGraphInstrumentChartEndpointConfig

    def get_plotly(self, queryset):
        instrument = queryset.first()
        instance_generator = FinancialsChartGenerator(instrument=instrument)
        fig = instance_generator.financials_chart()
        return fig


class ProfitabilityRatiosInstrumentChartViewSet(SummaryTableInstrumentChartViewSet):
    title_config_class = ProfitabilityRatiosInstrumentChartTitle
    endpoint_config_class = ProfitabilityRatiosInstrumentChartEndpointConfig

    def get_plotly(self, queryset):
        instrument = queryset.first()
        instance_generator = FinancialsChartGenerator(instrument=instrument)
        fig = instance_generator.profitability_ratios_chart()
        return fig


class CashFlowAnalysisInstrumentTableViewSet(SummaryTableInstrumentChartViewSet):
    title_config_class = CashFlowAnalysisInstrumentTableChartTitle
    endpoint_config_class = CashFlowAnalysisInstrumentTableChartEndpointConfig

    def get_plotly(self, queryset):
        instrument = queryset.first()
        instance_generator = FinancialsChartGenerator(instrument=instrument)
        fig = instance_generator.cash_flow_analysis_table_chart()
        return fig


class CashFlowAnalysisInstrumentBarChartViewSet(SummaryTableInstrumentChartViewSet):
    title_config_class = CashFlowAnalysisInstrumentBarChartTitle
    endpoint_config_class = CashFlowAnalysisInstrumentBarChartEndpointConfig

    def get_plotly(self, queryset):
        instrument = queryset.first()
        instance_generator = FinancialsChartGenerator(instrument=instrument)
        fig = instance_generator.cash_flow_analysis_bar_chart()
        return fig


class NetDebtAndEbitdaInstrumentChartViewSet(SummaryTableInstrumentChartViewSet):
    title_config_class = NetDebtAndEbitdaInstrumentChartTitle
    endpoint_config_class = NetDebtAndEbitdaInstrumentChartEndpointConfig

    def get_plotly(self, queryset):
        instrument = queryset.first()
        instance_generator = FinancialsChartGenerator(instrument=instrument)
        fig = instance_generator.net_debt_and_ebitda_chart()
        return fig


class ValuationRatiosChartView(InstrumentMixin, viewsets.ChartViewSet):
    queryset = Instrument.objects.all()
    title_config_class = FinancialAnalysisGeneratorTitleConfig
    filterset_class = FinancialAnalysisValuationRatiosFilterSet
    LIST_DOCUMENTATION = "wbfdm/markdown/documentation/financial_analysis_instrument_ratios.md"

    def get_plotly(self, queryset):
        # Set plotly as the default plotting lib
        pd.options.plotting.backend = "plotly"

        # GET data from fake filters
        date1, date2 = get_date_interval_from_request(self.request)
        if not date1 or not date2:
            return go.Figure()
        period = getattr(PeriodChoices, self.request.GET.get("period", "NTM"), PeriodChoices.NTM)
        output = self.request.GET.get("output", "CHART")
        vs_related = self.request.GET.get("vs_related", "false") == "true"
        clean_data = self.request.GET.get("clean_data", "true") == "true"
        ranges = self.request.GET.get("ranges", "false") == "true"
        range_type = self.request.GET.get("range_type", "MINMAX")
        range_period = int(self.request.GET.get("range_period", "120"))
        x_axis_var = getattr(VariableChoices, self.request.GET.get("x_axis_var", "EPSG"), VariableChoices.EPSG)
        x_axis, x_axis_title, x_axis_format = x_axis_var.lower(), x_axis_var.chart_label, x_axis_var.format
        y_axis_var = getattr(VariableChoices, self.request.GET.get("y_axis_var", "PE"), VariableChoices.PE)
        y_axis, y_axis_title, y_axis_format = y_axis_var.lower(), y_axis_var.chart_label, y_axis_var.format
        z_axis_var = getattr(VariableChoices, self.request.GET.get("z_axis_var", "MKTCAP"), VariableChoices.MKTCAP)
        z_axis, z_axis_title, z_axis_format = z_axis_var.lower(), z_axis_var.chart_label, z_axis_var.format
        median = self.request.GET.get("median", "true") == "true"

        # Fail early if filter combination doesn't make sense or the period is too large for the peer chart
        if output == "TSTABLE" and vs_related:
            fig = go.Figure()
            fig.update_layout(
                title_text="To provide the best user experience, you may not use <b>'versus related'</b> instruments in the <b>'time-series'</b> table view."
            )
            return fig

        if output == "CHART" and vs_related and ranges:
            fig = go.Figure()
            fig.update_layout(
                title_text="You may only <b>'draw ranges'</b> for a single instrument <b>('versus related' = NO)</b>."
            )
            return fig

        if output == "CHART" and vs_related and (date2 - date1).days > 900:
            fig = go.Figure()
            fig.update_layout(
                title_text="To provide the best user experience, it is possible to display <b>up to 2.5 calendar years</b> in the chart view with <b>'versus related = YES'</b>."
            )
            return fig

        if output == "CHART" and ranges and range_type == "ROLLING" and range_period < 1:
            fig = go.Figure()
            fig.update_layout(title_text="<b>Rolling period</b> cannot be lower than 1.")
            return fig

        # Get all ratios
        generator = FinancialAnalysisGenerator([self.instrument], date1, date2, vs_related)
        ratios = generator.get_common_valuation_ratios_df(period, clean_data)

        # If ratios are empty, return early
        if ratios.empty:
            fig = go.Figure()
            fig.update_layout(title_text="No data available.")
            return fig

        # Label dates
        ratios["datetxt"] = pd.to_datetime(ratios["date"]).dt.strftime("%Y-%m-%d")

        if output == FinancialAnalysisValuationRatiosFilterSet.OutputChoices.TSTABLE:
            fig = go.Figure(
                data=[
                    go.Table(
                        header=dict(
                            values=[
                                "Date",
                                "Price-to-Earnings PE " + period,
                                "Price-to-Earnings-to-Growth PEG " + period,
                                "Price-to-Sales PS " + period,
                                "EV-to-EBITDA " + period,
                                "Price-to-FreeCashflow P/FCF " + period,
                            ]
                        ),
                        cells=dict(
                            values=[
                                ratios["datetxt"],
                                ratios["pe"].astype(float).round(1).replace([np.nan], None).replace([None], ""),
                                ratios["peg"].astype(float).round(2).replace([np.nan], None).replace([None], ""),
                                ratios["ps"].astype(float).round(1).replace([np.nan], None).replace([None], ""),
                                ratios["evebitda"].astype(float).round(1).replace([np.nan], None).replace([None], ""),
                                ratios["pfcf"].astype(float).round(1).replace([np.nan], None).replace([None], ""),
                            ],
                        ),
                    ),
                ]
            )
            return fig

        elif output == FinancialAnalysisValuationRatiosFilterSet.OutputChoices.TABLE:
            ratios = ratios.groupby("instrument").tail(1)
            ratios = ratios.reset_index(drop=True)

            # If table and additional instruments, add median and mean rows
            if vs_related:
                ratios.fillna(value=np.nan, inplace=True)
                ratios_median = ratios.median(numeric_only=True, axis=0)
                ratios.loc["Mean"] = ratios.mean(numeric_only=True, axis=0)
                ratios.loc[ratios.index[-1], "instrument_title"] = "Mean"
                ratios.loc["Median"] = ratios_median
                ratios.loc[ratios.index[-1], "instrument_title"] = "Median"
                ratios.rename(index={"Mean": ratios["date"][0]}, inplace=True)
                ratios.rename(index={"Median": ratios["date"][0]}, inplace=True)
                ratios.replace(np.nan, None, inplace=True)

            # Round all variables to 1 decimal but peg
            columns = ratios.columns.difference(["instrument", "instrument_title", "peg", "date", "datetxt"])
            for col in columns:
                ratios[col] = ratios[col].astype(float).round(1).replace([np.nan], None).replace([None], "")
            ratios["peg"] = ratios["peg"].astype(float).round(2).replace([np.nan], None).replace([None], "")

            # last two lines in bold
            if vs_related:
                for i in [0, -2, -1]:
                    row = ratios.iloc[i, :].values
                    bold_row = ["<b>" + str(entry) + "</b>" for entry in row]
                    ratios.iloc[i, :] = bold_row

            return go.Figure(
                data=[
                    go.Table(
                        header=dict(
                            values=[
                                period + " on " + str(ratios["datetxt"].head(1).item()),
                                "Price-to-Earnings PE",
                                "Price-to-Earnings-to-Growth PEG",
                                "Price-to-Sales PS",
                                "EV-to-EBITDA",
                                "Price-to-FreeCashFlow P/FCF",
                            ]
                        ),
                        cells=dict(
                            values=[
                                ratios["instrument_title"],
                                ratios["pe"],
                                ratios["peg"],
                                ratios["ps"],
                                ratios["evebitda"],
                                ratios["pfcf"],
                            ],
                        ),
                    )
                ]
            )

        else:
            # Calculate custom axis ranges for better visual representation
            def axis_range(series, type="lower"):
                if type == "lower":
                    a = series.min()
                    if pd.isna(a):
                        return 0
                    if a > 0:
                        _range = 0.75 * float(str(a).replace("nan", "0"))
                    else:
                        _range = 1.25 * float(str(a).replace("nan", "-1"))
                else:
                    a = series.max()
                    if pd.isna(a):
                        return 1
                    if a > 0:
                        _range = 1.25 * float(str(a).replace("nan", "30"))
                    else:
                        _range = 0.75 * float(str(a).replace("nan", "0"))
                return _range

            if vs_related:
                # Get biweekly dates to run the loop for plotly sliders
                def daterange(start_date, end_date):
                    for n in range(1 + int((end_date - start_date).days / 14)):
                        if n == len(range(int((end_date - start_date).days / 14))):
                            yield end_date
                        yield start_date + timedelta(14 * n)

                fig = go.Figure()
                dates = []
                for index, single_date in enumerate(daterange(date1, date2)):
                    ratio_trace = ratios[
                        (ratios["datetxt"] == single_date.strftime("%Y-%m-%d")) & (ratios[z_axis] > 0)
                    ]
                    if (
                        not ratio_trace.empty
                        and not all(v is None for v in ratio_trace[x_axis])
                        and not all(v is None for v in ratio_trace[y_axis])
                    ):
                        dates.append(single_date.strftime("%Y-%m-%d"))
                        ratio_main = ratio_trace.head(1)
                        ratio_other = ratio_trace.iloc[1:]
                        fig.add_trace(
                            go.Scatter(
                                visible=False,
                                x=ratio_main[x_axis],
                                y=ratio_main[y_axis],
                                customdata=np.stack((ratio_main["instrument_title"], ratio_main[x_axis]), axis=-1),
                                mode="markers",
                                marker=dict(
                                    color="green",
                                    opacity=0.5,
                                    size=ratio_main[z_axis].astype(float),
                                    sizeref=(2.0 * np.nanmax(ratios[z_axis].fillna(0))) / (20.0**2),
                                ),
                                hovertemplate="<br>".join(
                                    [
                                        s.replace(" ", "&nbsp;")
                                        for s in [
                                            "<b>%{customdata[0]}</b>",
                                            "X:          <b>" + x_axis_title + ":</b>    %{x:" + str(x_axis_format),
                                            "Y:          <b>" + y_axis_title + ":</b>    %{y:" + str(y_axis_format),
                                            "Bubble: <b>"
                                            + z_axis_title
                                            + ":</b>    %{marker.size:"
                                            + str(z_axis_format)
                                            + "<extra></extra>",
                                        ]
                                    ]
                                ),
                            )
                        )
                        colors = px.colors.qualitative.Pastel
                        fig.add_trace(
                            go.Scatter(
                                visible=False,
                                name="Ratios: " + str(ratio_trace["datetxt"]),
                                x=ratio_other[x_axis],
                                y=ratio_other[y_axis],
                                customdata=np.stack((ratio_other["instrument_title"], ratio_other[x_axis]), axis=-1),
                                mode="markers",
                                marker=dict(
                                    color=colors[0 : len(ratio_other["instrument_title"])],
                                    opacity=0.5,
                                    size=ratio_other[z_axis].astype(float),
                                    sizeref=(2.0 * np.nanmax(ratios[z_axis].fillna(0))) / (20.0**2),
                                ),
                                hovertemplate="<br>".join(
                                    [
                                        s.replace(" ", "&nbsp;")
                                        for s in [
                                            "<b>%{customdata[0]}</b>",
                                            "X:          <b>" + x_axis_title + ":</b>    %{x:" + str(x_axis_format),
                                            "Y:          <b>" + y_axis_title + ":</b>    %{y:" + str(y_axis_format),
                                            "Bubble: <b>"
                                            + z_axis_title
                                            + ":</b>    %{marker.size:"
                                            + str(z_axis_format)
                                            + "<extra></extra>",
                                        ]
                                    ]
                                ),
                            )
                        )
                        fig.update_layout(title_text="Relative Valuation <b>" + period + "</b>", showlegend=False)
                        fig.update_xaxes(
                            title_text=x_axis_title + " <b>" + period + "</b>",
                            hoverformat=x_axis_format,
                            tickformat=x_axis_format.split("}")[0],
                            range=[axis_range(ratios[x_axis], type="lower"), axis_range(ratios[x_axis], type="upper")],
                        )
                        fig.update_yaxes(
                            title_text=y_axis_title + " <b>" + period + "</b>",
                            hoverformat=y_axis_title,
                            tickformat=y_axis_format.split("}")[0],
                            range=[axis_range(ratios[y_axis], type="lower"), axis_range(ratios[y_axis], type="upper")],
                        )
                        fig.add_hline(y=0, line_width=0.15, line_color="grey")
                        fig.add_vline(x=0, line_width=0.15, line_color="grey")
                        if median:
                            fig.add_hline(y=ratios[y_axis].median(), line_width=1, line_dash="dash", line_color="grey")
                            fig.add_vline(x=ratios[x_axis].median(), line_width=1, line_dash="dash", line_color="grey")

                if len(dates) == 0:
                    fig.update_layout(title_text="No data available.")
                    return fig
                else:
                    steps = []
                    for i in range(len(dates)):
                        step = dict(
                            method="update",
                            args=[
                                {"visible": [False] * len(dates) * 2},
                                {"name": "Relative Valuation <b>" + period + "</b>. Chosen date: " + str(dates[i])},
                            ],
                        )
                        step["args"][0]["visible"][i * 2] = True
                        step["args"][0]["visible"][(i * 2) + 1] = True
                        steps.append(step)

                    sliders = [
                        dict(active=len(dates) - 1, currentvalue={"prefix": "Date: "}, pad={"t": 50}, steps=steps)
                    ]

                    fig.data[-1].visible = True
                    fig.data[-2].visible = True

                    fig.update_layout(sliders=sliders)

                    for i in range(len(dates)):
                        fig["layout"]["sliders"][0]["steps"][i]["label"] = str(dates[i])

                    return fig

            if not ranges:
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                for index, plot in enumerate(
                    [
                        ("pe", "#ff6361", VariableChoices.PE.chart_label, VariableChoices.PE, False),
                        ("peg", "#ffa600", VariableChoices.PEG.chart_label, VariableChoices.PEG, True),
                        ("ps", "#58508d", VariableChoices.PS.chart_label, VariableChoices.PS, False),
                        ("evebitda", "#003f5c", VariableChoices.EVEBITDA.chart_label, VariableChoices.EVEBITDA, False),
                        ("pfcf", "#bc5090", VariableChoices.PFCF.chart_label, VariableChoices.PFCF, False),
                    ],
                    start=1,
                ):
                    fig.add_trace(
                        go.Scatter(
                            x=ratios["date"],
                            y=ratios[plot[0]],
                            line=dict(color=plot[1], width=2),
                            name=plot[2] + " " + period,
                            hovertemplate="%{x}: <b>" + plot[3] + " " + period + "</b> %{y} <extra></extra>",
                        ),
                        secondary_y=plot[4],
                    )

                fig.update_layout(title_text="Relative Valuation " + period, yaxis_ticksuffix="x")
                fig.update_yaxes(title_text="Ratios " + period, hoverformat=".2f", secondary_y=False)
                if abs(axis_range(ratios["peg"], type="upper")) >= 1:
                    ticks = ".1f"
                else:
                    ticks = ".2f"
                fig.update_yaxes(
                    title_text="PEG " + period,
                    hoverformat=".2f",
                    tickformat=ticks,
                    title_font_color="#ffa600",
                    secondary_y=True,
                )
                fig.update_yaxes(
                    rangemode="tozero", scaleanchor="y2", scaleratio=0.1, constraintoward="bottom", secondary_y=False
                )
                fig.update_yaxes(
                    rangemode="tozero", scaleanchor="y", scaleratio=1, constraintoward="bottom", secondary_y=True
                )
                fig.add_hline(y=0, line_width=3, line_dash="dash", line_color="grey")
                fig["layout"]["yaxis2"]["showgrid"] = False
                return fig

            fig = make_subplots(rows=5, cols=1, vertical_spacing=0.01, shared_xaxes=True)
            x_range = [ratios["date"].iloc[0], ratios["date"].iloc[-1]]

            for index, plot in enumerate(
                [
                    ("pe", "#ff6361"),
                    ("peg", "#ffa600"),
                    ("ps", "#58508d"),
                    ("evebitda", "#003f5c"),
                    ("pfcf", "#bc5090"),
                ],
                start=1,
            ):
                fig.add_trace(
                    go.Scatter(x=ratios["date"], y=ratios[plot[0]], line=dict(color=plot[1], width=2)),
                    row=index,
                    col=1,
                )
                if range_type == FinancialAnalysisValuationRatiosFilterSet.RangeChoices.MINMAX:
                    if not ratios[plot[0]].isnull().all():
                        fig.add_trace(
                            go.Scatter(
                                x=x_range,
                                y=[ratios[plot[0]].max(), ratios[plot[0]].max()],
                                mode="lines",
                                line_width=1,
                                line_dash="dash",
                                line_color=plot[1],
                            ),
                            row=index,
                            col=1,
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=x_range,
                                y=[ratios[plot[0]].min(), ratios[plot[0]].min()],
                                mode="lines",
                                line_width=1,
                                line_dash="dash",
                                line_color=plot[1],
                            ),
                            row=index,
                            col=1,
                        )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=ratios["date"],
                            y=ratios[plot[0]].rolling(range_period, min_periods=1).max().fillna(""),
                            mode="lines",
                            line_width=0.75,
                            line_dash="dash",
                            line_color=plot[1],
                        ),
                        row=index,
                        col=1,
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=ratios["date"],
                            y=ratios[plot[0]].rolling(range_period, min_periods=1).min().fillna(""),
                            mode="lines",
                            line_width=0.75,
                            line_dash="dash",
                            line_color=plot[1],
                        ),
                        row=index,
                        col=1,
                    )

            fig.update_layout(
                yaxis=dict(title_text="P/E", ticksuffix="x", hoverformat=".1f"),
                yaxis2=dict(title_text="PEG", tickformat=".1f", hoverformat=".1f"),
                yaxis3=dict(title_text="P/S", ticksuffix="x", hoverformat=".1f"),
                yaxis4=dict(title_text="EV/EBITDA", ticksuffix="x", hoverformat=".1f"),
                yaxis5=dict(title_text="P/FCF", ticksuffix="x", hoverformat=".1f"),
            )

            fig.update_traces(hovertemplate="%{x}: %{y} <extra></extra>")

            if range_type == FinancialAnalysisValuationRatiosFilterSet.RangeChoices.MINMAX:
                fig.update_layout(
                    title_text=period + " Valuation ratios with Min/Max range", title_x=0, showlegend=False
                )
            else:
                fig.update_layout(
                    title_text=period + " Valuation ratios with " + str(range_period) + " days rolling min-max range",
                    title_x=0,
                    showlegend=False,
                )

            return fig


class EarningsInstrumentChartViewSet(InstrumentMixin, viewsets.ChartViewSet):
    title_config_class = EarningsInstrumentChartTitle
    endpoint_config_class = EarningsInstrumentChartEndpointConfig
    queryset = Instrument.objects.all()
    filterset_class = EarningsAnalysisFilterSet
    LIST_DOCUMENTATION = "wbfdm/markdown/documentation/earnings_instrument.md"

    def get_plotly(self, queryset):
        # GET data from fake filters
        date1, date2 = get_date_interval_from_request(self.request)
        if not date1 or not date2:
            return go.Figure()
        period = getattr(PeriodChoices, self.request.GET.get("period", "NTM"), PeriodChoices.NTM)
        analysis = self.request.GET.get("output", "EPS")
        vs_related = self.request.GET.get("vs_related", "false") == "true"

        # Get all earnings data
        generator = FinancialAnalysisGenerator([self.instrument], date1, date2, vs_related)
        earnings = generator.get_earnings_df(period, clean_data=True)

        # If earnings are empty, return early
        if earnings.empty:
            fig = go.Figure()
            fig.update_layout(title_text="No data available.")
            return fig

        if period == PeriodChoices.TTM:
            hover_helper = " EPS "
            title_helper = "Reported Earnings "
        else:
            hover_helper = " Consensus EPS "
            title_helper = "Consensus Earnings Estimates "

        fig = go.Figure()
        earnings = earnings.set_index(["instrument", "instrument_title", "date"]).unstack(level=1)
        earnings = earnings.reset_index().drop("instrument", axis=1).replace(np.nan, None).set_index("date")
        if analysis == "EPS":
            for col in earnings.columns:
                fig.add_trace(
                    go.Scatter(
                        x=earnings.index,
                        y=earnings[col],
                        name=col[1],
                        hovertemplate="%{x}: <b>" + col[1] + hover_helper + period + "</b> %{y} <extra></extra>",
                    ),
                )

            fig.update_layout(title_text=title_helper + period, yaxis_tickprefix="$")
            fig.update_yaxes(title_text="EPS ($) " + period, hoverformat=".2f", tickformat=".2f")

        return fig
