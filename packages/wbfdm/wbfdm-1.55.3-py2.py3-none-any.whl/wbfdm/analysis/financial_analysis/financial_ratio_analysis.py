from contextlib import suppress
from datetime import date

import pandas as pd
from django.db.models import TextChoices

from wbfdm.enums import Financial, MarketData, PeriodType
from wbfdm.models import Instrument


class FinancialRatio(TextChoices):
    PE = "pe", "P/E"
    PS = "ps", "P/S"
    PB = "pb", "P/B"
    PFCF = "pfcf", "P/FCF"

    @classmethod
    def get_financials_for_ratio(cls, ratio: "FinancialRatio") -> list[Financial]:
        financials = {
            cls.PE: [Financial.EPS],
            cls.PS: [Financial.REVENUE, Financial.SHARES_OUTSTANDING],
            cls.PB: [Financial.TANGIBLE_BOOK_VALUE_PER_SHARE],
            cls.PFCF: [Financial.CASH_FLOW_FROM_OPERATIONS, Financial.CAPEX],
        }

        return financials[ratio]

    @classmethod
    def get_financials(cls, ratios: list["FinancialRatio"]) -> list[Financial]:
        financials = list()
        for ratio in ratios:
            financials.extend(cls.get_financials_for_ratio(ratio))
        return list(set(financials))

    def compute_pe(self, df: pd.DataFrame) -> pd.DataFrame:
        if Financial.EPS.value in df:
            df[self.value] = df["close"] / df[Financial.EPS.value]
        return df

    def compute_ps(self, df: pd.DataFrame) -> pd.DataFrame:
        if "revenue_per_share" in df:
            df[self.value] = df["close"] / df["revenue_per_share"]
        return df

    def compute_pb(self, df: pd.DataFrame) -> pd.DataFrame:
        if Financial.TANGIBLE_BOOK_VALUE_PER_SHARE.value in df:
            df[self.value] = df["close"] / df[Financial.TANGIBLE_BOOK_VALUE_PER_SHARE.value]
        return df

    def compute_pfcf(self, df: pd.DataFrame) -> pd.DataFrame:
        if Financial.FREE_CASH_FLOW_PER_SHARE.value in df:
            df[self.value] = df["close"] / df[Financial.FREE_CASH_FLOW_PER_SHARE.value]
        return df

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        compute_methods = {
            self.PE: self.compute_pe,
            self.PS: self.compute_ps,
            self.PB: self.compute_pb,
            self.PFCF: self.compute_pfcf,
        }
        return compute_methods[self](df)


def get_financial_ratios(
    instrument_id: int, ratios: list[FinancialRatio], from_date: date, to_date: date, ttm: bool = True
):
    """Computes financial ratios and adds them to the dataframe"""
    if ttm:
        financials_df = pd.DataFrame(
            Instrument.objects.filter(id=instrument_id).dl.statements(
                financials=FinancialRatio.get_financials(ratios),
                period_type=PeriodType.INTERIM,
            )
        )
    else:
        financials_df = pd.DataFrame(
            Instrument.objects.filter(id=instrument_id).dl.financials(
                values=FinancialRatio.get_financials(ratios),
                period_type=PeriodType.INTERIM,
            )
        )
    if financials_df.empty:
        return pd.DataFrame()
    financials_df = financials_df.pivot_table(
        index="period_end_date",
        columns="financial",
        values="value",
    ).sort_index()
    financials_df.index = pd.to_datetime(financials_df.index)
    if (
        FinancialRatio.PS in ratios
        and Financial.REVENUE.value in financials_df
        and Financial.SHARES_OUTSTANDING.value in financials_df
    ):
        financials_df["revenue_per_share"] = (
            financials_df[Financial.REVENUE.value] / financials_df[Financial.SHARES_OUTSTANDING.value]
        )
    if (
        FinancialRatio.PFCF in ratios
        and Financial.FREE_CASH_FLOW_PER_SHARE.value not in financials_df.columns
        and Financial.CASH_FLOW_FROM_OPERATIONS.value in financials_df
        and Financial.CAPEX.value in financials_df
    ):
        financials_df[Financial.FREE_CASH_FLOW_PER_SHARE.value] = (
            financials_df[Financial.CASH_FLOW_FROM_OPERATIONS.value] - financials_df[Financial.CAPEX.value]
        )
    financials_df = financials_df.rolling("365d").sum()
    prices_df = pd.DataFrame(
        Instrument.objects.filter(id=instrument_id).dl.market_data(
            values=[MarketData.CLOSE], from_date=from_date, to_date=to_date
        )
    )
    if not prices_df.empty:
        prices_df = prices_df.set_index("valuation_date").sort_index()[["close"]]
        prices_df.index = pd.to_datetime(prices_df.index)

        financials_df = pd.merge_asof(
            prices_df, financials_df, left_index=True, right_index=True, direction="backward" if ttm else "forward"
        )

    for ratio in ratios:
        with suppress(KeyError):
            financials_df = ratio.compute(financials_df)

    return financials_df
