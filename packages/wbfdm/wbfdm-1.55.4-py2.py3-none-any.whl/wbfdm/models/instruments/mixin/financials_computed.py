from datetime import date

import pandas as pd


#
#
# class FundamentalComputedMixin:
#     def _compute_revenue_growth(self) -> float:
#         if (
#             self.revenue is not None
#             and (last_fundamental := self.last_fundamental)
#             and (last_revenue := last_fundamental.revenue)
#         ):
#             return self.revenue / last_revenue - 1
#
#     def _compute_gross_profit(self) -> float:
#         if self.revenue is not None and self.cost_of_good_sold is not None:
#             return self.revenue - self.cost_of_good_sold
#
#     def _compute_gross_profit_margin(self) -> float:
#         if (
#             self.gross_profit is not None
#             and self.revenue
#             and self.deprecation_and_amortization_to_sales_ratio is not None
#         ):
#             return (self.gross_profit / self.revenue) + self.deprecation_and_amortization_to_sales_ratio
#
#     def _compute_ebitda_margin(self) -> float:
#         if self.ebitda is not None and self.revenue:
#             return self.ebitda / self.revenue
#
#     def _compute_ebit_margin(self) -> float:
#         if self.ebit is not None and self.revenue:
#             return self.ebit / self.revenue
#
#     def _compute_net_profit_margin(self) -> float:
#         if self.net_profit is not None and self.revenue:
#             return self.net_profit / self.revenue
#
#     def _compute_cost_of_good_sold(self) -> float:
#         if self.cost_of_good_sold_without_depreciation is not None and self.deprecation_and_amortization is not None:
#             return self.cost_of_good_sold_without_depreciation + self.deprecation_and_amortization
#
#     def _compute_eps_growth(self) -> float:
#         if self.eps is not None and (last_fundamental := self.last_fundamental) and (last_eps := last_fundamental.eps):
#             return self.eps / last_eps - 1
#
#     def _compute_sga_to_sales_ratio(self) -> float:
#         if self.sga is not None and self.revenue:
#             return self.sga / self.revenue
#
#     def _compute_interest_expense_to_sales_ratio(self) -> float:
#         if self.interest_expense is not None and self.revenue:
#             return self.interest_expense / self.revenue
#
#     def _compute_deprecation_and_amortization_to_sales_ratio(self) -> float:
#         if self.deprecation_and_amortization is not None and self.revenue:
#             return self.deprecation_and_amortization / self.revenue
#
#     def _compute_free_cash(self) -> float:
#         if self.cash_from_operation is not None and self.capital_expenditures is not None:
#             return self.cash_from_operation - self.capital_expenditures
#
#     def _compute_free_cash_flow(self):
#         if (
#             self.free_cash is not None
#             and (price := self.last_price)
#             and (outstanding_shares_consolidated := price.outstanding_shares_consolidated)
#         ):
#             return self.free_cash / float(outstanding_shares_consolidated)
#
#     def _compute_free_cash_flow_growth(self) -> float:
#         if (
#             self.free_cash_flow is not None
#             and (last_fundamental := self.last_fundamental)
#             and (last_free_cash_flow := last_fundamental.free_cash_flow)
#         ):
#             return self.free_cash_flow / last_free_cash_flow - 1
#
#     def _compute_free_cash_flow_to_sales_ratio(self) -> float:
#         if self.free_cash_flow is not None and self.revenue:
#             return self.free_cash_flow / self.revenue
#
#     def _compute_book_value_per_share(self) -> float:
#         if self.total_assets is not None and self.total_debt is not None:
#             if (
#                 yearly_valuations := self.instrument.valuations.exclude(outstanding_shares_consolidated=0).filter(
#                     date__year=self.year,
#                     date__lte=self.date_range.upper,
#                     outstanding_shares__isnull=False,
#                 )
#             ).exists() and (
#                 last_outstanding_shares := yearly_valuations.latest("date").outstanding_shares_consolidated
#             ):
#                 return (self.total_assets - self.total_debt) / float(last_outstanding_shares)
#
#     def _compute_net_change_in_cash(self) -> float:
#         if (
#             self.cash_from_operation is not None
#             and self.investment_cash is not None
#             and self.financing_cash is not None
#         ):
#             return self.cash_from_operation - self.investment_cash + self.financing_cash
#
#     def _compute_employee_count_growth(self) -> float:
#         if self.employee_count is not None and (previous := self.last_fundamental) and previous.employee_count:
#             return self.employee_count / previous.employee_count - 1
#
#     def _compute_capex_to_sales(self) -> float:
#         if self.capital_expenditures is not None and self.revenue:
#             return self.capital_expenditures / self.revenue
#
#     def _compute_net_debt_to_ebitda_ratio(self) -> float:
#         if self.net_debt is not None and self.ebitda:
#             return self.net_debt / self.ebitda
#
#     def _compute_burn_rate(self) -> float:
#         if self.net_change_in_cash is not None:
#             return min(self.net_change_in_cash / 12, 0)
#
#     def _compute_operating_burn_rate(self) -> float:
#         if self.cash_from_operation is not None:
#             return min(self.cash_from_operation / 12, 0)
#
#     def _compute_free_cash_burn_rate(self) -> float:
#         if self.free_cash is not None:
#             return min(self.free_cash / 12, 0)
#
#     def _compute_cash_reserve_to_burn_rate_ratio(self) -> float:
#         if self.cash_and_short_term_investments is not None and self.burn_rate:
#             return abs(self.cash_and_short_term_investments / self.burn_rate / 12)
#
#     def _compute_cash_reserve_to_operating_burn_rate_ratio(self) -> float:
#         if self.cash_and_short_term_investments is not None and self.operating_burn_rate:
#             return abs(self.cash_and_short_term_investments / self.operating_burn_rate / 12)
#
#     def _compute_cash_reserve_to_free_cash_burn_rate_ratio(self) -> float:
#         if self.cash_and_short_term_investments is not None and self.free_cash_burn_rate:
#             return abs(self.cash_and_short_term_investments / self.free_cash_burn_rate / 12)
#
#     def _compute_working_capital_to_burn_rate_ratio(self) -> float:
#         if self.working_capital is not None and self.burn_rate:
#             if self.working_capital <= 0:
#                 return None
#             return abs(self.working_capital / self.burn_rate / 12)
#
#     def _compute_working_capital_to_operating_burn_rate_ratio(self) -> float:
#         if self.working_capital is not None and self.operating_burn_rate:
#             if self.working_capital <= 0:
#                 return None
#             return abs(self.working_capital / self.operating_burn_rate / 12)
#
#     def _compute_working_capital_to_free_cash_burn_rate_ratio(self) -> float:
#         if self.working_capital is not None and self.free_cash_burn_rate:
#             if self.working_capital <= 0:
#                 return None
#             return abs(self.working_capital / self.free_cash_burn_rate / 12)
#
#     def _compute_current_ratio(self) -> float:
#         if self.current_assets is not None and self.current_liabilities:
#             return self.current_assets / self.current_liabilities
#
#     def _compute_cash_and_short_term_investments_to_current_assets_ratio(self) -> float:
#         if self.cash_and_short_term_investments is not None and self.current_assets:
#             return self.cash_and_short_term_investments / self.current_assets
#
#     def _compute_rd_to_sales_ratio(self) -> float:
#         if self.cost_research_development is not None and self.revenue:
#             return self.cost_research_development / self.revenue
#
#     def _compute_interest_coverage_ratio(self) -> float:
#         if self.ebit is not None and self.interest_expense:
#             return self.ebit / self.interest_expense
#
#     def _compute_return_on_equity(self) -> float:
#         if (
#             (previous := self.last_fundamental)
#             and self.net_profit is not None
#             and self.shareholder_equity is not None
#             and (previous_shareholder := previous.shareholder_equity) is not None
#         ):
#             avg_shareholder = (self.shareholder_equity + previous_shareholder) / 2
#             if avg_shareholder:
#                 return self.net_profit / avg_shareholder
#
#     def _compute_return_on_assets(self) -> float:
#         if (
#             (previous := self.last_fundamental)
#             and self.net_profit is not None
#             and self.total_assets is not None
#             and (previous_total_assets := previous.total_assets) is not None
#         ):
#             avg_total_assets = (self.total_assets + previous_total_assets) / 2
#             if avg_total_assets:
#                 return self.net_profit / avg_total_assets
#
#     def _compute_return_on_capital_employed(self) -> float:
#         if (
#             self.ebit is not None
#             and self.total_assets
#             and self.current_liabilities
#             and (diff := self.total_assets - self.current_liabilities)
#         ):
#             return self.ebit / diff
#
#     def _compute_return_on_invested_capital(self) -> float:
#         if (
#             self.ebit is not None
#             and self.company_tax_rate is not None
#             and self.shareholder_equity is not None
#             and self.total_liabilities is not None
#             and self.cash_and_cash_equivalents is not None
#             and (previous := self.last_fundamental)
#         ):
#             if (
#                 previous.shareholder_equity is not None
#                 and previous.total_liabilities is not None
#                 and previous.cash_and_cash_equivalents is not None
#             ):
#                 divisor = (
#                     self.shareholder_equity
#                     + self.total_liabilities
#                     - self.cash_and_cash_equivalents
#                     + previous.shareholder_equity
#                     + previous.total_liabilities
#                     - previous.cash_and_cash_equivalents
#                 ) / 2
#                 if divisor:
#                     return self.ebit * (1 - self.company_tax_rate) / divisor
#
#     def _compute_revenue_to_employee_ratio(self) -> float:
#         if self.revenue is not None and self.employee_count:
#             return self.revenue / self.employee_count
#
#
# class GeographicSegmentComputedMixin:
#     def _compute_value_growth(self) -> float:
#         if self.value is not None and (previous_segment := self.last_geographic_segment) and previous_segment.value:
#             return self.value / previous_segment.value - 1
#
#
# class ForecastComputedMixin:
#     def _compute_revenue_growth_y1(self) -> float:
#         if (fundamental := self.yearly_fundamental) and self.revenue_y1 is not None and fundamental.revenue:
#             return self.revenue_y1 / fundamental.revenue - 1
#
#     def _compute_revenue_growth_y2(self) -> float:
#         if self.revenue_y2 is not None and self.revenue_y1:
#             return self.revenue_y2 / self.revenue_y1 - 1
#
#     def _compute_revenue_growth_y3(self) -> float:
#         if self.revenue_y3 is not None and self.revenue_y2:
#             return self.revenue_y3 / self.revenue_y2 - 1
#
#     def _compute_revenue_growth_y4(self) -> float:
#         if self.revenue_y4 is not None and self.revenue_y3:
#             return self.revenue_y4 / self.revenue_y3 - 1
#
#     def _compute_revenue_growth_y5(self) -> float:
#         if self.revenue_y5 is not None and self.revenue_y4:
#             return self.revenue_y5 / self.revenue_y4 - 1
#
#     def _compute_deprecation_and_amortization_y1(self):
#         if self.ebitda_margin_y1 is not None and self.ebit_margin_y1 is not None:
#             return self.ebitda_margin_y1 - self.ebit_margin_y1
#
#     def _compute_deprecation_and_amortization_y2(self):
#         if self.ebitda_margin_y2 is not None and self.ebit_margin_y2 is not None:
#             return self.ebitda_margin_y2 - self.ebit_margin_y2
#
#     def _compute_deprecation_and_amortization_y3(self):
#         if self.ebitda_margin_y3 is not None and self.ebit_margin_y3 is not None:
#             return self.ebitda_margin_y3 - self.ebit_margin_y3
#
#     def _compute_deprecation_and_amortization_y4(self):
#         if self.ebitda_margin_y4 is not None and self.ebit_margin_y4 is not None:
#             return self.ebitda_margin_y4 - self.ebit_margin_y4
#
#     def _compute_deprecation_and_amortization_y5(self):
#         if self.ebitda_margin_y5 is not None and self.ebit_margin_y5 is not None:
#             return self.ebitda_margin_y5 - self.ebit_margin_y5
#
#     def _compute_gross_profit_margin_y1(self):
#         if (
#             self.gross_profit_margin_without_depreciation_y1 is not None
#             and self.deprecation_and_amortization_y1 is not None
#         ):
#             return self.gross_profit_margin_without_depreciation_y1 + self.deprecation_and_amortization_y1
#
#     def _compute_gross_profit_margin_y2(self):
#         if (
#             self.gross_profit_margin_without_depreciation_y2 is not None
#             and self.deprecation_and_amortization_y2 is not None
#         ):
#             return self.gross_profit_margin_without_depreciation_y2 + self.deprecation_and_amortization_y2
#
#     def _compute_gross_profit_margin_y3(self):
#         if (
#             self.gross_profit_margin_without_depreciation_y3 is not None
#             and self.deprecation_and_amortization_y3 is not None
#         ):
#             return self.gross_profit_margin_without_depreciation_y3 + self.deprecation_and_amortization_y3
#
#     def _compute_gross_profit_margin_y4(self):
#         if (
#             self.gross_profit_margin_without_depreciation_y4 is not None
#             and self.deprecation_and_amortization_y4 is not None
#         ):
#             return self.gross_profit_margin_without_depreciation_y4 + self.deprecation_and_amortization_y4
#
#     def _compute_gross_profit_margin_y5(self):
#         if (
#             self.gross_profit_margin_without_depreciation_y5 is not None
#             and self.deprecation_and_amortization_y5 is not None
#         ):
#             return self.gross_profit_margin_without_depreciation_y5 + self.deprecation_and_amortization_y5
#
#     def _compute_gross_profit_y1(self):
#         if self.gross_profit_margin_y1 is not None and self.revenue_y1 is not None:
#             return self.gross_profit_margin_y1 * self.revenue_y1
#
#     def _compute_gross_profit_y2(self):
#         if self.gross_profit_margin_y2 is not None and self.revenue_y2 is not None:
#             return self.gross_profit_margin_y2 * self.revenue_y2
#
#     def _compute_gross_profit_y3(self):
#         if self.gross_profit_margin_y3 is not None and self.revenue_y3 is not None:
#             return self.gross_profit_margin_y3 * self.revenue_y3
#
#     def _compute_gross_profit_y4(self):
#         if self.gross_profit_margin_y4 is not None and self.revenue_y4 is not None:
#             return self.gross_profit_margin_y4 * self.revenue_y4
#
#     def _compute_gross_profit_y5(self):
#         if self.gross_profit_margin_y5 is not None and self.revenue_y5 is not None:
#             return self.gross_profit_margin_y5 * self.revenue_y5
#
#     def _compute_net_profit_margin_y1(self) -> float:
#         if self.reported_net_profit_y1 is not None and self.revenue_y1:
#             return self.reported_net_profit_y1 / self.revenue_y1
#
#     def _compute_net_profit_margin_y2(self) -> float:
#         if self.reported_net_profit_y2 is not None and self.revenue_y2:
#             return self.reported_net_profit_y2 / self.revenue_y2
#
#     def _compute_net_profit_margin_y3(self) -> float:
#         if self.reported_net_profit_y3 is not None and self.revenue_y3:
#             return self.reported_net_profit_y3 / self.revenue_y3
#
#     def _compute_net_profit_margin_y4(self) -> float:
#         if self.reported_net_profit_y4 is not None and self.revenue_y4:
#             return self.reported_net_profit_y4 / self.revenue_y4
#
#     def _compute_net_profit_margin_y5(self) -> float:
#         if self.reported_net_profit_y5 is not None and self.revenue_y5:
#             return self.reported_net_profit_y5 / self.revenue_y5
#
#     def _compute_ebitda_margin_y1(self) -> float:
#         if self.ebitda_y1 is not None and self.revenue_y1:
#             return self.ebitda_y1 / self.revenue_y1
#
#     def _compute_ebitda_margin_y2(self) -> float:
#         if self.ebitda_y2 is not None and self.revenue_y2:
#             return self.ebitda_y2 / self.revenue_y2
#
#     def _compute_ebitda_margin_y3(self) -> float:
#         if self.ebitda_y3 is not None and self.revenue_y3:
#             return self.ebitda_y3 / self.revenue_y3
#
#     def _compute_ebitda_margin_y4(self) -> float:
#         if self.ebitda_y4 is not None and self.revenue_y4:
#             return self.ebitda_y4 / self.revenue_y4
#
#     def _compute_ebitda_margin_y5(self) -> float:
#         if self.ebitda_y5 is not None and self.revenue_y5:
#             return self.ebitda_y5 / self.revenue_y5
#
#     def _compute_ebit_margin_y1(self) -> float:
#         if self.ebit_y1 is not None and self.revenue_y1:
#             return self.ebit_y1 / self.revenue_y1
#
#     def _compute_ebit_margin_y2(self) -> float:
#         if self.ebit_y2 is not None and self.revenue_y2:
#             return self.ebit_y2 / self.revenue_y2
#
#     def _compute_ebit_margin_y3(self) -> float:
#         if self.ebit_y3 is not None and self.revenue_y3:
#             return self.ebit_y3 / self.revenue_y3
#
#     def _compute_ebit_margin_y4(self) -> float:
#         if self.ebit_y4 is not None and self.revenue_y4:
#             return self.ebit_y4 / self.revenue_y4
#
#     def _compute_ebit_margin_y5(self) -> float:
#         if self.ebit_y5 is not None and self.revenue_y5:
#             return self.ebit_y5 / self.revenue_y5
#
#     def _compute_eps_y1(self):
#         if self.reported_net_profit_y1 is not None and self.shares:
#             return self.reported_net_profit_y1 / self.shares
#
#     def _compute_eps_y2(self):
#         if self.reported_net_profit_y2 is not None and self.shares:
#             return self.reported_net_profit_y2 / self.shares
#
#     def _compute_eps_y3(self):
#         if self.reported_net_profit_y3 is not None and self.shares:
#             return self.reported_net_profit_y3 / self.shares
#
#     def _compute_eps_y4(self):
#         if self.reported_net_profit_y4 is not None and self.shares:
#             return self.reported_net_profit_y4 / self.shares
#
#     def _compute_eps_y5(self):
#         if self.reported_net_profit_y5 is not None and self.shares:
#             return self.reported_net_profit_y5 / self.shares
#
#     def _compute_eps_growth_y1(self) -> float:
#         if (fundamental := self.yearly_fundamental) and self.eps_y1 is not None and fundamental.eps:
#             return self.eps_y1 / fundamental.eps - 1
#
#     def _compute_eps_growth_y2(self) -> float:
#         if self.eps_y2 is not None and self.eps_y1:
#             return self.eps_y2 / self.eps_y1 - 1
#
#     def _compute_eps_growth_y3(self) -> float:
#         if self.eps_y3 is not None and self.eps_y2:
#             return self.eps_y3 / self.eps_y2 - 1
#
#     def _compute_eps_growth_y4(self) -> float:
#         if self.eps_y4 is not None and self.eps_y3:
#             return self.eps_y4 / self.eps_y3 - 1
#
#     def _compute_eps_growth_y5(self) -> float:
#         if self.eps_y5 is not None and self.eps_y4:
#             return self.eps_y5 / self.eps_y4 - 1
#
#     def _compute_net_debt_to_ebitda_ratio_y1(self) -> float:
#         if self.net_debt_y1 is not None and self.ebitda_y1:
#             return self.net_debt_y1 / self.ebitda_y1
#
#     def _compute_net_debt_to_ebitda_ratio_y2(self) -> float:
#         if self.net_debt_y2 is not None and self.ebitda_y2:
#             return self.net_debt_y2 / self.ebitda_y2
#
#     def _compute_net_debt_to_ebitda_ratio_y3(self) -> float:
#         if self.net_debt_y3 is not None and self.ebitda_y3:
#             return self.net_debt_y3 / self.ebitda_y3
#
#     def _compute_net_debt_to_ebitda_ratio_y4(self) -> float:
#         if self.net_debt_y4 is not None and self.ebitda_y4:
#             return self.net_debt_y4 / self.ebitda_y4
#
#     def _compute_net_debt_to_ebitda_ratio_y5(self) -> float:
#         if self.net_debt_y5 is not None and self.ebitda_y5:
#             return self.net_debt_y5 / self.ebitda_y5
#
#     def _compute_free_cash_flow_growth_y1(self) -> float:
#         if (
#             (daily_fundamental := self.daily_fundamental)
#             and self.free_cash_flow_y1 is not None
#             and daily_fundamental.free_cash_flow
#         ):
#             return self.free_cash_flow_y1 / daily_fundamental.free_cash_flow - 1
#
#     def _compute_free_cash_flow_growth_y2(self) -> float:
#         if self.free_cash_flow_y2 is not None and self.free_cash_flow_y1:
#             return self.free_cash_flow_y2 / self.free_cash_flow_y1 - 1
#
#     def _compute_free_cash_flow_growth_y3(self) -> float:
#         if self.free_cash_flow_y3 is not None and self.free_cash_flow_y2:
#             return self.free_cash_flow_y3 / self.free_cash_flow_y2 - 1
#
#     def _compute_free_cash_flow_growth_y4(self) -> float:
#         if self.free_cash_flow_y4 is not None and self.free_cash_flow_y3:
#             return self.free_cash_flow_y4 / self.free_cash_flow_y3 - 1
#
#     def _compute_free_cash_flow_growth_y5(self) -> float:
#         if self.free_cash_flow_y5 is not None and self.free_cash_flow_y4:
#             return self.free_cash_flow_y5 / self.free_cash_flow_y4 - 1
#
#     def _compute_free_cash_flow_to_sales_ratio_y1(self) -> float:
#         if self.free_cash_flow_y1 is not None and self.revenue_y1:
#             return self.free_cash_flow_y1 / self.revenue_y1
#
#     def _compute_free_cash_flow_to_sales_ratio_y2(self) -> float:
#         if self.free_cash_flow_y2 is not None and self.revenue_y2:
#             return self.free_cash_flow_y2 / self.revenue_y2
#
#     def _compute_free_cash_flow_to_sales_ratio_y3(self) -> float:
#         if self.free_cash_flow_y3 is not None and self.revenue_y3:
#             return self.free_cash_flow_y3 / self.revenue_y3
#
#     def _compute_free_cash_flow_to_sales_ratio_y4(self) -> float:
#         if self.free_cash_flow_y4 is not None and self.revenue_y4:
#             return self.free_cash_flow_y4 / self.revenue_y4
#
#     def _compute_free_cash_flow_to_sales_ratio_y5(self) -> float:
#         if self.free_cash_flow_y5 is not None and self.revenue_y5:
#             return self.free_cash_flow_y5 / self.revenue_y5
#
#     def _compute_capex_to_sales_y1(self) -> float:
#         if self.capital_expenditures_y1 is not None and self.revenue_y1:
#             return self.capital_expenditures_y1 / self.revenue_y1
#
#     def _compute_capex_to_sales_y2(self) -> float:
#         if self.capital_expenditures_y2 is not None and self.revenue_y2:
#             return self.capital_expenditures_y2 / self.revenue_y2
#
#     def _compute_capex_to_sales_y3(self) -> float:
#         if self.capital_expenditures_y3 is not None and self.revenue_y3:
#             return self.capital_expenditures_y3 / self.revenue_y3
#
#     def _compute_capex_to_sales_y4(self) -> float:
#         if self.capital_expenditures_y4 is not None and self.revenue_y4:
#             return self.capital_expenditures_y4 / self.revenue_y4
#
#     def _compute_capex_to_sales_y5(self) -> float:
#         if self.capital_expenditures_y5 is not None and self.revenue_y5:
#             return self.capital_expenditures_y5 / self.revenue_y5
#
#     def __compute_return_on_equity(self, year: int) -> float:
#         if (
#             (net_profit := getattr(self, f"reported_net_profit_y{year}")) is not None
#             and (previous := self.yearly_fundamental)
#             and previous.net_profit is not None
#             and previous.shareholder_equity
#         ):
#             return net_profit / previous.shareholder_equity
#
#     def _compute_return_on_equity_y1(self):
#         return self.__compute_return_on_equity(1)
#
#     def _compute_return_on_equity_y2(self):
#         return self.__compute_return_on_equity(2)
#
#     def _compute_return_on_equity_y3(self):
#         return self.__compute_return_on_equity(3)
#
#     def _compute_return_on_equity_y4(self):
#         return self.__compute_return_on_equity(4)
#
#     def _compute_return_on_equity_y5(self):
#         return self.__compute_return_on_equity(5)
#
#     def __compute_return_on_assets(self, year: int) -> float:
#         if (
#             (net_profit := getattr(self, f"reported_net_profit_y{year}")) is not None
#             and (previous := self.yearly_fundamental)
#             and previous.net_profit is not None
#             and previous.total_assets
#         ):
#             return net_profit / previous.total_assets
#
#     def _compute_return_on_assets_y1(self):
#         return self.__compute_return_on_assets(1)
#
#     def _compute_return_on_assets_y2(self):
#         return self.__compute_return_on_assets(2)
#
#     def _compute_return_on_assets_y3(self):
#         return self.__compute_return_on_assets(3)
#
#     def _compute_return_on_assets_y4(self):
#         return self.__compute_return_on_assets(4)
#
#     def _compute_return_on_assets_y5(self):
#         return self.__compute_return_on_assets(5)
#
#     def __compute_return_on_capital_employed(self, year: int) -> float:
#         if (
#             (previous := self.yearly_fundamental)
#             and (ebit := getattr(self, f"ebit_y{year}")) is not None
#             and previous.total_assets
#             and previous.current_liabilities
#             and (diff := previous.total_assets - previous.current_liabilities)
#         ):
#             return ebit / diff
#
#     def _compute_return_on_capital_employed_y1(self):
#         return self.__compute_return_on_capital_employed(1)
#
#     def _compute_return_on_capital_employed_y2(self):
#         return self.__compute_return_on_capital_employed(2)
#
#     def _compute_return_on_capital_employed_y3(self):
#         return self.__compute_return_on_capital_employed(3)
#
#     def _compute_return_on_capital_employed_y4(self):
#         return self.__compute_return_on_capital_employed(4)
#
#     def _compute_return_on_capital_employed_y5(self):
#         return self.__compute_return_on_capital_employed(5)
#
#     def __compute_return_on_invested_capital(self, year: int) -> float:
#         if (
#             (previous := self.yearly_fundamental)
#             and (ebit := getattr(self, f"ebit_y{year}")) is not None
#             and previous.company_tax_rate is not None
#             and previous.shareholder_equity is not None
#             and previous.total_liabilities is not None
#             and previous.cash_and_cash_equivalents is not None
#         ):
#             divisor = previous.shareholder_equity + previous.total_liabilities - previous.cash_and_cash_equivalents
#             if divisor:
#                 return ebit * (1 - previous.company_tax_rate) / divisor
#
#     def _compute_return_on_invested_capital_y1(self):
#         return self.__compute_return_on_invested_capital(1)
#
#     def _compute_return_on_invested_capital_y2(self):
#         return self.__compute_return_on_invested_capital(2)
#
#     def _compute_return_on_invested_capital_y3(self):
#         return self.__compute_return_on_invested_capital(3)
#
#     def _compute_return_on_invested_capital_y4(self):
#         return self.__compute_return_on_invested_capital(4)
#
#     def _compute_return_on_invested_capital_y5(self):
#         return self.__compute_return_on_invested_capital(5)
#
#     def __compute_interest_coverage_ratio(self, year: int) -> float:
#         if (
#             (previous := self.yearly_fundamental)
#             and (ebit := getattr(self, f"ebit_y{year}")) is not None
#             and previous.interest_expense
#         ):
#             return ebit / previous.interest_expense
#
#     def _compute_interest_coverage_ratio_y1(self):
#         return self.__compute_interest_coverage_ratio(1)
#
#     def _compute_interest_coverage_ratio_y2(self):
#         return self.__compute_interest_coverage_ratio(2)
#
#     def _compute_interest_coverage_ratio_y3(self):
#         return self.__compute_interest_coverage_ratio(3)
#
#     def _compute_interest_coverage_ratio_y4(self):
#         return self.__compute_interest_coverage_ratio(4)
#
#     def _compute_interest_coverage_ratio_y5(self):
#         return self.__compute_interest_coverage_ratio(5)
#
#
# class DailyFundamentalComputedMixin:
#     def _compute_free_cash_flow_ttm_growth(self) -> float:
#         if (
#             self.free_cash_flow is not None
#             and (last_ttl_daily_fundamental := self.last_ttl_daily_fundamental)
#             and (last_free_cash_flow := last_ttl_daily_fundamental.free_cash_flow)
#         ):
#             return self.free_cash_flow / last_free_cash_flow - 1
#
#     def _compute_free_cash_flow(self) -> float:
#         if (
#             self.free_cash is not None
#             and (price := self.price)
#             and (outstanding_shares_consolidated := price.outstanding_shares_consolidated)
#         ):
#             return self.free_cash / float(outstanding_shares_consolidated)
#
#     def _compute_revenue_growth_3y_cagr(self) -> float:
#         if (
#             (forecast := self.forecast)
#             and (fundamental := self.yearly_fundamental)
#             and (revenue_y3 := forecast.revenue_y3) is not None
#             and fundamental.revenue
#         ):
#             if (den := revenue_y3 / fundamental.revenue) >= 0:
#                 return math.pow(den, 1 / 3) - 1
#
#     def _compute_eps_3y_cagr(self) -> float:
#         if (
#             (forecast := self.forecast)
#             and (fundamental := self.yearly_fundamental)
#             and (eps_3y := forecast.eps_y3) is not None
#             and fundamental.eps
#         ):
#             if (den := eps_3y / fundamental.eps) >= 0:
#                 return math.pow(den, 1 / 3) - 1
#
#     def _compute_free_cash_flow_3y_cagr(self) -> float:
#         if (
#             (forecast := self.forecast)
#             and (fundamental := self.yearly_fundamental)
#             and (fcf_3y := forecast.free_cash_flow_y3) is not None
#             and fundamental.free_cash_flow
#         ):
#             if (den := fcf_3y / fundamental.free_cash_flow) >= 0:
#                 return math.pow(den, 1 / 3) - 1
#
#     def _compute_eps_ttm(self):
#         pass
#
#
class InstrumentPriceComputedMixin:
    def _compute_outstanding_shares_consolidated(self):
        if self.outstanding_shares_consolidated is None and self.outstanding_shares is not None:
            return self.outstanding_shares

    def _compute_gross_value(self):
        if self.net_value is not None and self.gross_value is None:
            return self.net_value

    def _compute_volume_50d(self):
        volumes = list(
            filter(
                None,
                self.instrument.valuations.filter(date__lte=self.date)
                .order_by("-date")
                .values_list("volume", flat=True)[:50],
            )
        )
        if len(volumes) > 0:
            return sum(volumes) / len(volumes)
        return 0.0

    def _compute_volume_200d(self):
        volumes = list(
            filter(
                None,
                self.instrument.valuations.filter(date__lte=self.date)
                .order_by("-date")
                .values_list("volume", flat=True)[:200],
            )
        )
        if len(volumes) > 0:
            return sum(volumes) / len(volumes)
        return 0.0

    def _compute_performance_1d(self):
        try:
            last_price = self.instrument.prices.get(
                calculated=self.calculated, date=(self.date - pd.tseries.offsets.BDay(1)).date()
            )
            if self.net_value is not None and last_price.net_value:
                return self.net_value / last_price.net_value - 1
        except self.DoesNotExist:
            pass

    def _compute_performance_7d(self):
        try:
            last_price = self.instrument.prices.get(
                calculated=self.calculated, date=(self.date - pd.tseries.offsets.BDay(7)).date()
            )
            if self.net_value is not None and last_price.net_value:
                return self.net_value / last_price.net_value - 1
        except self.DoesNotExist:
            pass

    def _compute_performance_30d(self):
        try:
            last_price = self.instrument.prices.get(
                calculated=self.calculated, date=(self.date - pd.tseries.offsets.BDay(30)).date()
            )
            if self.net_value is not None and last_price.net_value:
                return self.net_value / last_price.net_value - 1
        except self.DoesNotExist:
            pass

    def _compute_performance_90d(self):
        try:
            last_price = self.instrument.prices.get(
                calculated=self.calculated, date=(self.date - pd.tseries.offsets.BDay(90)).date()
            )
            if self.net_value is not None and last_price.net_value:
                return self.net_value / last_price.net_value - 1
        except self.DoesNotExist:
            pass

    def _compute_performance_365d(self):
        try:
            last_price = self.instrument.prices.get(
                calculated=self.calculated, date=(self.date - pd.tseries.offsets.BDay(365)).date()
            )
            if self.net_value is not None and last_price.net_value:
                return self.net_value / last_price.net_value - 1
        except self.DoesNotExist:
            pass

    def _compute_performance_ytd(self):
        try:
            last_price = self.instrument.prices.get(
                calculated=self.calculated, date=(date(self.date.year, 1, 1) - pd.tseries.offsets.BDay(0)).date()
            )
            if self.net_value is not None and last_price.net_value:
                return self.net_value / last_price.net_value - 1
        except self.DoesNotExist:
            pass

    def _compute_performance_inception(self):
        try:
            last_price = self.instrument.prices.get(calculated=self.calculated, date=self.instrument.inception_date)
            if self.net_value is not None and last_price.net_value:
                return self.net_value / last_price.net_value - 1
        except self.DoesNotExist:
            pass
