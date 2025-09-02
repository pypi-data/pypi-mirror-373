from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest
from faker import Faker

from wbfdm.analysis.financial_analysis.statement_with_estimates import (
    StatementWithEstimates,
)
from wbfdm.analysis.financial_analysis.utils import Loader
from wbfdm.enums import Financial, MarketData

fake = Faker()


@pytest.mark.django_db
class TestStatementWithEstimates:
    # Coverage test to cover all the Statement with estimates properties
    @pytest.fixture()
    def df(self, values):
        data = []
        for financial in values:
            for interim in ["Y", "S1", "S2"]:
                data.append(
                    {
                        "year": 2021,
                        "estimate": False,
                        "interim": interim,
                        "period_end_date": date(2021, 12, 31),
                        "financial": financial.value,
                        "value": fake.pyfloat(),
                    }
                )
        df = pd.DataFrame(data).pivot_table(
            index=["year", "interim", "estimate", "period_end_date"], columns="financial", values="value"
        )
        return df.reset_index(level=[2, 3])

    @pytest.fixture()
    def summery_with_estimate_df(self):
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
            MarketData.CLOSE,
            MarketData.MARKET_CAPITALIZATION,
            Financial.EMPLOYEES,
            Financial.CASH_AND_SHORT_TERM_INVESTMENT,
            Financial.DILUTED_WEIGHTED_AVG_SHARES,
            Financial.TOTAL_DEBT,
            Financial.NET_DEBT,
            Financial.STOCK_COMPENSATION,
            Financial.TANGIBLE_BOOK_VALUE_PER_SHARE,
        ]

        data = []
        for financial in values:
            for interim in ["Y", "S1", "S2"]:
                data.append(
                    {
                        "year": 2021,
                        "estimate": False,
                        "interim": interim,
                        "period_end_date": date(2021, 12, 31),
                        "financial": financial.value,
                        "value": fake.pyfloat(),
                    }
                )
        df = pd.DataFrame(data).pivot_table(
            index=["year", "interim", "estimate", "period_end_date"], columns="financial", values="value"
        )
        return df.reset_index(level=[2, 3])

    @pytest.mark.parametrize(
        "values",
        [
            [
                Financial.NET_DEBT,
                Financial.EBITDA,
                Financial.TOTAL_DEBT,
                Financial.FREE_CASH_FLOW,
                Financial.CASH_FLOW_FROM_OPERATIONS,
            ]
        ],
    )
    @patch.object(Loader, "load")
    def test_credit_with_estimates(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).credit_with_estimates
        assert set(res.df.columns) == {
            "net_debt_ebitda_ratio",
            "total_debt_ebitda_ratio",
            "fcf_total_debt_ratio",
            "cfo_total_debt_ratio",
            "period_end_date",
            "estimate",
        }
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
                Financial.TOTAL_DEBT,
                Financial.SHAREHOLDERS_EQUITY,
                Financial.WORKING_CAPITAL,
            ]
        ],
    )
    @patch.object(Loader, "load")
    def test_long_term_solvency_with_estimates(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).long_term_solvency_with_estimates
        assert set(res.df.columns) == {
            "total_debt_equity_ratio",
            "total_debt_capital_ratio",
            "period_end_date",
            "estimate",
        }
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
                Financial.CURRENT_ASSETS,
                Financial.CURRENT_LIABILITIES,
                Financial.CASH_FLOW_FROM_OPERATIONS,
            ]
        ],
    )
    @patch.object(Loader, "load")
    def test_short_term_liquidity_with_estimates(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).short_term_liquidity_with_estimates
        assert set(res.df.columns) == {
            "current_ratio",
            "cash_from_operation_current_liabilities_ratio",
            "period_end_date",
            "estimate",
        }
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
                Financial.REVENUE,
                Financial.TOTAL_ASSETS,
                Financial.COST_OF_GOODS_SOLD,
            ]
        ],
    )
    @patch.object(Loader, "load")
    def test_asset_turnover_with_estimates(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).asset_turnover_with_estimates
        assert set(res.df.columns) == {"asset_turnover", "period_end_date", "estimate"}
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
                Financial.CASH_FLOW_FROM_OPERATIONS,
                Financial.CURRENT_LIABILITIES,
                Financial.REVENUE,
                Financial.TOTAL_ASSETS,
                Financial.TOTAL_DEBT,
            ]
        ],
    )
    @patch.object(Loader, "load")
    def test_cashflow_ratios_with_estimates(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).cashflow_ratios_with_estimates
        assert set(res.df.columns) == {
            "current_liability_coverage_ratio",
            "cash_flow_margin",
            "asset_efficiency_margin",
            "net_debt_coverage_ratio",
            "period_end_date",
            "estimate",
        }
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
                Financial.REVENUE,
                Financial.GROSS_PROFIT,
                Financial.SGA_EXPENSES,
                Financial.EBITDA,
                Financial.EBIT,
                Financial.NET_INCOME,
                Financial.FREE_CASH_FLOW,
            ]
        ],
    )
    @patch.object(Loader, "load")
    def test_margins_with_estimates(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).margins_with_estimates
        assert set(res.df.columns) == {
            "gross_margin",
            "sga_margin",
            "ebitda_margin",
            "ebit_margin",
            "net_income_margin",
            "free_cash_flow_margin",
            "period_end_date",
            "estimate",
        }
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
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
        ],
    )
    @patch.object(Loader, "load")
    def test_income_statement_with_estimate(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).income_statement_with_estimate
        assert set(res.df.columns) == {*[v.value for v in values], "period_end_date", "estimate"}
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
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
        ],
    )
    @patch.object(Loader, "load")
    def test_balance_sheet_with_estimate(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).balance_sheet_with_estimate
        assert set(res.df.columns) == {*[v.value for v in values], "period_end_date", "estimate"}
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
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
        ],
    )
    @patch.object(Loader, "load")
    def test_cash_flow_statement_with_estimate(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).cash_flow_statement_with_estimate
        assert set(res.df.columns) == {*[v.value for v in values], "period_end_date", "estimate"}
        assert not res.formatted_df.empty

    @pytest.mark.parametrize(
        "values",
        [
            [
                Financial.RETURN_ON_EQUITY,
                Financial.RETURN_ON_INVESTED_CAPITAL,
                Financial.RETURN_ON_CAPITAL,
                Financial.RETURN_ON_ASSETS,
            ]
        ],
    )
    @patch.object(Loader, "load")
    def test_ratios_with_estimate(self, mock_fct, instrument, df, values):
        mock_fct.return_value = df
        res = StatementWithEstimates(instrument).ratios_with_estimate
        assert set(res.df.columns) == {*[v.value for v in values], "period_end_date", "estimate"}
        assert not res.formatted_df.empty

    @patch.object(Loader, "load")
    def test_summary_with_estimate(self, mock_fct, summery_with_estimate_df, instrument):
        mock_fct.return_value = summery_with_estimate_df
        res = StatementWithEstimates(instrument).summary_with_estimate
        expected_values = {
            "revenue",
            "price_sales_ratio",
            "gross_profit",
            "gross_profit_margin",
            "net_income_reported",
            "net_income_margin",
            "eps_reported",
            "price_earning_reported_ratio",
            "eps",
            "price_earning_ratio",
            "ebitda",
            "ebitda_margin",
            "ev_ebitda_ratio",
            "ebit",
            "ebit_margin",
            "ev_ebit_ratio",
            "total_assets",
            "current_liabilities",
            "roce",
            "cash_flow_per_share",
            "price_to_cash_flow_ratio",
            "book_value_per_share",
            "price_to_book_ratio",
            "tangible_book_value_per_share",
            "price_to_tangible_bv_ratio",
            "cash_and_short_term_investment",
            "diluded_weighted_avg_shares",
            "cash_shares_ratio",
            "total_debt",
            "total_debt_shares_ratio",
            "net_debt",
            "net_debt_shares_ratio",
            "stock_compensation",
            "employees",
            "stock_compensation_employee_ratio",
            "capex",
            "shares_outstanding",
            "market_capitalization",
            "close",
            "market_capitalization",
            "net_cash",
            "period_end_date",
            "estimate",
        }
        assert set(res.df.columns) == expected_values
        assert not res.formatted_df.empty
