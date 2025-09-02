from datetime import date
from enum import Enum
from typing import Iterator

from django.db import connections
from jinjasql import JinjaSql  # type: ignore
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbcore.contrib.dataloader.utils import dictfetchall

from wbfdm.dataloaders.protocols import StatementsProtocol
from wbfdm.dataloaders.types import StatementDataDict
from wbfdm.enums import DataType, Financial, PeriodType, StatementType


class RKDStatementType(Enum):
    INCOME_STATEMENT = 1
    CASHFLOW_STATEMENT = 2
    BALANCE_SHEET = 3


class RKDFinancial(Enum):
    EMPLOYEES = "METL"
    CASH_AND_SHORT_TERM_INVESTMENT = "SCSI"
    DILUTED_WEIGHTED_AVG_SHARES = "SDWS"
    TOTAL_DEBT = "STLD"
    NET_DEBT = "SNTD"
    STOCK_COMPENSATION = "VSCP"
    TANGIBLE_BOOK_VALUE_PER_SHARE = "STBP"
    REVENUE = "RTLR"
    SHARES_OUTSTANDING = "QTCO"
    EPS = "SDAI"
    CASH_FLOW_FROM_OPERATIONS = "OTLO"
    CAPEX = "SCEX"


reported_sql = """
    SELECT
        CONCAT(val.Code, '-', CONVERT(DATE, val.PerEndDt), '-', fil.InterimNo, '-', val.LineID) as id,
        val.LineID as external_ordering,
        itemsub.Desc_ as external_description,
        itemsub.StdCOA as external_code,
        val.Code as external_identifier,
        CONVERT(DATE, val.PerEndDt) as period_end_date,
        per.Fyr as year,
        fil.InterimNo as interim,
        CASE
            when fil.PerTypeCode = 1 THEN 'Y'
            when fil.PerTypeCode = 2 THEN 'Q'
            when fil.PerTypeCode = 3 THEN 'S'
            when fil.PerTypeCode = 4 THEN 'T'
            when fil.PerTypeCode = 5 THEN 'Q'
            when fil.PerTypeCode = 6 THEN 'Y'
        END as period_type,
        CASE
            WHEN fil.UnitsConvToCode = 'T' AND item.ItemPrecision in (1,2) THEN val.Value_ * 1e3
            WHEN fil.UnitsConvToCode = 'M' AND item.ItemPrecision in (1,2) THEN val.Value_ * 1e6
            WHEN fil.UnitsConvToCode = 'B' AND item.ItemPrecision in (1,2) THEN val.Value_ * 1e9
            ELSE val.Value_
        END as value,
        'qa-rkd' as source,
        CASE
            WHEN item.IsCurrency = 1 THEN code.Desc_
            ELSE NULL
        END AS currency

    FROM RKDFndCSFFinVal AS val

    JOIN RKDFndCSFStmt AS stmt ON
        val.Code = stmt.Code
        AND val.PerEndDt = stmt.PerEndDt
        AND val.PerTypeCode = stmt.PerTypeCode
        AND val.StmtDt = stmt.StmtDt
        AND val.StmtTypeCode = stmt.StmtTypeCode
        AND stmt.CompStmtCode = 1

    JOIN RKDFndCSFPerFiling AS fil ON
        stmt.Code = fil.Code
        AND stmt.PerEndDt = fil.PerEndDt
        AND stmt.PerTypeCode = fil.PerTypeCode
        AND stmt.StmtDt = fil.StmtDt

    LEFT JOIN RKDFNDCSFITEMSUB AS itemsub ON
        val.Code = itemsub.Code
        AND val.PerTypeCode = itemsub.PerTypeCode
        AND val.StmtTypeCode = itemsub.StmtTypeCode
        AND val.LineID = itemsub.LineID

    LEFT JOIN RKDFndCSFItem AS item ON
        itemsub.Item = item.Item

    LEFT JOIN RKDFndCode AS code ON
        fil.CurrConvToCode = code.Code
        AND code.Type_ = 58

    LEFT JOIN RKDFndCsfPeriod AS per ON
        per.Code = fil.Code
        AND per.PerEndDt = fil.PerEndDt
        AND per.PerTypeCode = (
            CASE
                WHEN fil.PerTypeCode = 1 THEN 1
                WHEN fil.PerTypeCode in (2,3,4,5) THEN 5
            END
        )

    WHERE
        val.Code in (
        {% for instrument in instruments %}
            {{instrument}} {% if not loop.last %}, {% endif %}
        {% endfor %})
        AND val.StmtTypeCode = {{ statement_type }}
        {% if from_year %}AND per.Fyr >= {{ from_year }} {% endif %}
        {% if to_year %}AND per.Fyr <= {{ to_year }} {% endif %}
        {% if from_date %}AND val.PerEndDt >= {{ from_date }} {% endif %}
        {% if to_date %}AND val.PerEndDt <= {{ to_date }} {% endif %}
        {% if period_type == 'interim' %}AND fil.InterimNo > 0{% elif period_type == 'annual' %}AND (fil.InterimNo = 0 OR fil.InterimNo IS NULL){% endif %}
    ORDER BY val.LineID
"""
standardized_sql = """
    SELECT
        CONCAT(val.Code, '-', CONVERT(DATE, val.PerEndDt), '-', fil.InterimNo, '-', item.LineID) as id,
        item.LineID as external_ordering,
        item.Desc_ as external_description,
        item.COA as external_code,
        val.Code as external_identifier,
        CONVERT(DATE, val.PerEndDt) as period_end_date,
        per.Fyr as year,
        CASE
            when fil.PerTypeCode = 1 THEN 'Y'
            when fil.PerTypeCode = 2 THEN 'Q'
            when fil.PerTypeCode = 3 THEN 'S'
            when fil.PerTypeCode = 4 THEN 'T'
            when fil.PerTypeCode = 5 THEN 'Q'
            when fil.PerTypeCode = 6 THEN 'Y'
        END as period_type,
        fil.InterimNo as interim,
        CASE
            WHEN fil.UnitsConvToCode = 'T' AND item.ItemPrecision in (1,2) THEN val.Value_ * 1e3
            WHEN fil.UnitsConvToCode = 'M' AND item.ItemPrecision in (1,2) THEN val.Value_ * 1e6
            WHEN fil.UnitsConvToCode = 'B' AND item.ItemPrecision in (1,2) THEN val.Value_ * 1e9
            ELSE val.Value_
        END as value,
        'qa-rkd' as source,
        CASE
            WHEN item.IsCurrency = 1 THEN code.Desc_
            ELSE NULL
        END AS currency

    FROM RKDFndStdFinVal AS val

    LEFT JOIN RKDFndStdPeriod AS per ON
        per.Code = val.Code
        AND per.PerEndDt = val.PerEndDt
        AND per.PerTypeCode = (
            CASE
                WHEN val.PerTypeCode = 1 THEN 1
                WHEN val.PerTypeCode in (2,3,4,5) THEN 5
            END
        )
        AND per.PerEnddt = (
            SELECT TOP 1 per2.PerEndDt
            FROM RKDFndStdPeriod AS per2
            WHERE per.Code = per2.Code
              AND per.PerTypeCode = per2.PerTypeCode
              AND per.Fyr = per2.Fyr
              AND (
                per2.InterimNo = per.InterimNo
                    OR (
                    per2.InterimNo IS NULL AND per.InterimNo IS NULL
                    )
                )
            ORDER BY per2.PerEndDt DESC
        )

    JOIN RKDFndStdStmt AS stmt ON
        val.Code = stmt.Code
        AND val.PerEndDt = stmt.PerEndDt
        AND val.PerTypeCode = stmt.PerTypeCode
        AND val.StmtDt = stmt.StmtDt
        AND val.StmtTypeCode = stmt.StmtTypeCode
        AND stmt.CompStmtCode = 1
        AND stmt.StmtDt = (
            select top 1 stmt2.StmtDt
            from RKDFndStdStmt as stmt2
            where stmt2.Code = stmt.Code
                and stmt2.PerEndDt = stmt.PerEndDt
                and stmt2.PerTypeCode = stmt.PerTypeCode
                and stmt2.StmtTypeCode = stmt.StmtTypeCode
                and stmt2.CompStmtCode = stmt.CompStmtCode
            order by stmt2.StmtDt desc
        )

    JOIN RKDFndStdPerFiling AS fil ON
        stmt.Code = fil.Code
        AND stmt.PerEndDt = fil.PerEndDt
        AND stmt.PerTypeCode = fil.PerTypeCode
        AND stmt.StmtDt = fil.StmtDt

    LEFT JOIN RKDFndStdItem AS item ON
        val.Item = item.Item

    LEFT JOIN RKDFndCode AS code ON
        fil.CurrConvToCode = code.Code
        AND code.Type_ = 58

    WHERE
        val.Code in (
        {% for instrument in instruments %}
            {{instrument}} {% if not loop.last %}, {% endif %}
        {% endfor %})
        {% if statement_type %} AND val.StmtTypeCode = {{ statement_type }}{% endif %}
        {% if from_year %}AND per.Fyr >= {{ from_year }} {% endif %}
        {% if to_year %}AND per.Fyr <= {{ to_year }} {% endif %}
        {% if from_date %}AND val.PerEndDt >= {{ from_date }} {% endif %}
        {% if to_date %}AND val.PerEndDt <= {{ to_date }} {% endif %}
        {% if period_type == 'interim' %}AND fil.InterimNo > 0{% elif period_type == 'annual' %}AND (fil.InterimNo = 0 OR fil.InterimNo IS NULL){% endif %}
        {% if external_codes %}
            AND item.COA in (
                {% for external_code in external_codes %}
                    {{ external_code }} {% if not loop.last %}, {% endif %}
                {% endfor %}
            )
        {% endif %}
    ORDER BY item.LineID
"""


class RKDStatementsDataloader(StatementsProtocol, Dataloader):
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
        lookup = {k: v for k, v in self.entities.values_list("dl_parameters__statements__parameters", "id")}
        sql = reported_sql if data_type is DataType.REPORTED else standardized_sql
        if not financials:
            financials = []
        external_codes = [RKDFinancial[fin.name].value for fin in financials if fin.name in RKDFinancial.__members__]

        query, bind_params = JinjaSql(param_style="format").prepare_query(
            sql,
            {
                "instruments": lookup.keys(),
                "statement_type": RKDStatementType[statement_type.name].value if statement_type else None,
                "from_year": from_year,
                "to_year": to_year,
                "from_date": from_date,
                "to_date": to_date,
                "period_type": period_type.value,
                "external_codes": external_codes,
            },
        )
        with connections["qa"].cursor() as cursor:
            cursor.execute(
                query,
                bind_params,
            )
            for row in dictfetchall(cursor):
                if row["interim"] is None:
                    row["interim"] = 0
                # sometime we get None for the year. We default to the period end date year then
                row["year"] = int(row["year"] or row["period_end_date"].year)
                row["instrument_id"] = lookup[row["external_identifier"]]
                if financials:
                    try:
                        row["financial"] = Financial[RKDFinancial(row["external_code"]).name].value
                    except (ValueError, KeyError):
                        continue
                yield row
