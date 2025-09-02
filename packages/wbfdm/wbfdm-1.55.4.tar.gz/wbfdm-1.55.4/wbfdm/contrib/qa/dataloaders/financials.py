from datetime import date
from itertools import batched  # type: ignore
from typing import Iterator

from django.db import connections
from django.template.loader import get_template
from jinjasql import JinjaSql  # type: ignore
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbcore.contrib.dataloader.utils import dictfetchall

from wbfdm.dataloaders.protocols import FinancialsProtocol
from wbfdm.dataloaders.types import FinancialDataDict
from wbfdm.enums import (
    CalendarType,
    DataType,
    EstimateType,
    Financial,
    PeriodType,
    SeriesType,
)


class IBESFinancialsDataloader(FinancialsProtocol, Dataloader):
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
        lookup = {k: v for k, v in self.entities.values_list("dl_parameters__financials__parameters", "id")}
        for batch in batched(lookup.keys(), 1000):
            sql = ""
            if series_type == SeriesType.COMPLETE:
                sql = "qa/sql/ibes/complete.sql"
                if calendar_type == CalendarType.CALENDAR:
                    sql = "qa/sql/ibes/calendarized.sql"

            elif series_type == SeriesType.FULL_ESTIMATE:
                sql = "qa/sql/ibes/estimates.sql"

            query, bind_params = JinjaSql(param_style="format").prepare_query(
                get_template(sql, using="jinja").template,
                {
                    "instruments": batch,
                    "financials": [financial.value for financial in values],
                    "estimate_type": estimate_type.value,
                    "from_date": from_date,
                    "to_date": to_date,
                    "from_year": from_year,
                    "to_year": to_year,
                    "from_index": from_index,
                    "to_index": to_index,
                    "from_valid": from_valid,
                    "to_valid": to_valid,
                    "period_type": period_type.value,
                },
            )
            with connections["qa"].cursor() as cursor:
                cursor.execute(
                    query,
                    bind_params,
                )
                for row in dictfetchall(cursor):
                    row["instrument_id"] = lookup[row["external_identifier"]]
                    row["estimate"] = bool(row["estimate"])
                    row["value"] = row.get("value", None)
                    row["difference_pct"] = row.get("difference_pct", 0)
                    row["value_high"] = row.get("value_high", row["value"])
                    row["value_low"] = row.get("value_low", row["value"])
                    row["value_amount"] = row.get("value_amount", row["value"])
                    row["value_stdev"] = row.get("value_stdev", row["value"])
                    yield row
