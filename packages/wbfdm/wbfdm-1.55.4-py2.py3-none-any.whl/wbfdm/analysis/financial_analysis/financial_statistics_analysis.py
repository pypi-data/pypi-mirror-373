from datetime import date
from math import pow

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta


class FinancialStatistics:
    def __init__(self, prices: pd.Series):
        prices = prices.copy().astype("float")
        if type(prices) is not pd.Series:
            raise ValueError("prices is expected to be a pandas Series")
        self.prices = prices.sort_index()
        if not prices.empty:
            self.start = self.prices.index[0]
            self.end = self.prices.index[-1]
        else:
            self.start = self.end = None
        self.prices.index = pd.to_datetime(self.prices.index)

    def is_valid(self):
        return not self.prices.empty

    def extract_monthly_performance_df(self) -> pd.Series:
        return self.compute_performance()

    def extract_annual_performance_df(self) -> pd.Series:
        return self.compute_performance(freq="BYE")

    def extract_inception_performance_df(self) -> float:
        if not self.prices.empty and self.prices.iloc[0]:
            return self.prices.iloc[-1] / self.prices.iloc[0] - 1
        return 0

    def extract_daily_performance_df(self) -> pd.Series:
        return self.compute_performance(freq="B")

    # ---------------------------- Financial Statistics ----------------------------
    # ------------------------------------------------------------------------------

    def compute_performance(self, freq: str | int = "BME", extrapolate: bool = True) -> pd.Series:
        perfs = self.prices
        if not perfs.empty:
            if isinstance(freq, int):
                perfs = perfs.resample(f"{freq}D", origin="end").ffill().pct_change()
            else:
                perfs = perfs.asfreq(freq, method="ffill")
                if extrapolate:
                    perfs.loc[self.prices.index[0]] = self.prices.iloc[0]
                perfs.loc[self.prices.index[-1]] = self.prices.iloc[-1]
                perfs = perfs.sort_index()
                perfs = perfs / perfs.shift(1) - 1
        return perfs.dropna(how="any").rename("performance")

    def get_mean_return(self, freq: str = "B") -> float | None:
        """Calculates the mean of returns"""
        if self.is_valid():
            return self.compute_performance(freq=freq).mean()
        return None

    def get_best_and_worst_returns(self, top: int = 10, freq: str = "B") -> pd.DataFrame:
        """Returns a DataFrame with the top best returns and top worst returns"""
        df = pd.DataFrame(columns=["Date Best Return", "Best Return", "Date Worst Return", "Worst Return"])
        if self.is_valid():
            sort_returns = self.compute_performance(freq=freq).sort_values()
            df.loc[:, "Worst Return"] = sort_returns[0:top].values
            df.loc[:, "Date Worst Return"] = sort_returns[0:top].index
            sort_returns = sort_returns.sort_values(ascending=False)
            df.loc[:, "Best Return"] = sort_returns[0:top].values
            df.loc[:, "Date Best Return"] = sort_returns[0:top].index
            df["Date Worst Return"] = pd.to_datetime(df["Date Worst Return"])
            df["Date Best Return"] = pd.to_datetime(df["Date Best Return"])
            return df
        return df

    def get_drawdowns(self, freq: str = "B") -> pd.Series:
        """
        Investopedia: A drawdown is a peak-to-trough decline during a specific period for an investment,
        trading account, or fund. A drawdown is usually quoted as the percentage between the peak and the
        subsequent trough.
        """
        high_net_value = self.prices.cummax()  # keep highest price the column
        drawdowns = self.prices / high_net_value - 1
        if freq:
            drawdowns = drawdowns.asfreq(freq, method="ffill")
        return drawdowns

    def get_last_drawdowns(self) -> pd.Series:
        """Returns a Dataframe with the last drawdowns"""
        df = self.get_drawdowns()
        last_highest_price_date = df[df == 0].index[-1].strftime("%Y-%m-%d")
        return df.loc[last_highest_price_date : df.index[-1]]

    def get_maximum_drawdown(self) -> float:
        """Returns the maximum drawdown."""
        df = self.get_drawdowns()
        maximum_dd = df.min()  # maximum in negative value
        return maximum_dd

    def get_last_recent_maximum_drawdown(self) -> float:
        """Returns the last recent maximum drawdown."""
        df = self.get_last_drawdowns()
        maximum_dd = df.min()  # maximum in negative value
        return maximum_dd

    def get_maximum_drawdown_date(self) -> float:
        df = self.get_drawdowns()
        mdd_date = df[df == df.min()].index.to_pydatetime()[0].strftime("%Y-%m-%d")
        return mdd_date

    def get_last_recent_maximum_drawdown_date(self) -> date:
        """Returns the last recent maximum drawdown date."""
        df = self.get_last_drawdowns()
        mdd_date = df[df == df.min()].index.to_pydatetime()[0].strftime("%Y-%m-%d")
        return mdd_date

    def get_longest_drawdown_period(self) -> int:
        """Returns the longest number of day during drawdown"""
        df = self.get_drawdowns()
        df["Drawdown Period"] = df.mask(df < 0.0, 1)
        a = df["Drawdown Period"] != 0
        df1 = a.cumsum() - a.cumsum().where(~a).ffill().fillna(0).astype(int)
        return df1.max()

    def get_cumulative_returns(self, freq: str = "B") -> pd.Series:
        """Returns a dataframe with the cumulative return each day."""
        returns = self.compute_performance(freq=freq)
        # R = [(1+r1) * (1 + r2) * ... * (1+rn)] - 1
        return returns.add(1).cumprod() - 1

    def get_last_cumulative_return(self, freq: str = "B") -> float:
        """Returns the last cumulative return."""
        cumulative_returns = self.get_cumulative_returns(freq=freq)
        return cumulative_returns.iat[-1]

    def get_positive_outliers(self, quantile: float = 0.95, freq: str = "B") -> pd.Series:
        """Extracts the outliers in a DataFrame."""
        returns = self.compute_performance(freq=freq)
        return returns[returns > returns.quantile(quantile)].dropna(how="all")

    def get_value_at_risk(self, alpha: float = 0.05, freq: str = "B") -> float:
        """Calculates the value at risk for a given confident interval."""
        if alpha < 0 or alpha > 1:
            raise ValueError(f"Alpha = {alpha} is not possible, alpha must be between 0 and 1.")

        returns = self.compute_performance(freq=freq)
        return returns.quantile(alpha, interpolation="higher")

    def get_conditional_value_at_risk(self, alpha: float = 0.05, freq: str = "B") -> float:
        """Calculates the conditional value at risk for a given confident interval."""
        if alpha < 0 or alpha > 1:
            raise ValueError(f"Alpha = {alpha} is not possible, alpha must be between 0 and 1.")

        returns = self.compute_performance(freq=freq)
        return returns[returns <= returns.quantile(alpha, interpolation="lower")].dropna(how="all").mean()

    def get_skewness(self, freq: str = "B") -> float:
        """Calculates the skewness of the returns."""
        returns = self.compute_performance(freq=freq)
        return returns.skew()

    def get_kurtosis(self, freq: str = "B") -> float:
        """Calculates the Kurtosis of the returns."""
        returns = self.compute_performance(freq=freq)
        return returns.kurtosis()

    def get_excess_kurtosis(self, freq: str = "B") -> float:
        return self.get_kurtosis(freq=freq) - 3.0

    def get_compound_annual_growth_rate(self) -> float:
        """Calculates the compound annual growth rate (Last Price / First Price)(¹/year) - 1"""
        first_price, last_price = self.prices.iat[0], self.prices.iat[-1]
        years = (self.prices.index[-1] - self.prices.index[0]).days / 365.0
        return (last_price / first_price) ** (1 / years) - 1 if first_price != 0 and years != 0 else 0

    def get_sortino_ratio(self, target_ratio: float = 0, freq: str = "B") -> float:
        """
        Calculates the adjusted Sortino ratio:
        Sortino ratio = (Rp - target_ratio) / below_target_semi_deviation
        below_target_semi_deviation = √(1 / T * Σ (d²))
        d = (Rt-1 - target_ratio) only if the result is negative
        """
        returns = self.compute_performance(freq=freq)
        below_target_sd = np.sqrt((returns[returns < target_ratio] ** 2).sum() / len(returns))
        annualized_return = self.get_compound_annual_growth_rate()
        below_target_annualized = below_target_sd * np.sqrt(260)
        return (annualized_return - target_ratio) / below_target_annualized

    def get_adjusted_sortino_ratio(self, freq: str = "B") -> float:
        """Calculates the adjusted Sortino ratio (Sortino Ratio / √(2))"""
        return self.get_sortino_ratio(freq=freq) / np.sqrt(2)

    def get_calmar_ratio(self) -> float:
        """Calculates the calmar ratio (CAGR% / MaxDD%)"""
        compound_annual_growth_rate = self.get_compound_annual_growth_rate()
        maximum_dd = self.get_maximum_drawdown()
        return compound_annual_growth_rate / abs(maximum_dd)

    def get_risk_free_rate(self, risk_free_rate_prices_df: pd.Series) -> float | None:
        # if the instrument has no prices, we do not know the lifetime of instrument, so we do not know for the risk
        # instrument too
        if not risk_free_rate_prices_df.empty:
            nb_days = (self.prices.index[-1] - self.prices.index[0]).days
            nb_days = 1 if nb_days == 0 else nb_days
            exp = 365.0 / nb_days
            annualized_free_rate = 1 + risk_free_rate_prices_df.sort_index(ascending=False) / (365 * 100)
            tmp = annualized_free_rate.shift(1, fill_value=1).cumprod().dropna()
            risk_free_rate = pow(tmp.iloc[-1], exp) - 1
            return risk_free_rate

    def get_sterling_ratio(self, risk_free_rate_prices_df: pd.Series) -> float | None:
        """Calculates the adjusted Sterling ratio ((Rp- Rf) / MDD)"""
        if not risk_free_rate_prices_df.empty:
            maximum_dd = self.get_maximum_drawdown()
            annualized_return = self.get_compound_annual_growth_rate()
            rf = self.get_risk_free_rate(risk_free_rate_prices_df)
            rf = 0 if not rf else rf
            return (annualized_return - rf) / abs(maximum_dd)

    def get_burke_ratio(self, risk_free_rate_prices_df: pd.Series) -> float | None:
        """Calculates the adjusted Burke ratio ((Rp- Rf) / √(Σ (DD²)))"""
        if not risk_free_rate_prices_df.empty:
            drawdowns = self.get_drawdowns()
            drawdowns = np.sqrt(drawdowns[drawdowns != 0].pow(2).sum())
            annualized_return = self.get_compound_annual_growth_rate()
            rf = self.get_risk_free_rate(risk_free_rate_prices_df)
            rf = 0 if not rf else rf
            return (annualized_return - rf) / drawdowns

    def get_volatility(self, freq: str = "B") -> float:
        """Calculates the volatility of returns"""
        adj = 1
        if freq == "B":
            adj = 260
        elif freq == "W-MON":
            adj = 52
        elif freq == "BME":
            adj = 12
        return self.compute_performance(freq=freq).std() * np.sqrt(adj)

    def get_annualized_daily_volatility(self) -> float:
        """Computed the annualized volatility"""
        df = self.compute_performance(freq=1)
        last_date = df.index[-1]
        last_year = last_date - relativedelta(months=12)
        df = df.loc[df.index >= last_year]
        return df.std()

    def prepare_daily_returns_instrument_vs_benchmark(self, benchmark_prices_df: pd.Series) -> pd.DataFrame:
        if benchmark_prices_df.empty:
            raise ValueError("benchmark price cannot be empty")
        df = pd.DataFrame()
        df["benchmark"] = FinancialStatistics(benchmark_prices_df).extract_daily_performance_df()
        df["instrument"] = self.extract_daily_performance_df()
        return df

    def get_beta(self, benchmark_prices_df: pd.Series) -> float | None:
        if not benchmark_prices_df.empty:
            df = self.prepare_daily_returns_instrument_vs_benchmark(benchmark_prices_df)
            cov = df["instrument"].cov(df["benchmark"])
            var = df["benchmark"].var()
            beta = cov / var
            return beta

    def get_correlation(self, benchmark_prices_df: pd.Series) -> float | None:
        if not benchmark_prices_df.empty:
            df = self.prepare_daily_returns_instrument_vs_benchmark(benchmark_prices_df)
            return df["instrument"].corr(df["benchmark"])

    def get_sharpe_ratio(self, risk_free_rate_prices_df: pd.Series) -> float | None:
        if not risk_free_rate_prices_df.empty:
            annualized_volatility = self.get_volatility()
            annualized_return = self.get_compound_annual_growth_rate()
            rf = self.get_risk_free_rate(risk_free_rate_prices_df)
            rf = 0 if not rf else rf
            return (annualized_return - rf) / annualized_volatility

    # -------------------------- End of Financial Statistics -----------------------
    # ------------------------------------------------------------------------------
