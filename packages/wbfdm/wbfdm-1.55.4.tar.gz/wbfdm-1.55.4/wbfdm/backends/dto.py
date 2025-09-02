from dataclasses import dataclass
from datetime import date


@dataclass
class PriceDTO:
    pk: str
    instrument: int
    date: date
    open: float
    close: float
    high: float
    low: float
    volume: float
    market_capitalization: float
    outstanding_shares: float

    @property
    def net_value(self) -> float:
        return self.close


@dataclass
class AdjustmentDTO:
    pk: str
    date: date
    adjustment_factor: float
    cumulative_adjustment_factor: float


@dataclass
class DividendDTO:
    pk: str
    rate: float
    ex_dividend_date: date
    payment_date: date
