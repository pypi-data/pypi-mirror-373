import datetime as dt
import math
import re
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from django.db.models import ExpressionWrapper, F, FloatField, QuerySet
from pandas.tseries.offsets import BYearEnd
from plotly.subplots import make_subplots
from wbcore.contrib.currency.models import CurrencyFXRates

from wbfdm.enums import MarketData
from wbfdm.models import Instrument, InstrumentPrice


class FinancialsChartGenerator:
    def __init__(self, instrument: Instrument):
        self.instrument = instrument

    def _make_presentable_fields(self, fields_list: list, bold: bool = True) -> pd.Index:
        full_capitalize_fields = self.get_full_capitalize_fields()
        percent_fields = self.get_percent_fields()
        finance_friendly = self._rename_fields_into_finance_friendly()
        pattern = re.compile(r"\b(" + "|".join(finance_friendly.keys()) + r")\b")

        for i, x in enumerate(fields_list):
            y = pattern.sub(lambda z: finance_friendly[z.group()], x)
            if x in percent_fields:
                x = y + "_(%)"
            else:
                x = y
            fields_list[i] = x

        fields_list = [x.split("_") for x in fields_list]
        for i, primary_list in enumerate(fields_list):
            for j, word in enumerate(primary_list):
                primary_list[j] = word.upper() if word in full_capitalize_fields else word.capitalize()

            fields_list[i] = " ".join(primary_list)
        fields_list = [f"<b>{x}</b>" for x in fields_list] if bold else fields_list
        return pd.Index(fields_list)

    def _make_pretty_table(self, df: pd.DataFrame) -> go.Figure:
        previous_years = [elem for elem in df.columns if elem.find("E") == -1]
        big_int_fields = self.get_big_int_fields()
        percent_fields = self.get_percent_fields()
        multiples_fields = self.get_multiples_fields()
        big_int_fields = df.index.intersection(big_int_fields)
        percent_fields = df.index.intersection(percent_fields)
        multiples_fields = df.index.intersection(multiples_fields)
        other_fields = df.index.difference(big_int_fields.append(percent_fields).append(multiples_fields))
        df.loc[big_int_fields] = (
            df.loc[big_int_fields].div(1000000).applymap(lambda x: f"{x:,.0f}" if not np.isnan(x) else "")
        )
        df.loc[percent_fields] = df.loc[percent_fields].applymap(lambda x: f"{x:,.1%}" if not np.isnan(x) else "")
        df.loc[multiples_fields] = df.loc[multiples_fields].applymap(lambda x: f"{x:,.1f}x" if not np.isnan(x) else "")
        df.loc[other_fields] = df.loc[other_fields].applymap(lambda x: f"{x:,.2f}" if not np.isnan(x) else "")
        df.insert(
            0,
            f"{self.instrument.name_repr} in USD mn",
            self._make_presentable_fields(fields_list=df.index.tolist()),
        )
        df_table = df.reset_index().drop("index", axis=1)
        df_table.columns = df_table.columns.map("<b>{}</b>".format)
        colors = ["white", "#EEEEF1"] * math.floor(len(df_table.index) / 2)
        colors += ["white"] if len(df_table.index) % 2 == 1 else ""
        fig = go.Figure(
            go.Table(
                columnwidth=[3] + [1] * len(df_table.columns),
                header=dict(
                    values=df_table.columns.tolist(),
                    line_color="darkslategray",
                    fill_color="grey",
                    font=dict(color="white", size=13),
                    align=["left", "center"],
                    height=40,
                ),
                cells=dict(
                    values=df.T.values.tolist(),
                    align=["left", "center"],
                    line_color="darkslategray",
                    fill_color=["lightgrey"] + [colors] * len(previous_years) + ["lightyellow"],
                    height=30,
                ),
            ),
        )
        return fig

    @staticmethod
    def _rename_fields_into_finance_friendly() -> dict:
        return {
            "gross_profit_margin": "gross_profit_margin_[non-gaap]",
            "ebitda_margin": "ebitda_margin_[non-gaap]",
            "net_profit_margin": "net_profit_margin_[gaap]",
            "net_profit": "net_profit_[non-gaap]",
            "reported_net_profit": "net_profit_[gaap]",
            "eps": "eps_[non-gaap]",
            "eps_growth": "eps_growth_[non-gaap]",
        }

    @staticmethod
    def get_big_int_fields() -> list[str]:
        return [
            "revenue",
            "cost_of_good_sold",
            "gross_profit",
            "ebitda",
            "ebit",
            "net_profit",
            "reported_net_profit",
            "cost_research_development",
            "sga",
            "free_cash_flow",
            "cash_from_operation",
            "working_capital",
            "capital_expenditures",
            "investment_cash",
            "financing_cash",
            "shareholder_equity",
            "total_assets",
            "current_liabilities",
            "total_debt",
            "cash_and_cash_equivalents",
            "net_debt",
            "cash_and_short_term_investments",
            "net_change_in_cash",
            "receivables",
            "inventories",
            "payables",
            "current_assets",
            "entreprise_value",
            "free_cash",
            "burn_rate",
            "operating_burn_rate",
            "free_cash_burn_rate",
            "operating_cash_flow",
            "investing_cash_flow",
            "unlevered_free_cash_flow",
        ]

    @staticmethod
    def get_percent_fields() -> list[str]:
        return [
            "revenue_growth",
            "revenue_growth_5y_cagr",
            "gross_profit_margin",
            "ebitda_margin",
            "ebit_margin",
            "net_profit_margin",
            "free_cash_flow_growth",
            "return_on_equity",
            "return_on_assets",
            "return_on_capital_employed",
            "operating_cash_flow_growth",
            "investing_cash_flow_growth",
            "unlevered_free_cash_flow_growth",
            "unlevered_free_cash_flow_margin",
            "diluted_eps_growth",
            "eps_growth",
        ]

    @staticmethod
    def get_full_capitalize_fields() -> list[str]:
        return ["ebitda", "ebit", "eps", "sga", "ytd", "[gaap]", "[non-gaap]"]

    @staticmethod
    def get_multiples_fields() -> list[str]:
        return ["net_debt_to_ebitda_ratio"]

    def get_latest_year(self, queryset: Optional[QuerySet] = None) -> int:
        # if queryset is None:
        #     fundamentals = Fundamental.annual_objects.filter(instrument=self.instrument)  # noqa
        #     if fundamentals.exists():
        #         return fundamentals.latest("period__date_range").period.period_year
        # elif queryset.exists():  # not empty
        #     return queryset.latest("period__date_range").period.period_year

        return dt.date.today().year - 1  # if no data provided, take last previous year

    def fundamentals_df(self, from_n_years_before: int = 3) -> pd.DataFrame:
        return pd.DataFrame()
        # fundamentals_fields_list = Fundamental.get_number_serializer_fields().keys()  # noqa
        # qs_fundamentals = Fundamental.annual_objects.filter(instrument=self.instrument)  # noqa
        # latest_year = self.get_latest_year(queryset=qs_fundamentals)
        # qs_fundamentals = (
        #     qs_fundamentals.filter(
        #         period__period_year__gte=latest_year - from_n_years_before,
        #         period__period_year__lte=latest_year,
        #     )
        #     .order_by("period__period_year")
        #     .values(*Fundamental.get_number_serializer_fields().keys(), "period__period_year")  # noqa
        # )
        # df_fundamentals = pd.DataFrame(qs_fundamentals)
        # if not df_fundamentals.empty:
        #     df_fundamentals["period__period_year"] = df_fundamentals.period__period_year.astype(str)
        #     df_fundamentals = df_fundamentals.set_index("period__period_year")[fundamentals_fields_list].T
        #     return df_fundamentals
        # return df_fundamentals.reindex(fundamentals_fields_list)

    def forecasts_df(self) -> pd.DataFrame:
        return pd.DataFrame()
        # forecasts_fields_list = list(Forecast.get_number_serializer_fields().keys())  # noqa
        # latest_year = self.get_latest_year(queryset=None)
        # forecasts = self.instrument.forecasts.filter(revenue_y1__isnull=False)
        # if forecasts.exists():
        #     last_forecast = forecasts.latest("date")
        #     df_forecasts = pd.DataFrame.from_dict(model_to_dict(last_forecast), orient="index").T[
        #         forecasts_fields_list
        #     ]
        # else:
        #     df_forecasts = pd.DataFrame(index=forecasts_fields_list)
        # forecasts_fields_list += ["reported_net_profit"]
        #
        # def split_year_fields(_year_n: str) -> list:
        #     return [field for field in forecasts_fields_list if field.find(_year_n) != -1]
        #
        # next_years = list(str(year) + "E" for year in range(latest_year + 1, latest_year + 6))
        # df_forecasts_ordered = pd.DataFrame(index=forecasts_fields_list)
        #
        # if forecasts.exists():
        #     for year, e_year in zip(["_y1", "_y2", "_y3", "_y4", "_y5"], next_years):
        #         year_fields = split_year_fields(_year_n=year)
        #         index = list(map(lambda x: x.replace(year, ""), year_fields))
        #         tmp = pd.DataFrame(index=[e_year], columns=index, data=df_forecasts[year_fields].values.tolist()).T
        #         df_forecasts_ordered = pd.concat([df_forecasts_ordered, tmp], axis=1)
        # return df_forecasts_ordered

    def combine_fundamentals_and_forecasts_df(self) -> pd.DataFrame:
        df_fundamentals = self.fundamentals_df()
        df_forecasts = self.forecasts_df()

        # Hardcode rename for those which do not have same field name:
        df_forecasts.rename(index={"adjusted_net_profit": "net_profit"}, inplace=True)

        df_table = pd.concat([df_fundamentals, df_forecasts], axis=1).astype(float)

        return df_table

    def get_instrument_price_data(
        self,
        from_date: dt.date | None = None,
        to_date: dt.date | None = None,
    ) -> pd.DataFrame:
        if not from_date:
            from_date = dt.date(dt.date.today().year - 1, 1, 1)

        df_prices = pd.DataFrame(
            Instrument.objects.filter(id=self.instrument.id).dl.market_data(
                values=[MarketData.CLOSE, MarketData.OPEN, MarketData.LOW, MarketData.HIGH, MarketData.VOLUME],
                from_date=from_date,
                to_date=to_date,
            )
        )
        if df_prices.empty:
            return pd.DataFrame()
        df_prices = df_prices[
            [
                MarketData.CLOSE.value,
                MarketData.OPEN.value,
                MarketData.LOW.value,
                MarketData.HIGH.value,
                MarketData.VOLUME.value,
                "valuation_date",
            ]
        ].rename(columns={"valuation_date": "date"})
        df_prices = df_prices.set_index("date").sort_index().astype(float)
        timeline = pd.date_range(df_prices.index[0], df_prices.index[-1])
        df_prices = df_prices.reindex(timeline, method="ffill")
        return df_prices[df_prices["close"] != 0]

    def summary_table_chart(self) -> go.Figure:
        df_table = self.combine_fundamentals_and_forecasts_df()

        if not df_table.empty:
            df_table.loc["reported_net_profit", :].replace([np.nan, np.inf, -np.inf], None, inplace=True)
            df_table = df_table.loc[
                [
                    "revenue",
                    "revenue_growth",
                    "gross_profit_margin",
                    "ebitda_margin",
                    "reported_net_profit",
                    "net_profit_margin",
                    "net_profit",
                    "eps",
                    "return_on_equity",
                    "return_on_assets",
                    "return_on_capital_employed",
                    "return_on_invested_capital",
                    "net_debt_to_ebitda_ratio",
                    "interest_coverage_ratio",
                    "employee_count",
                    "employee_count_growth",
                ],
                :,
            ]
            df_table.loc["eps_growth", :] = df_table.loc["eps", :].pct_change()
            df_table = df_table.reindex(
                [
                    "revenue",
                    "revenue_growth",
                    "gross_profit_margin",
                    "ebitda_margin",
                    "reported_net_profit",
                    "net_profit_margin",
                    "net_profit",
                    "eps",
                    "eps_growth",
                    "return_on_equity",
                    "return_on_assets",
                    "return_on_capital_employed",
                    "return_on_invested_capital",
                    "net_debt_to_ebitda_ratio",
                    "interest_coverage_ratio",
                    "employee_count",
                    "employee_count_growth",
                ]
            )

        fig = self._make_pretty_table(df=df_table)
        return fig

    @staticmethod
    def replace_hovertemplate(fig: go.Figure, i_position: int, text: str) -> go.Figure:
        try:
            fig["data"][i_position]["hovertemplate"] = text
        except IndexError:
            pass
        return fig

    def financials_chart(self) -> go.Figure:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        df_table = self.combine_fundamentals_and_forecasts_df()
        if not df_table.empty:
            df_table = df_table.loc[["revenue", "net_profit", "ebitda_margin", "net_profit_margin"], :]

            for variable in ["revenue", "net_profit"]:
                text = "Revenue" if variable == "revenue" else "Net Profit"
                fig.add_bar(
                    y=df_table.loc[variable, :].dropna().div(1000000).round(2).values,
                    x=df_table.loc[variable, :].dropna().index,
                    name="Revenue" if variable == "revenue" else "Net Profit",
                    yaxis="y",
                    hovertemplate="<b>" + text + "</b><br>%{x}<br>%{y:.2f} Mio.<extra></extra>",
                )
            for variable in ["ebitda_margin", "net_profit_margin"]:
                text = "EBITDA Margin" if variable == "ebitda_margin" else "Net Profit Margin"
                fig.add_scatter(
                    y=df_table.loc[variable, :].dropna().mul(100).values,
                    x=df_table.loc[variable, :].dropna().index,
                    name=text,
                    yaxis="y2",
                    hovertemplate="<b>" + text + "</b><br>%{x}<br>%{y:.2f}%<extra></extra>",
                )
        fig.update_xaxes(nticks=len(df_table.columns))
        symbol = self.instrument.currency.symbol
        fig.update_yaxes(title=f"{symbol if symbol else ''} in Million", secondary_y=False)
        fig.update_yaxes(ticksuffix="%", secondary_y=True)
        return fig

    def profitability_ratios_chart(self) -> go.Figure:
        df_table = self.combine_fundamentals_and_forecasts_df()
        if not df_table.empty:
            df_table = df_table.loc[
                ["return_on_equity", "return_on_assets", "return_on_capital_employed", "return_on_invested_capital"]
            ]

            df_table.rename(
                index={
                    "return_on_equity": "ROE",
                    "return_on_assets": "ROA",
                    "return_on_capital_employed": "ROCE",
                    "return_on_invested_capital": "ROIC",
                },
                inplace=True,
            )
        fig = go.Figure()
        for index_name in df_table.index:
            fig.add_trace(
                go.Scatter(
                    x=df_table.loc[index_name, :].dropna().index,
                    y=df_table.loc[index_name, :].mul(100).dropna().values,
                    mode="lines+markers",
                    name=index_name,
                    hovertemplate=f"<b>{index_name}</b>" + "<br>%{y:.2f}%<extra></extra>",
                )
            )
        fig.update_yaxes(ticksuffix="%")
        fig.update_layout(hovermode="x")
        return fig

    def stock_performance_summary_chart(self) -> go.Figure:
        df_prices = self.get_instrument_price_data()
        if df_prices.empty:
            return go.Figure()
        last_day = df_prices.index[-1]
        last_year_idx = df_prices.index.get_indexer([(last_day - relativedelta(years=1))], method="nearest")[
            0
        ]  # one year from last price date
        last_month_idx = df_prices.index.get_indexer([(last_day - relativedelta(months=1))], method="nearest")[0]
        three_months_idx = df_prices.index.get_indexer([(last_day - relativedelta(months=3))], method="nearest")[0]
        six_months_idx = df_prices.index.get_indexer([(last_day - relativedelta(months=6))], method="nearest")[0]
        ytd_idx = df_prices.index.get_indexer([(last_day - BYearEnd())], method="nearest")[0]
        performances = pd.Series(name="performance", dtype=float)

        performances["1_month"] = df_prices.iloc[-1]["close"] / df_prices.iloc[last_month_idx]["close"] - 1
        performances["3_months"] = df_prices.iloc[-1]["close"] / df_prices.iloc[three_months_idx]["close"] - 1
        performances["6_months"] = df_prices.iloc[-1]["close"] / df_prices.iloc[six_months_idx]["close"] - 1
        performances["12_months"] = df_prices.iloc[-1]["close"] / df_prices.iloc[last_year_idx]["close"] - 1
        performances["ytd"] = df_prices.iloc[-1]["close"] / df_prices.iloc[ytd_idx]["close"] - 1
        if df_prices.index[ytd_idx] > df_prices.index[last_month_idx]:
            performances = performances.reindex(["ytd", "1_month", "3_months", "6_months", "12_months"])
        elif df_prices.index[ytd_idx] > df_prices.index[three_months_idx]:
            performances = performances.reindex(["1_month", "ytd", "3_months", "6_months", "12_months"])
        elif df_prices.index[ytd_idx] > df_prices.index[six_months_idx]:
            performances = performances.reindex(["1_month", "3_months", "ytd", "6_months", "12_months"])
        else:
            performances = performances.reindex(["1_month", "3_months", "6_months", "ytd", "12_months"])
        colors = performances.copy()
        colors.loc[performances >= 0], colors.loc[performances < 0] = "green", "darkred"

        performances = performances.mul(100).round(2)
        fig = go.Figure(
            go.Bar(
                x=self._make_presentable_fields(fields_list=performances.index.tolist(), bold=False),
                y=performances.values,
                texttemplate="%{y:.2f}%",
                marker={"color": colors},
            )
        )
        fig.update_yaxes(ticksuffix="%")
        fig.update_layout(title=f'Last Price Date: {last_day.strftime("%Y-%m-%d")}')
        return fig

    def price_and_volume_chart(
        self,
        from_date: dt.date | None = None,
        to_date: dt.date | None = None,
        benchmarks: Optional[list[str]] = None,
        normalize: bool = False,
        short_sma: Optional[int] = 50,
        long_sma: Optional[int] = 200,
        candle_chart: bool = False,
        overlay_volume: bool = False,
    ) -> go.Figure:
        pd.options.plotting.backend = "plotly"
        df_prices = self.get_instrument_price_data(from_date=from_date, to_date=to_date).sort_index()
        if df_prices.empty:
            return go.Figure()

        df_prices = df_prices.asfreq("B")
        df_prices["short_sma"] = df_prices.close.rolling(short_sma).mean() if short_sma else pd.NA
        df_prices["long_sma"] = df_prices.close.rolling(long_sma).mean() if long_sma else pd.NA
        df_prices["volume_diff"] = df_prices.volume.diff()
        df_prices = df_prices.loc[from_date:to_date]

        bar_chart_name = "Volume"
        df_prices["color_volume"] = "green"
        if self.instrument.is_managed:
            bar_chart_name = "Inflow/Outflow"
            df_prices.loc[df_prices.volume < 0, "color_volume"] = "red"
        else:
            perf = df_prices.close.pct_change()
            df_prices.loc[perf < 0, "color_volume"] = "red"
        if overlay_volume:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
        else:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.7])
        if not candle_chart:
            instrument_prices = df_prices.loc[:, "close"].dropna()
            cumulative_returns = instrument_prices.pct_change().add(1).cumprod().sub(1).mul(100).fillna(0)
            subfig1 = go.Scatter(
                x=instrument_prices.round(2).index,
                y=instrument_prices.round(2).values,
                mode="lines",
                name=f"{self.instrument.name_repr} - Close Price",
                customdata=cumulative_returns,
                hovertemplate=(
                    f"<b>{self.instrument.name_repr} - Close Price</b>"
                    + "<br>%{x}<br>%{y}<br><i>Cumulative Return</i>: %{customdata:.2f}%<extra></extra>"
                ),
                fill="tozeroy",
                fillcolor="rgba(0,0,255,0.15)",
            )
        else:
            subfig1 = go.Candlestick(
                x=df_prices.index,
                open=df_prices["open"].dropna(),
                high=df_prices["high"].dropna(),
                low=df_prices["low"].dropna(),
                close=df_prices["close"].dropna(),
                name=f"{self.instrument.name_repr}",
            )

        fig.add_trace(subfig1, row=1, col=1) if not overlay_volume else fig.add_trace(subfig1, secondary_y=False)

        for sma in ["short_sma", "long_sma"]:
            name_str = f"Short SMA ({short_sma} days)" if sma == "short_sma" else f"Long SMA ({long_sma} days)"
            sma_fig = go.Scatter(
                x=df_prices.loc[:, sma].dropna().round(2).index,
                y=df_prices.loc[:, sma].dropna().round(2).values,
                mode="lines",
                name=name_str,
                hovertemplate=f"<b>{name_str}</b>" + "<br>%{x}<br>%{y}<extra></extra>",
            )
            fig.add_trace(sma_fig, row=1, col=1) if not overlay_volume else fig.add_trace(sma_fig, secondary_y=False)

        benchmarks = [] if not benchmarks else benchmarks
        qs_benchmarks = (
            InstrumentPrice.objects.filter(
                instrument__in=benchmarks,
                date__range=[from_date, to_date],
                calculated=False,
            )
            .order_by("date", "instrument")
            .annotate(
                fx_rate=CurrencyFXRates.get_fx_rates_subquery_for_two_currencies(
                    "date", "instrument__currency", self.instrument.currency
                ),
                convert_value=ExpressionWrapper(F("net_value") * F("fx_rate"), output_field=FloatField()),
            )
            .values("date", "instrument__name_repr", "convert_value")
        )
        if qs_benchmarks.exists():
            df_benchmarks = pd.DataFrame(qs_benchmarks).set_index(["date", "instrument__name_repr"])
            df_benchmarks = df_benchmarks.convert_value.unstack("instrument__name_repr").astype(float).asfreq("B")
            for benchmark in df_benchmarks.columns:
                df_benchmark = df_benchmarks.loc[:, benchmark].dropna()
                benchmark_cumulative_returns = df_benchmark.pct_change().add(1).cumprod().sub(1).mul(100).fillna(0)
                if normalize and df_prices.index[0] and df_prices.index[0] <= df_benchmark.index[0]:
                    mul_factor = df_prices.loc[df_benchmark.index[0], "close"] / df_benchmark.iat[0]
                    df_benchmark *= mul_factor
                benchmark_fig = go.Scatter(
                    x=df_benchmark.index,
                    y=df_benchmark.round(2).values,
                    mode="lines",
                    name=benchmark,
                    customdata=benchmark_cumulative_returns,
                    hovertemplate=(
                        f"<b>{benchmark}</b>"
                        + "<br>%{x}<br>%{y}<br><i>Cumulative Return</i>: %{customdata:.2f}%<extra></extra>"
                    ),
                )
                (
                    fig.add_trace(benchmark_fig, row=1, col=1)
                    if not overlay_volume
                    else fig.add_trace(benchmark_fig, secondary_y=False)
                )
        subfig2 = go.Bar(
            x=df_prices.loc[:, "close"].dropna().round(2).index,
            y=df_prices.loc[:, "volume"].dropna().round(2).values,
            marker={"color": df_prices.color_volume, "opacity": 0.4},
            name=bar_chart_name,
            hovertemplate="<b>" + bar_chart_name + "</b><br>%{x}<br>%{y:.4s}<extra></extra>",
        )
        fig.add_trace(subfig2, row=2, col=1) if not overlay_volume else fig.add_trace(subfig2, secondary_y=True)

        symbol = self.instrument.currency.symbol
        if overlay_volume:
            fig.update_yaxes(ticksuffix=symbol if symbol else "", title="Price", secondary_y=False)
            fig.update_yaxes(tickformat=".3s", title="Volume", showgrid=False, secondary_y=True)
        else:
            fig.update_yaxes(ticksuffix=symbol if symbol else "", title="Price", row=1, col=1)
            fig.update_yaxes(tickformat=".3s", title="Volume", row=2, col=1)
        fig.update_yaxes(spikesnap="cursor")
        fig.update_xaxes(spikesnap="cursor")
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(showlegend=False)
        fig.update_layout(yaxis=dict(range=[df_prices.close.min(), df_prices.close.max()]))
        return fig

    def instrument_vs_benchmark_prices_chart(
        self,
        benchmark: Optional[Instrument] = None,
        from_date: dt.date | None = None,
        to_date: dt.date | None = None,
    ) -> go.Figure:
        df_prices = self.get_instrument_price_data(from_date=from_date, to_date=to_date)
        if df_prices.empty:
            return go.Figure()
        pd.options.plotting.backend = "plotly"
        df_prices = df_prices.asfreq("B").close.to_frame()
        df_prices = df_prices.loc[from_date:to_date]
        if benchmark and (benchmark_prices := benchmark.prices.filter(date__gte=from_date, date__lte=to_date)):
            df_benchmark_prices = pd.DataFrame(benchmark_prices.values("date", "close"))
            df_benchmark_prices = (
                df_benchmark_prices.set_index("date").rename(columns={"close": benchmark.name_repr}).astype(float)
            )
            df_prices = df_prices.join(df_benchmark_prices)
        instrument_name = self.instrument.name_repr
        df_prices = df_prices.rename(columns={"close": instrument_name})
        df_prices = df_prices.pct_change().add(1).cumprod().sub(1).fillna(0)
        fig = df_prices[f"{instrument_name}"].mul(100).plot.line()
        fig.update_traces(
            hovertemplate=f"<b>{instrument_name}</b>" + "<br>%{y:.2f}%<extra></extra>",
        )
        if benchmark and df_prices.columns.isin([f"{benchmark.name_repr}"]).any():
            fig.add_trace(
                go.Scatter(
                    x=df_prices.loc[:, benchmark.name_repr].dropna().index,
                    y=df_prices.loc[:, benchmark.name_repr].mul(100).dropna().values,
                    mode="lines",
                    name=benchmark.name_repr,
                    hovertemplate=f"<b>{benchmark.name_repr}</b>" + "<br>%{y:.2f}%<extra></extra>",
                )
            )
        fig.update_yaxes(title=None, ticksuffix="%")
        fig.update_xaxes(title="Time")
        fig.update_layout(legend_title_text=None, hovermode="x unified")
        return fig

    def cash_flow_analysis_table_chart(self):
        df_table = self.combine_fundamentals_and_forecasts_df()
        if not df_table.empty:
            df_table = df_table.loc[
                [
                    "revenue",
                    "revenue_growth",
                    "ebitda",
                    "ebitda_margin",
                    "ebit",
                    "capital_expenditures",
                    "cash_from_operation",
                    "investment_cash",
                    "free_cash_flow",
                    "interest_expense",
                    "company_tax_rate",
                ],
                :,
            ]

            df_table.loc["depreciation_and_amortization", :] = df_table.loc["ebitda", :] - df_table.loc["ebit", :]
            df_table.loc["operating_cash_flow_growth", :] = df_table.loc["cash_from_operation", :].pct_change()
            df_table.loc["investing_cash_flow_growth", :] = df_table.loc["investment_cash", :].pct_change()
            df_table.loc["capex_/_depreciation_and_amortization", :] = (
                df_table.loc["capital_expenditures", :] / df_table.loc["depreciation_and_amortization", :]
            )
            df_table.loc["unlevered_free_cash_flow", :] = df_table.loc["free_cash_flow", :] + df_table.loc[
                "interest_expense", :
            ] * (1 - df_table.loc["company_tax_rate", :])
            df_table.loc["unlevered_free_cash_flow_growth", :] = df_table.loc[
                "unlevered_free_cash_flow", :
            ].pct_change()
            df_table.loc["unlevered_free_cash_flow_margin", :] = (
                df_table.loc["unlevered_free_cash_flow", :] / df_table.loc["revenue", :]
            )
            df_table.drop(
                [
                    "depreciation_and_amortization",
                    "capital_expenditures",
                    "ebit",
                    "interest_expense",
                    "company_tax_rate",
                    "free_cash_flow",
                ],
                axis=0,
                inplace=True,
            )
        fig = self._make_pretty_table(df=df_table)
        return fig

    def cash_flow_analysis_bar_chart(self):
        fig = go.Figure()
        df_table = self.combine_fundamentals_and_forecasts_df()
        if not df_table.empty:
            df_table.loc["unlevered_free_cash_flow", :] = df_table.loc["free_cash_flow", :] + df_table.loc[
                "interest_expense", :
            ] * (1 - df_table.loc["company_tax_rate", :])
            df_table = df_table.loc[["cash_from_operation", "investment_cash", "unlevered_free_cash_flow"], :]
            df_table.index = self._make_presentable_fields(df_table.index.tolist(), bold=False)
            for variable in df_table.index:
                y = df_table.loc[variable, :].dropna().div(1000000).round(2).values
                fig.add_bar(
                    y=y,
                    x=df_table.loc[variable, :].dropna().index,
                    name=variable,
                    hovertemplate="<b>" + variable + "</b><br>%{x}<br>%{y:.2f} Mio.<extra></extra>",
                    text=y,
                    textposition="auto",
                )
        symbol = self.instrument.currency.symbol
        fig.update_yaxes(title=f"{symbol if symbol else ''} in Million")
        return fig

    def net_debt_and_ebitda_chart(self):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        df_table = self.combine_fundamentals_and_forecasts_df()
        if not df_table.empty:
            df_table = df_table.loc[["net_debt", "net_debt_to_ebitda_ratio"], :]
            net_debt_values = df_table.loc["net_debt", :].dropna().div(1000000).round(2).values
            fig.add_bar(
                x=df_table.loc["net_debt", :].dropna().index,
                y=net_debt_values,
                name="Net debt",
                hovertemplate="<b>Net Debt</b><br>%{x}<br>%{y:.2f} Mio.<extra></extra>",
                text=net_debt_values,
                textposition="auto",
            )
            fig.add_scatter(
                x=df_table.loc["net_debt_to_ebitda_ratio", :].dropna().index,
                y=df_table.loc["net_debt_to_ebitda_ratio", :].dropna().mul(100).values,
                name="Net debt / EBITDA",
                yaxis="y2",
                hovertemplate="<b>Net debt / EBITDA</b><br>%{x}<br>%{y:.2f}%<extra></extra>",
            )
        symbol = self.instrument.currency.symbol
        fig.update_yaxes(title=f"{symbol if symbol else ''} in Million", secondary_y=False)
        fig.update_yaxes(ticksuffix="%", secondary_y=True)
        return fig
