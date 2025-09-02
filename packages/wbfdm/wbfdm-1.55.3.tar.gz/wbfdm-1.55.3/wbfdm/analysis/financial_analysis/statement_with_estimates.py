import pandas as pd

from wbfdm.enums import CalendarType, Financial, MarketData
from wbfdm.models import Instrument

from .utils import FinancialAnalysisResult, Loader


class StatementWithEstimates:
    """
    Utility class to hold all the potentials statement with estimates table as self contained properties
    """

    def __init__(self, instrument: Instrument, calendar_type: CalendarType = CalendarType.FISCAL):
        self.instrument = instrument
        self.calendar_type = calendar_type

    @property
    def credit_with_estimates(self) -> FinancialAnalysisResult:
        values = [
            Financial.NET_DEBT,
            Financial.EBITDA,
            Financial.TOTAL_DEBT,
            Financial.FREE_CASH_FLOW,
            Financial.CASH_FLOW_FROM_OPERATIONS,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        empty_series = pd.Series(dtype="float64", index=df.index)

        df["net_debt_ebitda_ratio"] = df.get(Financial.NET_DEBT.value, empty_series) / df.get(
            Financial.EBITDA.value, empty_series
        )
        df["total_debt_ebitda_ratio"] = df.get(Financial.TOTAL_DEBT.value, empty_series) / df.get(
            Financial.EBITDA.value, empty_series
        )
        df["fcf_total_debt_ratio"] = df.get(Financial.FREE_CASH_FLOW.value, empty_series) / df.get(
            Financial.TOTAL_DEBT.value, empty_series
        )
        df["cfo_total_debt_ratio"] = df.get(Financial.CASH_FLOW_FROM_OPERATIONS.value, empty_series) / df.get(
            Financial.TOTAL_DEBT.value, empty_series
        )

        df.drop(columns=list(map(lambda x: x.value, values)), inplace=True, errors="ignore")

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def long_term_solvency_with_estimates(self) -> FinancialAnalysisResult:
        values = [
            Financial.TOTAL_DEBT,
            Financial.SHAREHOLDERS_EQUITY,
            Financial.WORKING_CAPITAL,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        empty_series = pd.Series(dtype="float64", index=df.index)

        df["total_debt_equity_ratio"] = df.get(Financial.TOTAL_DEBT.value, empty_series) / df.get(
            Financial.SHAREHOLDERS_EQUITY.value, empty_series
        )
        df["total_debt_capital_ratio"] = df.get(Financial.TOTAL_DEBT.value, empty_series) / df.get(
            Financial.WORKING_CAPITAL.value, empty_series
        )

        df.drop(columns=list(map(lambda x: x.value, values)), inplace=True, errors="ignore")

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def short_term_liquidity_with_estimates(self) -> FinancialAnalysisResult:
        values = [
            Financial.CURRENT_ASSETS,
            Financial.CURRENT_LIABILITIES,
            # Financial.INVENTORY, --> Needed for the quick ratio
            Financial.CASH_FLOW_FROM_OPERATIONS,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        empty_series = pd.Series(dtype="float64", index=df.index)

        df["current_ratio"] = df.get(Financial.CURRENT_ASSETS.value, empty_series) / df.get(
            Financial.CURRENT_LIABILITIES.value, empty_series
        )
        df["cash_from_operation_current_liabilities_ratio"] = df.get(
            Financial.CASH_FLOW_FROM_OPERATIONS.value, empty_series
        ) / df.get(Financial.CURRENT_LIABILITIES.value, empty_series)
        # df["Cash Flow Margin (%)"] = (df["Inventory"] / df["Cost of goods sold"])  # Inventory does not exist
        df.drop(columns=list(map(lambda x: x.value, values)), inplace=True, errors="ignore")

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def asset_turnover_with_estimates(self) -> FinancialAnalysisResult:
        values = [
            Financial.REVENUE,
            Financial.TOTAL_ASSETS,
            Financial.COST_OF_GOODS_SOLD,
            # Financial.INVENTORY,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        empty_series = pd.Series(dtype="float64", index=df.index)

        df["asset_turnover"] = df.get(Financial.TOTAL_ASSETS.value, empty_series) / df.get(
            Financial.REVENUE.value, empty_series
        )
        # df["Cash Flow Margin (%)"] = (df["Inventory"] / df["Cost of goods sold"])  # Inventory does not exist
        df.drop(columns=list(map(lambda x: x.value, values)), inplace=True, errors="ignore")

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def cashflow_ratios_with_estimates(self) -> FinancialAnalysisResult:
        values = [
            Financial.CASH_FLOW_FROM_OPERATIONS,
            Financial.CURRENT_LIABILITIES,
            Financial.REVENUE,
            Financial.TOTAL_ASSETS,
            Financial.TOTAL_DEBT,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        empty_series = pd.Series(dtype="float64", index=df.index)

        df["current_liability_coverage_ratio"] = df.get(
            Financial.CASH_FLOW_FROM_OPERATIONS.value, empty_series
        ) / df.get(Financial.CURRENT_LIABILITIES.value, empty_series)
        df["cash_flow_margin"] = (
            df.get(Financial.CASH_FLOW_FROM_OPERATIONS.value, empty_series)
            / df.get(Financial.REVENUE.value, empty_series)
        ) * 100
        df["asset_efficiency_margin"] = (
            df.get(Financial.CASH_FLOW_FROM_OPERATIONS.value, empty_series)
            / df.get(Financial.TOTAL_ASSETS.value, empty_series)
        ) * 100
        df["net_debt_coverage_ratio"] = df.get(Financial.CASH_FLOW_FROM_OPERATIONS.value, empty_series) / df.get(
            Financial.TOTAL_DEBT.value, empty_series
        )
        df.drop(columns=list(map(lambda x: x.value, values)), inplace=True, errors="ignore")

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def margins_with_estimates(self) -> FinancialAnalysisResult:
        values = [
            Financial.REVENUE,
            Financial.GROSS_PROFIT,
            Financial.SGA_EXPENSES,
            Financial.EBITDA,
            Financial.EBIT,
            Financial.NET_INCOME,
            Financial.FREE_CASH_FLOW,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()
        empty_series = pd.Series(dtype="float64", index=df.index)

        df["gross_margin"] = (
            df.get(Financial.GROSS_PROFIT.value, empty_series) / df.get(Financial.REVENUE.value, empty_series)
        ) * 100
        df["sga_margin"] = (
            df.get(Financial.SGA_EXPENSES.value, empty_series) / df.get(Financial.REVENUE.value, empty_series)
        ) * 100
        df["ebitda_margin"] = (
            df.get(Financial.EBITDA.value, empty_series) / df.get(Financial.REVENUE.value, empty_series)
        ) * 100
        df["ebit_margin"] = (
            df.get(Financial.EBIT.value, empty_series) / df.get(Financial.REVENUE.value, empty_series)
        ) * 100
        df["net_income_margin"] = (
            df.get(Financial.NET_INCOME.value, empty_series) / df.get(Financial.REVENUE.value, empty_series)
        ) * 100
        df["free_cash_flow_margin"] = (
            df.get(Financial.FREE_CASH_FLOW.value, empty_series) / df.get(Financial.REVENUE.value, empty_series)
        ) * 100
        df.drop(columns=list(map(lambda x: x.value, values)), inplace=True, errors="ignore")

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def summary_with_estimate(self) -> FinancialAnalysisResult:
        values = [
            Financial.REVENUE,
            Financial.GROSS_PROFIT,
            Financial.GROSS_PROFIT_MARGIN,
            Financial.NET_INCOME_REPORTED,
            Financial.EPS_REPORTED,
            Financial.EPS,
            Financial.EBITDA,
            Financial.EBIT,
            Financial.CASH_FLOW_PER_SHARE,
            Financial.BOOK_VALUE_PER_SHARE,
            Financial.CAPEX,
            Financial.SHARES_OUTSTANDING,
            Financial.TOTAL_ASSETS,
            Financial.CURRENT_LIABILITIES,
            Financial.ENTERPRISE_VALUE,
            Financial.CASH_EQUIVALENTS,
        ]
        market_data_values = [
            MarketData.CLOSE,
            MarketData.MARKET_CAPITALIZATION,
        ]
        statement_values = [
            Financial.EMPLOYEES,
            Financial.CASH_AND_SHORT_TERM_INVESTMENT,
            Financial.DILUTED_WEIGHTED_AVG_SHARES,
            Financial.TOTAL_DEBT,
            Financial.NET_DEBT,
            Financial.STOCK_COMPENSATION,
            Financial.TANGIBLE_BOOK_VALUE_PER_SHARE,
        ]
        loader = Loader(
            self.instrument,
            values,
            calendar_type=self.calendar_type,
            market_data_values=market_data_values,
            statement_values=statement_values,
        )
        df = loader.load()
        empty_series = pd.Series(dtype="float64", index=df.index)

        if not df.empty:
            df[Financial.ENTERPRISE_VALUE.value] = (
                df.get(MarketData.MARKET_CAPITALIZATION.value, empty_series)
                + df.get(Financial.NET_DEBT.value, empty_series)
                - df.get(Financial.CASH_EQUIVALENTS.value, empty_series)
            )

            # Calculate a couple of variables
            yearly_df = df.loc[(slice(None), "Y", slice(None), slice(None)), :]
            yearly_empty_series = pd.Series(dtype="float64", index=yearly_df.index)

            quarterly_df = df.loc[
                (
                    slice(None),
                    df.index.isin(["Q1", "Q2", "Q3", "Q4", "S1", "S2", "T1", "T2", "T3"], level=1),
                    slice(None),
                    slice(None),
                ),
                :,
            ].sort_values(by="period_end_date")
            quarterly_empty_series = pd.Series(dtype="float64", index=quarterly_df.index)

            df["price_sales_ratio"] = pd.concat(
                [
                    yearly_df.get(MarketData.MARKET_CAPITALIZATION.value, yearly_empty_series)
                    / yearly_df.get(Financial.REVENUE.value, yearly_empty_series),
                    quarterly_df.get(MarketData.MARKET_CAPITALIZATION.value, quarterly_empty_series)
                    / quarterly_df.get(Financial.REVENUE.value, quarterly_empty_series)
                    .rolling(4, min_periods=1)
                    .sum(),
                ],
                axis=0,
            )
            df["price_earning_reported_ratio"] = pd.concat(
                [
                    yearly_df.get(MarketData.CLOSE.value, yearly_empty_series)
                    / yearly_df.get(Financial.EPS_REPORTED.value, yearly_empty_series),
                    quarterly_df.get(MarketData.CLOSE.value, quarterly_empty_series)
                    / quarterly_df.get(Financial.EPS_REPORTED.value, quarterly_empty_series)
                    .rolling(4, min_periods=1)
                    .sum(),
                ],
                axis=0,
            )
            df["price_earning_ratio"] = pd.concat(
                [
                    yearly_df.get(MarketData.CLOSE.value, yearly_empty_series)
                    / yearly_df.get(Financial.EPS.value, yearly_empty_series),
                    quarterly_df.get(MarketData.CLOSE.value, quarterly_empty_series)
                    / quarterly_df.get(Financial.EPS.value, quarterly_empty_series).rolling(4, min_periods=1).sum(),
                ],
                axis=0,
            )
            df["ev_ebitda_ratio"] = pd.concat(
                [
                    yearly_df.get(Financial.ENTERPRISE_VALUE.value, yearly_empty_series)
                    / yearly_df.get(Financial.EBITDA.value, yearly_empty_series),
                    quarterly_df.get(Financial.ENTERPRISE_VALUE.value, quarterly_empty_series)
                    / quarterly_df.get(Financial.EBITDA.value, quarterly_empty_series).rolling(4, min_periods=1).sum(),
                ],
                axis=0,
            )
            df["ev_ebit_ratio"] = pd.concat(
                [
                    yearly_df.get(Financial.ENTERPRISE_VALUE.value, yearly_empty_series)
                    / yearly_df.get(Financial.EBIT.value, yearly_empty_series),
                    quarterly_df.get(Financial.ENTERPRISE_VALUE.value, quarterly_empty_series)
                    / quarterly_df.get(Financial.EBIT.value, quarterly_empty_series).rolling(4, min_periods=1).sum(),
                ],
                axis=0,
            )

            df["ebitda_margin"] = (
                df.get(Financial.EBITDA.value, empty_series) / df.get(Financial.REVENUE.value, empty_series) * 100
            )
            df["ebit_margin"] = (
                df.get(Financial.EBIT.value, empty_series) / df.get(Financial.REVENUE.value, empty_series) * 100
            )
            df["net_income_margin"] = (
                df.get(Financial.NET_INCOME_REPORTED.value, empty_series)
                / df.get(Financial.REVENUE.value, empty_series)
                * 100
            )
            # df["price_to_cash_flow_ratio"] = df.get(MarketData.CLOSE.value, empty_series) / df.get(Financial.CASH_FLOW_PER_SHARE.value, empty_series)
            df["price_to_cash_flow_ratio"] = pd.concat(
                [
                    yearly_df.get(MarketData.CLOSE.value, yearly_empty_series)
                    / yearly_df.get(Financial.CASH_FLOW_PER_SHARE.value, yearly_empty_series),
                    quarterly_df.get(MarketData.CLOSE.value, quarterly_empty_series)
                    / quarterly_df.get(Financial.CASH_FLOW_PER_SHARE.value, quarterly_empty_series)
                    .rolling(4, min_periods=1)
                    .sum(),
                ],
                axis=0,
            )

            df["price_to_book_ratio"] = df.get(MarketData.CLOSE.value, empty_series) / df.get(
                Financial.BOOK_VALUE_PER_SHARE.value, empty_series
            )
            df["roce"] = pd.concat(
                [
                    yearly_df.get(Financial.EBIT.value, yearly_empty_series)
                    / (
                        yearly_df.get(Financial.TOTAL_ASSETS.value, yearly_empty_series)
                        - yearly_df.get(Financial.CURRENT_LIABILITIES.value, yearly_empty_series)
                    )
                    * 100,
                    quarterly_df.get(Financial.EBIT.value, quarterly_empty_series).rolling(4, min_periods=1).sum()
                    / (
                        quarterly_df.get(Financial.TOTAL_ASSETS.value, quarterly_empty_series)
                        - quarterly_df.get(Financial.CURRENT_LIABILITIES.value, quarterly_empty_series)
                    )
                    * 100,
                ],
                axis=0,
            )

            df["price_to_tangible_bv_ratio"] = df.get(MarketData.CLOSE.value, empty_series) / df.get(
                Financial.TANGIBLE_BOOK_VALUE_PER_SHARE.value, empty_series
            )
            df["cash_shares_ratio"] = df.get(Financial.CASH_AND_SHORT_TERM_INVESTMENT.value, empty_series) / df.get(
                Financial.DILUTED_WEIGHTED_AVG_SHARES.value, empty_series
            )
            df["total_debt_shares_ratio"] = df.get(Financial.TOTAL_DEBT.value, empty_series) / df.get(
                Financial.DILUTED_WEIGHTED_AVG_SHARES.value, empty_series
            )
            df["net_debt_shares_ratio"] = df.get(Financial.NET_DEBT.value, empty_series) / df.get(
                Financial.DILUTED_WEIGHTED_AVG_SHARES.value, empty_series
            )
            df["stock_compensation_employee_ratio"] = df.get(
                Financial.STOCK_COMPENSATION.value, empty_series
            ) / df.get(Financial.EMPLOYEES.value, empty_series)

            df["net_cash"] = df.get(Financial.CASH_EQUIVALENTS.value, empty_series) - df.get(
                Financial.CURRENT_LIABILITIES.value, empty_series
            )
            df[Financial.EBIT.value] = df.get(Financial.EBIT.value, empty_series)

        return FinancialAnalysisResult(
            df,
            ordering=[
                Financial.REVENUE.value,
                "price_sales_ratio",
                Financial.GROSS_PROFIT.value,
                Financial.GROSS_PROFIT_MARGIN.value,
                Financial.NET_INCOME_REPORTED.value,
                "net_income_margin",
                Financial.EPS_REPORTED.value,
                "price_earning_reported_ratio",
                Financial.EPS.value,
                "price_earning_ratio",
                Financial.EBITDA.value,
                "ebitda_margin",
                "ev_ebitda_ratio",
                Financial.EBIT.value,
                "ebit_margin",
                "ev_ebit_ratio",
                Financial.TOTAL_ASSETS.value,
                Financial.CURRENT_LIABILITIES.value,
                "roce",
                Financial.CASH_FLOW_PER_SHARE.value,
                "price_to_cash_flow_ratio",
                Financial.BOOK_VALUE_PER_SHARE.value,
                "price_to_book_ratio",
                Financial.TANGIBLE_BOOK_VALUE_PER_SHARE.value,
                "price_to_tangible_bv_ratio",
                Financial.CASH_AND_SHORT_TERM_INVESTMENT.value,
                Financial.DILUTED_WEIGHTED_AVG_SHARES.value,
                "cash_shares_ratio",
                Financial.TOTAL_DEBT.value,
                "total_debt_shares_ratio",
                Financial.NET_DEBT.value,
                "net_debt_shares_ratio",
                Financial.STOCK_COMPENSATION.value,
                Financial.EMPLOYEES.value,
                "stock_compensation_employee_ratio",
                Financial.CAPEX.value,
                Financial.SHARES_OUTSTANDING.value,
                MarketData.CLOSE.value,
                MarketData.MARKET_CAPITALIZATION.value,
                "net_cash",
            ],
            ignore_group_keys=[
                Financial.TANGIBLE_BOOK_VALUE_PER_SHARE.value,
                Financial.NET_DEBT.value,
                Financial.EMPLOYEES.value,
                Financial.CASH_AND_SHORT_TERM_INVESTMENT.value,
                Financial.DILUTED_WEIGHTED_AVG_SHARES.value,
                Financial.STOCK_COMPENSATION.value,
                Financial.TOTAL_DEBT.value,
            ],
            override_number_with_currency=self.instrument.currency.symbol or self.instrument.currency.key,
            override_number_with_currency_financials=[
                Financial.REVENUE.value,
                Financial.GROSS_PROFIT.value,
                Financial.NET_INCOME_REPORTED.value,
                Financial.EPS.value,
                Financial.EPS_REPORTED.value,
                Financial.EBITDA.value,
                Financial.EBIT.value,
                Financial.TOTAL_ASSETS.value,
                Financial.CURRENT_LIABILITIES.value,
                Financial.TOTAL_DEBT.value,
                Financial.NET_DEBT.value,
                Financial.STOCK_COMPENSATION.value,
                Financial.CAPEX.value,
                MarketData.CLOSE.value,
                MarketData.MARKET_CAPITALIZATION.value,
                Financial.CASH_FLOW_PER_SHARE.value,
                Financial.BOOK_VALUE_PER_SHARE.value,
                Financial.TANGIBLE_BOOK_VALUE_PER_SHARE.value,
                "cash_shares_ratio",
                "total_debt_shares_ratio",
                "net_debt_shares_ratio",
                "stock_compensation_employee_ratio",
                Financial.CASH_AND_SHORT_TERM_INVESTMENT.value,
            ],
            override_number_to_x_financials=[
                "price_sales_ratio",
                "price_earning_reported_ratio",
                "price_earning_ratio",
                "ev_ebitda_ratio",
                "ev_ebit_ratio",
                "price_to_book_ratio",
                "price_to_tangible_bv_ratio",
                "price_to_cash_flow_ratio",
            ],
            override_number_to_percent_financials=[
                Financial.GROSS_PROFIT_MARGIN.value,
                "net_income_margin",
                "ebitda_margin",
                "ebit_margin",
                "roce",
            ],
            errors=loader.errors,
        )

    @property
    def income_statement_with_estimate(self) -> FinancialAnalysisResult:
        values = [
            Financial.REVENUE,
            Financial.COST_OF_GOODS_SOLD,
            Financial.GROSS_PROFIT,
            Financial.GROSS_PROFIT_MARGIN,
            Financial.SELLING_MARKETING_EXPENSES,
            Financial.SGA_EXPENSES,
            Financial.GENERAL_ADMIN_EXPENSES,
            Financial.RND_EXPENSES,
            Financial.STOCK_COMPENSATION,
            Financial.TOTAL_OPERATING_EXPENSES,
            Financial.EBITDA,
            Financial.EBITDA_PER_SHARE,
            Financial.DEPRECATION,
            Financial.AMORTIZATION,
            Financial.EBIT,
            Financial.INTEREST_EXPENSE,
            Financial.NET_INCOME_BEFORE_TAXES,
            Financial.TAX_PROVISION,
            Financial.TAX_RATE,
            Financial.NET_INCOME,
            Financial.SHARES_OUTSTANDING,
            Financial.EPS,
            Financial.EBITDA_REPORTED,
            Financial.NET_INCOME_BEFORE_TAXES_REPORTED,
            Financial.NET_INCOME_REPORTED,
            Financial.EPS_REPORTED,
            Financial.DIVIDEND_PER_SHARE,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def balance_sheet_with_estimate(self) -> FinancialAnalysisResult:
        values = [
            Financial.CASH_EQUIVALENTS,
            Financial.INVENTORY,
            Financial.CURRENT_ASSETS,
            Financial.TOTAL_ASSETS,
            Financial.CURRENT_LIABILITIES,
            Financial.CURRENT_DEFERRED_REVENUE,
            Financial.TOTAL_DEBT,
            Financial.NET_DEBT,
            Financial.SHAREHOLDERS_EQUITY,
            Financial.GOODWILL,
            Financial.NET_ASSET_VALUE,
            Financial.BOOK_VALUE_PER_SHARE,
            Financial.TANGIBLE_BOOK_VALUE_PER_SHARE,
            Financial.ENTERPRISE_VALUE,
            Financial.TANGIBLE_BOOK_VALUE,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def cash_flow_statement_with_estimate(self) -> FinancialAnalysisResult:
        values = [
            Financial.WORKING_CAPITAL,
            Financial.INCOME_TAXES_PAID,
            Financial.CASH_FLOW_FROM_OPERATIONS,
            Financial.CAPEX,
            Financial.CASH_FLOW_FROM_INVESTING,
            Financial.FREE_CASH_FLOW,
            Financial.FREE_CASH_FLOW_PER_SHARE,
            Financial.TOTAL_DIVIDENDS,
            Financial.CASH_FLOW_FROM_FINANCING,
            Financial.CASH_FLOW_PER_SHARE,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)

    @property
    def ratios_with_estimate(self) -> FinancialAnalysisResult:
        values = [
            Financial.RETURN_ON_EQUITY,
            Financial.RETURN_ON_INVESTED_CAPITAL,
            Financial.RETURN_ON_CAPITAL,
            Financial.RETURN_ON_ASSETS,
        ]
        loader = Loader(self.instrument, values, self.calendar_type)
        df = loader.load()

        return FinancialAnalysisResult(df, ignore_group_keys=values, errors=loader.errors)
