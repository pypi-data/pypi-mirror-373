from datetime import date, timedelta
from typing import TYPE_CHECKING, Literal

import pandas as pd
from pandas.tseries.offsets import BDay
from stockstats import StockDataFrame

from wbfdm.analysis.technical_analysis.traces import TechnicalAnalysisTraceFactory
from wbfdm.enums import MarketData

if TYPE_CHECKING:
    from wbfdm.models import Instrument


class TechnicalAnalysis:
    def __init__(self, instrument: "Instrument", sdf: StockDataFrame):
        self.instrument = instrument
        self._sdf = sdf

    def trace_factory(self) -> TechnicalAnalysisTraceFactory:
        return TechnicalAnalysisTraceFactory(self)

    @property
    def instrument_name(self):
        return self.instrument.name

    @classmethod
    def init_from_dataloader(cls, instrument: "Instrument", dataloader):
        try:
            return cls(
                instrument,
                StockDataFrame.retype(
                    pd.DataFrame(dataloader)
                    .rename(columns={"valuation_date": "date"})
                    .set_index("date")
                    .sort_index()
                    .bfill()
                ),
            )
        except KeyError:
            return cls(instrument, StockDataFrame(columns=["date", "close", "volume", "calculated"]))

    @classmethod
    def init_full_from_instrument(
        cls, instrument: "Instrument", from_date: date | None = None, to_date: date | None = None
    ):
        return cls.init_from_dataloader(
            instrument,
            instrument.__class__.objects.filter(id=instrument.id).dl.market_data(from_date=from_date, to_date=to_date),
        )

    @classmethod
    def init_close_from_instrument(
        cls, instrument: "Instrument", from_date: date | None = None, to_date: date | None = None
    ):
        return cls.init_from_dataloader(
            instrument,
            instrument.__class__.objects.filter(id=instrument.id).dl.market_data(
                values=[MarketData.CLOSE], from_date=from_date, to_date=to_date
            ),
        )

    def add_sma(self, window, field="close"):
        self._sdf[[f"{field}_{window}_sma"]]

    def add_roc(self, window, field="close"):
        self._sdf[[f"{field}_{window}_roc"]]

    def add_shift(self, window, field="close"):
        self._sdf[[f"{field}_{window}_s"]]

    def add_delta(self, window, field="close"):
        self._sdf[[f"{field}_{window}_d"]]

    def add_drawdown(self, field="close"):
        self._sdf["drawdown"] = self._sdf[field] - self._sdf[field].cummax()

    def add_macd(self):
        self._sdf[["macd", "macdh", "macds"]]

    def add_bollinger(self, window=14):
        self._sdf[[f"boll_{window}", f"boll_ub_{window}", f"boll_lb_{window}"]]
        self._sdf.bfill()

    def add_energy_index(self):
        self._sdf[["cr", "cr-ma1", "cr-ma2", "cr-ma3"]]

    def add_williams_index(self, window=14):
        self._sdf[[f"wr_{window}"]]

    def add_volume_variation_index(self, window=26):
        self._sdf[[f"vr_{window}"]]

    def add_return(self, return_type: Literal["log"] | Literal["normal"] = "normal"):
        if return_type == "log":
            self._sdf[["log-ret"]]
        elif return_type == "normal":
            self._sdf["ret"] = (self._sdf["close"] - self._sdf["close_-1_s"]) / self._sdf["close_-1_s"]

    def add_cumulative_return(self, return_type: Literal["log"] | Literal["normal"] = "normal"):
        if return_type == "log":
            self._sdf["cum-log-ret"] = (1 + self._sdf[["log-ret"]]).cumprod() - 1
        elif return_type == "normal":
            self.add_return("normal")
            self._sdf["cum-ret"] = (1 + self._sdf[["ret"]]).cumprod() - 1

    def get_performance_between_dates(self, from_date: date, to_date: date | None = None) -> float:
        if to_date is None:
            to_date = date.today()

        close = self.df[(self.df.index >= (pd.Timestamp(from_date) - BDay(1)).date()) & (self.df.index <= to_date)][
            "close"
        ]
        if close.empty:
            return 0
        return (close[-1] - close[0]) / close[0]

    def get_performance_year_to_date(self) -> float:
        return self.get_performance_between_dates(from_date=date.today().replace(month=1, day=1))

    def get_performance_months(self, months: int) -> float:
        return self.get_performance_between_dates(from_date=date.today() - timedelta(30 * months))

    def get_performances_dataframe(self, freq: Literal["Y"] | Literal["ME"]) -> pd.DataFrame:
        df = self.df
        df.index = pd.to_datetime(df.index)
        df = df.groupby(pd.Grouper(freq=freq)).last()
        df["performance"] = df["close"].pct_change()
        return df[["close", "performance"]]

    def get_annual_performances_dataframe(self):
        return self.get_performances_dataframe("Y")

    def get_monthly_performances_dataframe(self):
        return self.get_performances_dataframe("ME")

    @property
    def df(self):
        return self._sdf
