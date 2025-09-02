from datetime import date
from typing import Literal, TypedDict

from typing_extensions import NotRequired


class BaseDict(TypedDict):
    """
    Represents a base dictionary with common fields.

    Attributes:
        id: str | int
            The unique identifier.
        external_id: str | int
            The external identifier.
        source: str
            The source of the data.
        currency: str
            The currency used.
    """

    id: str | int
    instrument_id: int
    external_id: str | int
    source: str
    currency: NotRequired[str]


class FXRateDict(TypedDict):
    currency_pair: str
    fx_date: date
    fx_rate: float


class MarketDataDict(BaseDict):
    """
    Represents a dictionary for daily valuation data.

    Attributes:
        valuation_date: date
            The date of valuation.
        external_identifier: str
            The external identifier of the instrument
        open: float | None
            The opening value (if available).
        close: float | None
            The closing value (if available).
        high: float | None
            The highest value (if available).
        low: float | None
            The lowest value (if available).
        bid: float | None
            The bid value (if available).
        ask: float | None
            The ask value (if available).
        volume: float | None
            The volume (if available).
        market_cap: float | None
            The market capitalization (if available).
    """

    valuation_date: date
    external_identifier: str

    open: NotRequired[float]
    close: NotRequired[float]
    high: NotRequired[float]
    low: NotRequired[float]
    bid: NotRequired[float]
    ask: NotRequired[float]
    volume: NotRequired[float]
    market_cap: NotRequired[float]
    calculated: NotRequired[bool]
    fx_rate: NotRequired[float]
    unadjusted_close: NotRequired[float]
    unadjusted_outstanding_shares: NotRequired[float | int]


class CorporateActionDataDict(BaseDict):
    old_shares: float
    new_shares: float

    action_code: str
    event_code: str
    valuation_date: date


class AdjustmentDataDict(BaseDict):
    adjustment_factor: float
    cumulative_adjustment_factor: float

    adjustment_date: date
    adjustment_end_date: date


class FinancialDataDict(BaseDict):
    """
    Represents a dictionary for financial data.

    Attributes:
        period_end_date: date
            The period end date / The reporting date
        valid_until: date | None
            The validity date (if available).
        fiscal_year: int
            The fiscal year.
        interim: int
            The interim period. 0 means yearly data.
        estimate: bool
            Indicates if the data is an estimate or actual data
        reported: bool
            Indicates if the data is reported or standardized
        value: str | float | int
            The value.
        financial: str
            The type of financial data.
    """

    valid_until: NotRequired[date]
    year: int
    interim: int
    estimate: NotRequired[bool]
    # reported: bool

    value: str | float | int
    financial: str


class StatementDataDict(BaseDict):
    """
    Represents a dictionary for statement data

    Attributes:
        external_code: str
            The code that is used by the data vendor to identify this type of financial
        external_ordering: int
            The ordering that is supplied by the data vendor to sort this financial
        external_description: str
            The description supplied by the data vendor to describe this financial
        period_end_date: date
            The period end date / The reporting date
        year: int
            The financial year of the statement.
        interim: int
            The interim period. 0 means yearly data.
        reported: bool
            Indicates if the data is reported or standardized.
        value: float | int
            The value of the datapoint of the statement.

    """

    external_code: str
    external_ordering: int
    external_description: str

    period_end_date: date
    year: int
    interim: int
    value: float | int
    reported: bool


class ReportDateDataDict(TypedDict):
    instrument_id: int
    external_id: int
    source: str
    period_end_date: date
    is_interim: bool
    start_date: date
    end_date: date
    market_phase: Literal["before_market"] | Literal["after_market"] | None
    status: Literal["confirmed"] | Literal["tentative"]


class OfficerDataDict(TypedDict):
    """
    Represents a dictionary for officers

    Attributes:
        instrument_id: int
            An identifier to uniquely identify the instrument linked to an officer
        position: str
            The title of the position
        name: str
            The name of the officer
        age: int
            The current age of the officer
        sex: "M" | "F"
            Indicates the sex of the officer
        start: date
            The date when the officer started the position
    """

    instrument_id: int
    position: str
    name: str
    age: int
    sex: Literal["M"] | Literal["F"]
    start: date


class ESGDataDict(TypedDict):
    instrument_id: int
    factor_code: str
    value: str | float | int | None


class ESGControversyDataDict(TypedDict):
    id: str | int
    instrument_id: str
    headline: str
    narrative: str
    source: str
    response: str
    status: str | None  # TODO: Move to enum?
    type: str | None  # TODO: Move to enum?
    assessment: str | None  # TODO: Move to enum?
    review: date | None
    initiated: date | None
    flag: str | None  # TODO: Move to enum?
