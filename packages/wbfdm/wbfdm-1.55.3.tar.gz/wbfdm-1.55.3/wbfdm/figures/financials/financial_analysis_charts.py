import enum
from datetime import date
from types import DynamicClassAttribute

import numpy as np
import pandas as pd
from django.db import models
from wbcore.contrib.currency.models import CurrencyFXRates

from wbfdm.models import Instrument


class PeriodChoices(models.TextChoices):
    TTM = "TTM", "TTM"
    NTM = "FTM", "FTM"
    FY1 = "FY1", "FY+1"
    FY2 = "FY2", "FY+2"


class VariableChoicesChartLabel(enum.Enum):
    PE = "Price-to-Earnings PE"
    PEG = "Price-to-Earnings-to-Growth PEG"
    PS = "Price-to-Sales PS"
    PFCF = "Price-to-FreeCashflow P/FCF"
    EVEBITDA = "EV-to-EBITDA"
    EV = "Enterprise Value"
    EPSG = "EPS growth"
    REVG = "Revenue growth"
    FCFG = "FCF growth"
    MKTCAP = "Market Cap"


class VariableFormatChoices(enum.Enum):
    PE = ".1f}x"
    PEG = ".2f}"
    PS = ".1f}x"
    PFCF = ".1f}x"
    EVEBITDA = ".1f}x"
    EV = ".0f}"
    EPSG = ".1%}"
    REVG = ".1%}"
    FCFG = ".1%}"
    MKTCAP = ",.0f}bn"


class VariableChoices(models.TextChoices):
    PE = "PE", "P/E"
    PEG = "PEG", "PEG"
    PS = "PS", "P/S"
    PFCF = "PFCF", "P/FCF"
    EVEBITDA = "EVEBITDA", "EV/EBITDA"
    EV = "EV", "Enterprise Value"
    EPSG = "EPSG", "EPS Growth"
    REVG = "REVG", "Revenue Growth"
    FCFG = "FCFG", "FCF Growth"
    MKTCAP = "MKTCAP", "Market Cap"

    @DynamicClassAttribute
    def format(self):
        """The format of the Enum member."""
        return VariableFormatChoices[self._value_].value

    @DynamicClassAttribute
    def chart_label(self):
        """The chart_label of the Enum member."""
        return VariableChoicesChartLabel[self._value_].value


def _interpolate(decreasing: pd.Series, increasing: pd.Series, factor) -> float:
    return (decreasing * (1 - factor)) + (increasing * factor)


def _adapt_growth(first, second) -> np.ndarray:
    """
    In finance some variables, e.g., earnings, may pass from negative to positive and a standard percentage change
    formula is inappropriate. This formula modifies the calculation for such cases.

    Parameters
    ----------
    first = past data point/series
    second = more recent data point/series

    Returns
    -------
    A float number representing growth (percentage change)

    """
    return np.where(first > 0, second / first - 1, (second + abs(first)) / abs(first))


class FinancialAnalysisGenerator:
    def __init__(self, instruments: list, from_date: date, to_date: date, with_related: bool = False):
        """
        Initialize a generator for a specific instrument

        Parameters
        ----------
        instrument = instrument of choice
        from_date
        to_date
        with_related = extend the instrument to a list that includes all related instruments
        """
        self.instruments = instruments
        self.from_date = from_date
        self.to_date = to_date

        if with_related:
            self.instruments.extend(
                list(
                    Instrument.objects.filter(
                        models.Q(instrument_classification_related__classified_instrument__instrument__in=instruments)
                    )
                )
            )
        self.instruments_repr_map = {i.id: i.name_repr for i in self.instruments}
        self.currency_map = {i.id: i.currency.id for i in self.instruments}

    def build_df(
        self,
        instrument_prices_field_names: list[str] = [],
        fundamental_field_names: list[str] = [],
        forecast_field_names: list[str] = [],
        daily_fundamental_field_names: list[str] = [],
    ):
        """
        Used to returns a df with all the variables passed in four separate lists

        Parameters
        ----------
        instrument_prices_field_names
        fundamental_field_names
        forecast_field_names
        daily_fundamental_field_names

        Returns
        -------
        A df with all the variables in columns and date/instrument index
        """

        # df_list = []
        # if instrument_prices_field_names:
        #     df_append = pd.DataFrame(
        #         InstrumentPrice.objects.filter(
        #             instrument__in=self.instruments, date__gte=self.from_date, date__lte=self.to_date, calculated=False
        #         ).values("date", "instrument", "net_value", "outstanding_shares")
        #     )
        #     if not df_append.empty:
        #         df_list.append(df_append.set_index(["instrument", "date"]))
        #
        # end_date_df = pd.DataFrame(
        #     FiscalPeriod.objects.filter(
        #         period_type=FiscalPeriod.PeriodTypeChoice.ANNUAL,
        #         period_interim=False,
        #         instrument__in=self.instruments,
        #     ).values("period_end_date", "instrument")
        # )
        # if not end_date_df.empty:
        #     if fundamental_field_names:
        #         df_append = pd.DataFrame(
        #             Fundamental.annual_objects.filter(
        #                 instrument__in=self.instruments,
        #                 period__date_range__overlap=DateRange(self.from_date, self.to_date),
        #             ).values(
        #                 "instrument",
        #                 "period__period_end_date",
        #                 *fundamental_field_names,
        #             )
        #         ).rename(columns={"period__period_end_date": "date"})
        #         if not df_append.empty:
        #             df_list.append(df_append.set_index(["instrument", "date"]))
        #
        #     if forecast_field_names:
        #         df_append = pd.DataFrame(
        #             Forecast.objects.filter(
        #                 instrument__in=self.instruments, date__gte=self.from_date, date__lte=self.to_date
        #             ).values("instrument", "date", *forecast_field_names)
        #         )
        #         if not df_append.empty:
        #             df_list.append(df_append.set_index(["instrument", "date"]))
        #
        #     if daily_fundamental_field_names:
        #         df_append = pd.DataFrame(
        #             DailyFundamental.objects.annotate(free_cash_flow_ttm=F("free_cash_flow"))
        #             .filter(instrument__in=self.instruments, date__gte=self.from_date, date__lte=self.to_date)
        #             .values("instrument", "date", *daily_fundamental_field_names)
        #         )
        #         if not df_append.empty:
        #             df_list.append(df_append.set_index(["instrument", "date"]))
        #
        #     df = pd.concat(df_list, axis=1).sort_index().astype(float)
        #
        #     if df.columns.duplicated().any():
        #         raise ValueError("You probably have a duplicated field in the field name list")
        #
        #     if df.columns.symmetric_difference(
        #         instrument_prices_field_names
        #         + fundamental_field_names
        #         + forecast_field_names
        #         + daily_fundamental_field_names
        #     ).empty:
        #         return df.merge(
        #             end_date_df.sort_values(by="period_end_date")
        #             .groupby("instrument")
        #             .last()
        #             .rename(columns={"period_end_date": "end_date"}),
        #             left_on="instrument",
        #             right_index=True,
        #         )
        return pd.DataFrame()

    def convert_fx(self, df: pd.DataFrame, foreign_fx_field_names: list[str]) -> pd.DataFrame:
        """
        A function to FX

        Parameters
        ----------
        df = dataframe that has one or plus columns to be converted
        foreign_fx_field_names = column names to be converted

        Returns
        -------
        A dataframe with one or more columns converted with FX
        """
        df = df.set_index(["instrument", "date"])
        df["currency"] = df.index.get_level_values("instrument").map(self.currency_map)
        currencies = df["currency"].unique()
        df = df.reset_index().set_index(["date", "currency"])
        df_fx_rate = pd.DataFrame(
            CurrencyFXRates.objects.order_by("date", "currency__id")
            .filter(date__range=[self.from_date, self.to_date], currency__in=currencies)
            .values("date", "currency", "value")
        ).set_index(["date", "currency"])
        df = df.join(df_fx_rate).rename(columns={"value": "fx"}).reset_index()
        df = df.set_index(["instrument", "date"]).groupby("instrument").ffill()
        df[foreign_fx_field_names] = df[foreign_fx_field_names].div(df["fx"].astype(float), axis=0)

        return df.reset_index()

    @staticmethod
    def clean_data(
        df: pd.DataFrame,
        var_list: list[str] = [],
        drop_negative=True,
        q_low: float = 0.05,
        q_high: float = 0.95,
        z_max: int = 100,
        smooth_range: int = 3,
    ) -> pd.DataFrame:
        """
        A function to clean time-series.

        1) Drops negative values (financial ratios are non-meaningful in this case)
        2) Drops outliers above and below a certain quartile
        3) Drops values above a certain threshold

        Parameters
        ----------
        var_list = a list of variables to clean
        drop_negative = boolean to consider only positive numbers
        q_low = lower cut-off quartile
        q_high = upper cut-off quartile
        z_max = upper absolute cutoff
        smooth_range = rolling period for simple moving average smoothing

        Returns
        -------
        A clean time-series
        """
        df_temp = df.loc[:, (var_list, slice(None))].copy()
        if drop_negative:
            df_temp = df_temp.mask(df_temp < 0)
        df_temp = df_temp.where(
            df_temp.ge(df_temp.quantile(q_low), axis=1) & df_temp.le(df_temp.quantile(q_high), axis=1)
        )
        df_temp.loc[:, var_list] = df_temp[var_list].where(df_temp[var_list] < z_max)
        df_temp.ffill(inplace=True)
        df_temp.loc[:, var_list] = df_temp.loc[:, var_list].rolling(window=smooth_range).mean()
        df.loc[:, (var_list, slice(None))] = df_temp
        return df

    def get_common_valuation_ratios_df(self, period: PeriodChoices, clean_data: bool = True) -> pd.DataFrame:
        """
        Calculates financial valuation ratios

        Parameters
        ----------
        period = financial period, i.e., Next Twelve Months, Trailing Twelve Months, Fiscal Year +1 and +2
        clean_data = a boolean to apply a clean_series method

        Returns
        -------
        A dataframe with common valuation ratios for all instruments of interest

        """
        df = self.build_df(
            ["net_value", "outstanding_shares"],
            ["revenue", "net_debt", "ebitda", "eps", "free_cash_flow"],
            [
                "revenue_y1",
                "entreprise_value_y1",
                "net_debt_y1",
                "ebitda_y1",
                "eps_y1",
                "free_cash_flow_y1",
                "revenue_y2",
                "entreprise_value_y2",
                "net_debt_y2",
                "ebitda_y2",
                "eps_y2",
                "free_cash_flow_y2",
            ],
            ["eps_ttm", "eps_ftw"],
        )

        if df.empty:
            return df

        if clean_data:
            df = df.groupby(level=0).ffill().groupby(level=0).bfill()

        # Calculate a decimal factor to know how many days an instrument has till its "annual report" publication
        # so Trailing Twelve Month (TTM) and Next(or Forward) Twelve Month (NTM/FTM) interpolated variables
        # may be calculated
        df["factor"] = (365 - (df.end_date - df.index.get_level_values("date")).dt.days) % 365 / 365
        df["free_cash_flow_ntm"] = _interpolate(df["free_cash_flow_y1"], df["free_cash_flow_y2"], df["factor"])
        df["free_cash_flow_ttm"] = _interpolate(df["free_cash_flow"], df["free_cash_flow_y1"], df["factor"])
        df["revenue_ntm"] = _interpolate(df["revenue_y1"], df["revenue_y2"], df["factor"])
        df["revenue_ttm"] = _interpolate(df["revenue"], df["revenue_y1"], df["factor"])
        df["mktcap"] = (df["net_value"] * df["outstanding_shares"] / 1000000000).replace(0, np.inf)
        match period:
            case PeriodChoices.NTM:
                df["revenue"] = df["revenue_ntm"]
                df["eps"] = df["eps_ftw"]
                df["ebitda"] = _interpolate(df["ebitda_y1"], df["ebitda_y2"], df["factor"])
                df["free_cash_flow"] = _interpolate(df["free_cash_flow_y1"], df["free_cash_flow_y2"], df["factor"])
                df["net_debt"] = _interpolate(df["net_debt_y1"], df["net_debt_y2"], df["factor"])
                df["ev"] = (df["net_value"] * df["outstanding_shares"]) + df["net_debt"]
                df["epsg"] = _adapt_growth(df["eps_ttm"], df["eps_ftw"])
                df["fcfg"] = _adapt_growth(df["free_cash_flow_ttm"], df["free_cash_flow_ntm"])
                df["revg"] = _adapt_growth(df["revenue_ttm"], df["revenue_ntm"])
            case PeriodChoices.TTM:
                df["revenue"] = df["revenue_ttm"]
                df["eps"] = df["eps_ttm"]
                df["ebitda"] = _interpolate(df["ebitda"], df["ebitda_y1"], df["factor"])
                df["free_cash_flow"] = _interpolate(df["free_cash_flow"], df["free_cash_flow_y1"], df["factor"])
                df["net_debt"] = _interpolate(df["net_debt"], df["net_debt_y1"], df["factor"])
                df["ev"] = df["net_value"] * df["outstanding_shares"] + df["net_debt"]
                df["epsg"] = _adapt_growth(df["eps_ttm"].shift(250), df["eps_ttm"])
                df["fcfg"] = _adapt_growth(df["free_cash_flow_ttm"].shift(250), df["free_cash_flow_ttm"])
                df["revg"] = _adapt_growth(df["revenue"], df["revenue_ttm"])
            case default:  # noqa
                df["ev"] = df["entreprise_value_y1"]
                df["ebitda"] = df["ebitda_y1"]
                df["free_cash_flow"] = df["free_cash_flow_y1"]
                df["epsg"] = _adapt_growth(df["eps"], df["eps_y1"])
                df["eps"] = df["eps_y1"]
                df["fcfg"] = _adapt_growth(df["free_cash_flow"], df["free_cash_flow_y1"])
                df["revg"] = _adapt_growth(df["revenue"], df["revenue_y1"])
                if period == PeriodChoices.FY2:
                    df["ev"] = df["entreprise_value_y2"]
                    df["eps"] = df["eps_y2"]
                    df["ebitda"] = df["ebitda_y2"]
                    df["free_cash_flow"] = df["free_cash_flow_y2"]
                    df["epsg"] = ((1 + _adapt_growth(df["eps_y1"], df["eps_y2"])) * (1 + df["epsg"])) - 1
                    df["fcfg"] = (
                        (_adapt_growth(df["free_cash_flow_y1"], df["free_cash_flow_y2"])) * (1 + df["free_cash_flow"])
                    ) - 1
                    df["revg"] = ((_adapt_growth(df["revenue_y1"], df["revenue_y2"])) * (1 + df["revg"])) - 1

        df = df.interpolate(method="linear")

        # After getting the dataframe, calculate the ratios, then optionally clean the final series
        df["pe"] = df["net_value"] / df["eps"]
        df["peg"] = df["net_value"] / df["eps"] / (100 * df["epsg"])
        df["ps"] = df["net_value"] / (df["revenue"] / df["outstanding_shares"])
        df["pfcf"] = df["net_value"] / df["free_cash_flow"]
        df["evebitda"] = df["ev"] / df["ebitda"]

        if clean_data:
            df = df.unstack("instrument")
            df = self.clean_data(df=df, var_list=["pe", "pfcf", "evebitda"])
            df = self.clean_data(df=df, var_list=["ps"], z_max=40)
            df = self.clean_data(df=df, var_list=["peg"], z_max=15, smooth_range=10).replace(0, np.nan)
            df = self.clean_data(df=df, var_list=["ev", "epsg", "revg", "fcfg"], drop_negative=False)
            df = df.stack("instrument")

        df = df.reset_index()
        df = pd.concat([df[df.instrument == self.instruments[0].id], df[df.instrument != self.instruments[0].id]])
        df["instrument_title"] = df["instrument"].map(self.instruments_repr_map)

        df = self.convert_fx(df, ["ev", "mktcap"]).replace([np.inf, -np.inf, np.nan], None)

        return df[
            [
                "instrument",
                "instrument_title",
                "date",
                "pe",
                "peg",
                "ps",
                "pfcf",
                "evebitda",
                "ev",
                "mktcap",
                "epsg",
                "revg",
                "fcfg",
            ]
        ]

    def get_earnings_df(self, period: PeriodChoices, clean_data: bool = True) -> pd.DataFrame:
        """
        Calculates earnings anylysis

        Parameters
        ----------
        period = financial period, i.e., Next Twelve Months, Trailing Twelve Months, Fiscal Year +1 and +2
        clean_data = a boolean to apply a clean_series method

        Returns
        -------
        A dataframe with earnings analysis for all instruments of interest

        """
        df = self.build_df(
            [],
            [],
            ["eps_y1", "eps_y2"],
            ["eps_ttm", "eps_ftw"],
        )

        if df.empty:
            return df

        if clean_data:
            df = df.groupby(level=0).ffill()

        match period:
            case PeriodChoices.FY1:
                df["eps"] = df["eps_y1"]
            case PeriodChoices.FY2:
                df["eps"] = df["eps_y2"]
            case PeriodChoices.TTM:
                df["eps"] = df["eps_ttm"]
            case default:  # noqa
                df["eps"] = df["eps_ftw"]

        df = df.interpolate(method="linear")

        if clean_data:
            df = df.unstack("instrument")
            df = self.clean_data(
                df=df, var_list=["eps"], drop_negative=False, q_low=0.01, q_high=0.99, z_max=200, smooth_range=4
            )
            df = df.stack("instrument")

        df = df.reset_index()
        df = pd.concat([df[df.instrument == self.instruments[0].id], df[df.instrument != self.instruments[0].id]])
        df["instrument_title"] = df["instrument"].map(self.instruments_repr_map)

        df = self.convert_fx(df, ["eps"]).replace([np.inf, -np.inf, np.nan], None)

        return df[
            [
                "instrument",
                "instrument_title",
                "date",
                "eps",
            ]
        ]
