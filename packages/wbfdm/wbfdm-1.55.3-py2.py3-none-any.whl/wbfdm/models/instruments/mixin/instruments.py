import calendar
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict, Optional

import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay

from wbfdm.analysis.financial_analysis.financial_statistics_analysis import (
    FinancialStatistics,
)
from wbfdm.backends.dto import PriceDTO
from wbfdm.enums import MarketData
from wbfdm.models.instruments.instrument_prices import InstrumentPrice


class InstrumentPMSMixin:
    def get_prices_df_with_calculated(self, market_data: MarketData = MarketData.CLOSE, **kwargs) -> pd.DataFrame:
        prices = pd.DataFrame(self.get_prices(values=[market_data], **kwargs)).rename(
            columns={"valuation_date": "date"}
        )
        if "calculated" not in prices.columns:
            prices["calculated"] = False

        if not prices.empty and market_data.value in prices.columns:
            prices = prices[[market_data.value, "calculated", "date"]].sort_values(by="calculated")
            prices = prices.groupby("date").first()
            prices.index = pd.to_datetime(prices.index)
            prices = prices.replace([np.inf, -np.inf, np.nan], None)
            return prices.sort_index()
        return pd.DataFrame()

    def get_prices_df(self, market_data: MarketData = MarketData.CLOSE, **kwargs) -> pd.Series:
        prices = self.get_prices_df_with_calculated(market_data=market_data, **kwargs)

        if market_data.value in prices.columns:
            return prices[market_data.value].astype(float)
        return pd.Series(dtype="float64")

    def get_price(self, val_date: date, price_date_timedelta: int = 3) -> Decimal:
        if self.is_cash:
            return Decimal(1)
        return Decimal(self._build_dto(val_date, price_date_timedelta=price_date_timedelta).close)

    def _build_dto(self, val_date: date, price_date_timedelta: int = 3) -> PriceDTO:  # for backward compatibility
        try:
            try:
                price = self.valuations.get(date=val_date)
            except InstrumentPrice.DoesNotExist:
                price = self.prices.get(date=val_date)
            close = float(price.net_value)
            return PriceDTO(
                pk=price.id,
                instrument=self.id,
                date=val_date,
                open=close,
                close=close,
                high=close,
                low=close,
                volume=close,
                market_capitalization=price.market_capitalization,
                outstanding_shares=float(price.outstanding_shares) if price.outstanding_shares else None,
            )
        except InstrumentPrice.DoesNotExist:
            prices = sorted(
                self.get_prices(from_date=(val_date - BDay(price_date_timedelta)).date(), to_date=val_date),
                key=lambda x: x["valuation_date"],
                reverse=True,
            )
            if (
                prices
                and (p := prices[0])
                and (close := p.get("close", None))
                and (p_date := p.get("valuation_date", None))
            ):
                return PriceDTO(
                    pk=p["id"],
                    instrument=self.id,
                    date=p_date,
                    open=p.get("open", None),
                    close=close,
                    high=p.get("high", None),
                    low=p.get("low", None),
                    volume=p.get("volume", None),
                    market_capitalization=p.get("market_capitalization", None),
                    outstanding_shares=p.get("outstanding_shares", None),
                )
            raise ValueError("Not price was found")

    # Instrument Prices Utility Functions
    @classmethod
    def _compute_performance(cls, prices: pd.Series, freq: str = "BME") -> pd.DataFrame:
        if prices.empty:
            raise ValueError("Price series cannot be empty")
        performance = FinancialStatistics(prices).compute_performance(freq=freq)  # For backward compatibility
        return pd.concat([prices, performance], axis=1).dropna(
            how="any", subset=["performance"]
        )  # For backward compatibility

    @classmethod
    def extract_monthly_performance_df(cls, prices: pd.Series) -> pd.DataFrame:
        if prices.empty:
            raise ValueError("Price series cannot be empty")
        performance = FinancialStatistics(prices).extract_monthly_performance_df()  # For backward compatibility
        df = pd.concat([performance], axis=1, keys=["performance"])
        df["year"] = df.index.year
        df["month"] = df.index.month
        return df.dropna(how="any", subset=["performance"]).reset_index(drop=True)  # For backward compatibility

    @classmethod
    def extract_annual_performance_df(cls, prices: pd.Series) -> pd.DataFrame:
        if prices.empty:
            raise ValueError("Price series cannot be empty")
        performance = FinancialStatistics(prices).extract_annual_performance_df()  # For backward compatibility
        df = pd.concat([performance], axis=1, keys=["performance"])
        df["year"] = df.index.year
        return df.dropna(how="any", subset=["performance"]).reset_index(drop=True)  # For backward compatibility

    @classmethod
    def extract_inception_performance_df(cls, prices: pd.Series) -> float:
        if prices.empty:
            raise ValueError("Price series cannot be empty")
        return FinancialStatistics(prices).extract_inception_performance_df()  # For backward compatibility

    @classmethod
    def extract_daily_performance_df(cls, prices: pd.Series) -> pd.DataFrame:
        if prices.empty:
            raise ValueError("Price series cannot be empty")
        performance = FinancialStatistics(prices).extract_daily_performance_df()
        df = pd.concat([performance], axis=1, keys=["performance"])
        df["year"] = df.index.year
        return df.dropna(how="any", subset=["performance"])  # For backward compatibility

    def get_monthly_return_summary(
        self, start: Optional[date] = None, end: Optional[date] = None, **kwargs
    ) -> pd.DataFrame:
        if not (prices := self.get_prices_df_with_calculated(from_date=start, to_date=end, **kwargs)).empty:
            calculated_mask = prices[["calculated"]].copy().groupby([prices.index.year, prices.index.month]).tail(1)
            calculated_mask["year"] = calculated_mask.index.year
            calculated_mask["month"] = calculated_mask.index.month
            calculated_mask = (
                calculated_mask[["year", "month", "calculated"]]
                .reset_index(drop=True)
                .groupby(["year", "month"])
                .any()
            )
            monthly_perfs = self.extract_monthly_performance_df(prices.close)
            annual_perfs = self.extract_annual_performance_df(prices.close)
            annual_perfs["month"] = "annual"
            perfs = pd.concat([monthly_perfs, annual_perfs], axis=0, ignore_index=True)

            return perfs.replace([np.inf, -np.inf, np.nan], None), calculated_mask
        return pd.DataFrame(), pd.DataFrame()

    def get_monthly_return_summary_dict(
        self, start: Optional[date] = None, end: Optional[date] = None, **kwargs
    ) -> Dict:
        perfs, calculated_mask = self.get_monthly_return_summary(start, end, **kwargs)
        res = defaultdict(dict)
        if not perfs.empty:
            for year, df in perfs.sort_values(by="year", ascending=False).groupby("year", sort=False):
                df = df.set_index("month")
                for i in range(1, 13):
                    try:
                        perf = float(df.loc[i, "performance"])
                    except (IndexError, KeyError):
                        perf = None
                    try:
                        calculated = bool(calculated_mask.loc[(year, i), "calculated"])
                    except (IndexError, KeyError):
                        calculated = False
                    res[year][calendar.month_abbr[i]] = {"performance": perf, "calculated": calculated}
                try:
                    res[year]["annual"] = {
                        "performance": float(df.loc["annual", "performance"]),
                        "calculated": bool(calculated_mask.loc[(year, slice(None)), "calculated"].any()),
                    }
                except (IndexError, KeyError):
                    res[year]["annual"] = {"performance": None, "calculated": False}

        return dict(res)

    def build_benchmark_df(self, end_date: Optional[date] = None, **kwargs) -> pd.Series:
        df = pd.Series(dtype="float64")
        prices_df = self.get_prices_df(to_date=end_date).rename("net_value")
        if not prices_df.empty and (benchmark := self.primary_benchmark) and self.primary_risk_instrument:
            start_date = prices_df.index[0]
            end_date = prices_df.index[-1]
            kwargs = {"from_date": start_date, "to_date": end_date}
            # Get and prepare Risk free rate dataframe from stainly
            risk_df = self.primary_risk_instrument.get_prices_df(**kwargs).rename("rate")

            benchmark_df = benchmark.get_prices_df(**kwargs).rename("benchmark_net_value")
            # Prepare final dataframe, fill the NAN with backward index
            df = pd.concat([risk_df, benchmark_df, prices_df], axis=1).astype("float64").ffill(axis=0).sort_index()
            df.index = pd.to_datetime(df.index)

        return df

    @classmethod
    def bulk_save_instrument_prices(cls, objs):
        InstrumentPrice.objects.bulk_create(
            objs,
            unique_fields=["instrument", "calculated", "date"],
            update_conflicts=True,
            update_fields=[
                "net_value",
                "gross_value",
                "volume",
                "market_capitalization",
                "market_capitalization_consolidated",
                "calculated",
            ],
            batch_size=1000,
        )
