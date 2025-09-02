from datetime import date

import pandas as pd

from wbfdm.enums import Financial, PeriodType, SeriesType
from wbfdm.models import Instrument
from wbfdm.utils import rename_period_index_level_to_repr


def financial_metric_estimate_analysis(instrument_id: int, financial: Financial) -> tuple[pd.DataFrame, dict, list]:
    estimate_mapping = {}
    columns = []
    if not (
        df := pd.DataFrame(
            Instrument.objects.filter(id=instrument_id).dl.financials(
                values=[financial],
                series_type=SeriesType.FULL_ESTIMATE,
                period_type=PeriodType.ALL,
                from_year=date.today().year - 5,
            ),
        )
    ).empty:
        df = df.pivot_table(
            index=["year", "interim", "period_type", "estimate"],
            columns=["financial"],
            values=["value", "difference_pct", "value_high", "value_low", "value_amount", "value_stdev"],
            dropna=False,
        )
        df["difference_pct"] = df["difference_pct"] * 100
        df = rename_period_index_level_to_repr(df)
        df = df.set_index([[f"{index[0]}-{index[1]}" for index in df.index]])

        columns = list(df.index)

        df = df[["value", "difference_pct", "value_high", "value_low", "value_stdev", "value_amount"]]
        df = df.rename(
            columns={
                "difference_pct": "Diff (%)",
                "value": "Estimate",
                "value_amount": "#",
                "value_high": "High Est.",
                "value_low": "Low Est.",
                "value_stdev": "St.Dev. Est.",
            }
        )
        df = df.T

        df["financial"] = [index[0] for index in df.index]
        df = df.set_index([[f"{index[0]}-{index[1]}" for index in df.index]])
        df = df.reset_index()

    return df, estimate_mapping, columns


def financial_metric_growths(instrument_id: int, financial: Financial):
    # Get the base dataframe from a dataloader with the given financial
    if not (
        df := pd.DataFrame(
            Instrument.objects.filter(id=instrument_id).dl.financials(
                values=[financial],
                series_type=SeriesType.COMPLETE,
                period_type=PeriodType.ALL,
                from_year=date.today().year - 5,
            )
        )
    ).empty:
        # Pivot the dataframe to get the financial in the correct format
        df = df.pivot_table(index=["year", "interim", "period_type"], columns="financial", values="value")

        # Compute the growth factors
        df[f"{financial.value}_qq"] = df.loc[df.index.get_level_values("interim") != 0].pct_change() * 100
        df[f"{financial.value}_yy_y"] = (
            df.loc[df.index.get_level_values("interim") == 0, financial.value].pct_change() * 100
        )
        df[f"{financial.value}_yy_q"] = (
            df.loc[df.index.get_level_values("interim") != 0, financial.value].pct_change(4) * 100
        )
        df[f"{financial.value}_yy"] = df[f"{financial.value}_yy_y"].combine_first(df[f"{financial.value}_yy_q"])

        # Select on the two growth columns
        df = df[[f"{financial.value}_yy", f"{financial.value}_qq"]]

        df = rename_period_index_level_to_repr(df)
        df = df.set_index([[f"{index[0]}-{index[1]}" for index in df.index]])
        df = df.rename(columns={f"{financial.value}_yy": "YoY Growth (%)", f"{financial.value}_qq": "QoQ Growth (%)"})
        df = df.T
        df = df.reset_index().reset_index()

    return df
