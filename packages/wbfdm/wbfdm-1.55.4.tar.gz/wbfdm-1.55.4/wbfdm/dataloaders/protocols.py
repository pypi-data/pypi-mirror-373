from datetime import date
from typing import Iterator, Protocol

from wbfdm.dataloaders.types import (
    AdjustmentDataDict,
    CorporateActionDataDict,
    ESGControversyDataDict,
    ESGDataDict,
    FinancialDataDict,
    FXRateDict,
    MarketDataDict,
    OfficerDataDict,
    ReportDateDataDict,
    StatementDataDict,
)
from wbfdm.enums import (
    ESG,
    CalendarType,
    DataType,
    EstimateType,
    Financial,
    Frequency,
    MarketData,
    PeriodType,
    SeriesType,
    StatementType,
)


class ReportDateProtocol(Protocol):
    def reporting_dates(self, only_next: bool = True) -> Iterator[ReportDateDataDict]: ...


class AdjustmentsProtocol(Protocol):
    def adjustments(
        self, from_date: date | None = None, to_date: date | None = None
    ) -> Iterator[AdjustmentDataDict]: ...


class FXRateProtocol(Protocol):
    def fx_rates(
        self,
        from_date: date,
        to_date: date,
        target_currency: str,
    ) -> Iterator[FXRateDict]: ...


class MarketDataProtocol(Protocol):
    def market_data(
        self,
        values: list[MarketData] = [MarketData.CLOSE],
        from_date: date | None = None,
        to_date: date | None = None,
        exact_date: date | None = None,
        frequency: Frequency = Frequency.DAILY,
        target_currency: str | None = None,
        apply_fx_rate: bool = True,
    ) -> Iterator[MarketDataDict]: ...


class CorporateActionsProtocol(Protocol):
    def corporate_actions(
        self, from_date: date | None = None, to_date: date | None = None
    ) -> Iterator[CorporateActionDataDict]: ...


class OfficersProtocol(Protocol):
    def officers(self) -> Iterator[OfficerDataDict]: ...


class StatementsProtocol(Protocol):
    def statements(
        self,
        statement_type: StatementType | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        from_year: int | None = None,
        to_year: int | None = None,
        period_type: PeriodType = PeriodType.ALL,
        data_type: DataType = DataType.STANDARDIZED,
        financials: list[Financial] | None = None,
        target_currency: str | None = None,
    ) -> Iterator[StatementDataDict]: ...


class FinancialsProtocol(Protocol):
    def financials(
        self,
        values: list[Financial],
        from_date: date | None = None,
        to_date: date | None = None,
        from_year: int | None = None,
        to_year: int | None = None,
        from_index: int | None = None,
        to_index: int | None = None,
        from_valid: date | None = None,
        to_valid: date | None = None,
        period_type: PeriodType = PeriodType.ANNUAL,
        calendar_type: CalendarType = CalendarType.FISCAL,
        series_type: SeriesType = SeriesType.COMPLETE,
        data_type: DataType = DataType.STANDARDIZED,
        estimate_type: EstimateType = EstimateType.VALID,
        target_currency: str | None = None,
    ) -> Iterator[FinancialDataDict]: ...


class ESGControversyProtocol(Protocol):
    def esg_controversies(self) -> Iterator[ESGControversyDataDict]: ...


class ESGProtocol(Protocol):
    def esg(
        self,
        values: list[ESG],
    ) -> Iterator[ESGDataDict]: ...
