from datetime import date
from typing import Iterator

from wbcore.contrib.dataloader.dataloaders import DataloaderProxy

from wbfdm.dataloaders.protocols import (
    AdjustmentsProtocol,
    CorporateActionsProtocol,
    ESGControversyProtocol,
    ESGProtocol,
    FinancialsProtocol,
    FXRateProtocol,
    MarketDataProtocol,
    OfficersProtocol,
    ReportDateProtocol,
    StatementsProtocol,
)
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

from .cache import Cache


def _market_data_row_parser(row):
    if row.get("close") is None and (bid := row.get("bid")) is not None and (ask := row.get("ask")) is not None:
        price = (bid + ask) / 2
        row["close"] = price
        row["open"] = price
        row["low"] = price
        row["high"] = price
    return row


class InstrumentDataloaderProxy(
    DataloaderProxy[
        FXRateProtocol
        | AdjustmentsProtocol
        | MarketDataProtocol
        | CorporateActionsProtocol
        | OfficersProtocol
        | StatementsProtocol
        | FinancialsProtocol
        | ReportDateProtocol
        | ESGControversyProtocol
        | ESGProtocol
    ]
):
    def reporting_dates(self, only_next: bool = True) -> Iterator[ReportDateDataDict]:
        for dl in self.iterate_dataloaders("reporting_dates"):
            yield from dl.reporting_dates(only_next=only_next)

    def fx_rates(
        self,
        from_date: date,
        to_date: date,
        target_currency: str,
    ) -> Iterator[FXRateDict]:
        for dl in self.iterate_dataloaders("fx_rates"):
            yield from dl.fx_rates(from_date, to_date, target_currency)

    def adjustments(self, from_date: date | None = None, to_date: date | None = None) -> Iterator[AdjustmentDataDict]:
        for dl in self.iterate_dataloaders("adjustments"):
            yield from dl.adjustments(from_date=from_date, to_date=to_date)

    def market_data(
        self,
        values: list[MarketData] | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        exact_date: date | None = None,
        frequency: Frequency = Frequency.DAILY,
        target_currency: str | None = None,
        apply_fx_rate: bool = True,
    ) -> Iterator[MarketDataDict]:
        if not values:
            values = list(MarketData)
        for dl in self.iterate_dataloaders("market_data"):
            yield from map(
                lambda row: _market_data_row_parser(row),
                dl.market_data(
                    values=values,
                    from_date=from_date,
                    to_date=to_date,
                    exact_date=exact_date,
                    frequency=frequency,
                    target_currency=target_currency,
                    apply_fx_rate=apply_fx_rate,
                ),
            )

    def corporate_actions(
        self, from_date: date | None = None, to_date: date | None = None
    ) -> Iterator[CorporateActionDataDict]:
        for dl in self.iterate_dataloaders("corporate_actions"):
            yield from dl.corporate_actions(from_date=from_date, to_date=to_date)

    def officers(self) -> Iterator[OfficerDataDict]:
        for dl in self.iterate_dataloaders("officers"):
            yield from dl.officers()

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
    ) -> Iterator[StatementDataDict]:
        for dl in self.iterate_dataloaders("statements"):
            yield from dl.statements(
                statement_type=statement_type,
                from_date=from_date,
                to_date=to_date,
                from_year=from_year,
                to_year=to_year,
                period_type=period_type,
                data_type=data_type,
                financials=financials,
                target_currency=target_currency,
            )

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
    ) -> Iterator[FinancialDataDict]:
        for dl in self.iterate_dataloaders("financials"):
            yield from dl.financials(
                values=values,
                from_date=from_date,
                to_date=to_date,
                from_year=from_year,
                to_year=to_year,
                from_index=from_index,
                to_index=to_index,
                from_valid=from_valid,
                to_valid=to_valid,
                period_type=period_type,
                calendar_type=calendar_type,
                series_type=series_type,
                data_type=data_type,
                estimate_type=estimate_type,
                target_currency=target_currency,
            )

    def esg_controversies(self) -> Iterator[ESGControversyDataDict]:
        for dl in self.iterate_dataloaders("esg_controversies"):
            yield from dl.esg_controversies()

    def esg(
        self,
        values: list[ESG],
    ) -> Iterator[ESGDataDict]:
        for dl in self.iterate_dataloaders("esg"):
            if (
                (cache_identifier_key := getattr(dl, "CACHE_IDENTIFIER_KEY", None))
                and (cache_symbol_key := getattr(dl, "CACHE_SYMBOL_KEY", None))
                and (cache_value_key := getattr(dl, "CACHE_VALUE_KEY", None))
            ):
                cache = Cache(
                    identifier_key=cache_identifier_key,
                    symbol_key=cache_symbol_key,
                    value_key=cache_value_key,
                    timeout=getattr(dl, "CACHE_TIMEOUT", 10 * 24 * 3600),  # default to 10days
                )
                cache.initialize(dl.entity_ids, [v.value for v in values])

                yield from cache.fetch_from_cache()
                if len(cache.missing_symbols) > 0 and len(cache.missing_ids) > 0:
                    dl.entities = dl.entities.filter(id__in=cache.missing_ids)
                    yield from map(
                        lambda row: cache.write(row),
                        dl.esg(values=[v for v in values if v.value in cache.missing_symbols]),
                    )
                cache.close()
            else:
                yield from dl.esg(values=values)
