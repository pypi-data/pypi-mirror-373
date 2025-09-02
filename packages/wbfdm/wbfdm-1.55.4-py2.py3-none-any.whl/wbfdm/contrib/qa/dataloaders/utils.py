from typing import TYPE_CHECKING

from pypika import Case, Column, Criterion, Field, MSSQLQuery, Table
from pypika.terms import ValueWrapper

if TYPE_CHECKING:
    from pypika.queries import CreateQueryBuilder, QueryBuilder
    from pypika.terms import Term


def compile_source(source: str) -> "Term":
    return ValueWrapper(source).as_("source")


SOURCE_DS2 = compile_source("qa-ds2")
SOURCE_RKD = compile_source("qa-rkd")
SOURCE_IBES = compile_source("qa-ibes")


def create_table(tablename: "str", *columns: "Column") -> tuple[Table, "CreateQueryBuilder"]:
    table = Table(tablename)
    return table, MSSQLQuery.create_table(table).columns(*columns)


def get_currency_fx_rate(
    query: "QueryBuilder", alias_prefix: str, from_ccy: str | Field, to_ccy: str | Field, fx_date: str | Criterion
) -> tuple["QueryBuilder", Criterion]:
    """Gets the currency exchange rate with fallback to 1 if rate not found.

    Extends a query with FX table joins to retrieve currency conversion rates. Uses left joins
    and provides a default rate of 1 when no conversion rate exists, effectively making the
    conversion neutral in such cases.

    Warning:
        The alias_prefix must be unique across the entire query chain. Reusing the same
        prefix in multiple calls will cause table alias conflicts, leading to incorrect
        results or SQL errors. Each call to this function should use a distinct prefix.

    Args:
        query (QueryBuilder): Base query to extend with FX-related joins
        alias_prefix (str): Prefix for table aliases to prevent naming conflicts in joins.
                          Must be unique across the entire query chain.
        from_ccy (str | pk.Field): Source currency code or Field to convert from
        to_ccy (str | pk.Field): Target currency code or Field to convert to
        fx_date (Any): Date for which to get the exchange rate

    Returns:
        tuple[QueryBuilder, pk.Criterion]: A tuple containing:
            - Modified query with FX table joins
            - Coalesced midrate (defaults to 1 if no rate found)
    """
    # Create aliased FX tables to avoid naming conflicts in complex queries
    fx_code = Table("DS2FxCode", alias=f"{alias_prefix}DS2FxCode")
    fx_rate = Table("DS2FxRate", alias=f"{alias_prefix}DS2FxRate")
    # Build query with FX table joins
    query = (
        query
        # Join FX code table matching currencies and ensuring SPOT rate type
        .left_join(fx_code)
        .on((fx_code.FromCurrCode == from_ccy) & (fx_code.ToCurrCode == to_ccy) & (fx_code.RateTypeCode == "SPOT"))
        # Join FX rate table matching internal code and date
        .left_join(fx_rate)
        .on((fx_rate.ExRateIntCode == fx_code.ExRateIntCode) & (fx_rate.ExRateDate == fx_date))
    )

    # Return query and coalesced rate (falls back to 1 if no rate found)
    fx = Case().when(from_ccy == to_ccy, 1).else_(fx_rate.midrate)
    return (query, fx)
