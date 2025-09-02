import wbcore.serializers as wb_serializer
from wbcore.serializers.fields.number import DisplayMode


def get_default_attrs(cls, field_name):
    field = cls._meta.get_field(field_name)
    return {"label": field.verbose_name, "help_text": field.help_text}


class FundamentalSerializerFieldMixin:
    @classmethod
    def get_number_serializer_fields(cls):
        return {
            "revenue": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "revenue"),
            ),
            "revenue_growth": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "revenue_growth")
            ),
            "cost_of_good_sold_without_depreciation": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "cost_of_good_sold_without_depreciation"),
            ),
            "cost_of_good_sold": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "cost_of_good_sold"),
            ),
            "gross_profit": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "gross_profit"),
            ),
            "gross_profit_margin": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "gross_profit_margin")
            ),
            "eps": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps"),
            ),
            "eps_growth": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "eps_growth")
            ),
            "diluted_eps": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "diluted_eps"),
            ),
            "ebitda": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebitda"),
            ),
            "ebitda_margin": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebitda_margin")
            ),
            "ebit": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebit"),
            ),
            "ebit_margin": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebit_margin")
            ),
            "net_profit": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "net_profit"),
            ),
            "net_profit_margin": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "net_profit_margin")
            ),
            "company_tax_rate": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "company_tax_rate")
            ),
            "cost_research_development": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "cost_research_development"),
            ),
            "interest_expense": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "interest_expense"),
            ),
            "interest_expense_to_sales_ratio": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "interest_expense_to_sales_ratio")
            ),
            "sga": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "sga"),
            ),
            "sga_to_sales_ratio": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "sga_to_sales_ratio")
            ),
            "deprecation_and_amortization": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "deprecation_and_amortization"),
            ),
            "deprecation_and_amortization_to_sales_ratio": wb_serializer.FloatField(
                percent=True,
                precision=3,
                read_only=True,
                **get_default_attrs(cls, "deprecation_and_amortization_to_sales_ratio"),
            ),
            "free_cash": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash"),
            ),
            "free_cash_flow": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash_flow"),
            ),
            "free_cash_flow_growth": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_growth")
            ),
            "free_cash_flow_to_sales_ratio": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_to_sales_ratio")
            ),
            "cash_from_operation": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "cash_from_operation"),
            ),
            "working_capital": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "working_capital"),
            ),
            "capital_expenditures": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "capital_expenditures"),
            ),
            "investment_cash": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "investment_cash"),
            ),
            "financing_cash": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "financing_cash"),
            ),
            "shareholder_equity": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "shareholder_equity"),
            ),
            "total_assets": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "total_assets"),
            ),
            "current_liabilities": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "current_liabilities"),
            ),
            "total_liabilities": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "total_liabilities"),
            ),
            "total_debt": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "total_debt"),
            ),
            "cash_and_cash_equivalents": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "cash_and_cash_equivalents"),
            ),
            "net_debt": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "net_debt"),
            ),
            "cash_and_short_term_investments": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "cash_and_short_term_investments"),
            ),
            "net_change_in_cash": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "net_change_in_cash"),
            ),
            "receivables": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "receivables"),
            ),
            "inventories": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "inventories"),
            ),
            "payables": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "payables"),
            ),
            "book_value_per_share": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "book_value_per_share"),
            ),
            "current_assets": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "current_assets"),
            ),
            "employee_count": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                read_only=True,
                **get_default_attrs(cls, "employee_count"),
            ),
            "employee_count_growth": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "employee_count_growth")
            ),
            "entreprise_value": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "entreprise_value"),
            ),
            "net_debt_to_ebitda_ratio": wb_serializer.FloatField(
                precision=2, read_only=True, **get_default_attrs(cls, "net_debt_to_ebitda_ratio")
            ),
            "burn_rate": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "burn_rate"),
            ),
            "operating_burn_rate": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "operating_burn_rate"),
            ),
            "free_cash_burn_rate": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash_burn_rate"),
            ),
            "cash_reserve_to_burn_rate_ratio": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "cash_reserve_to_burn_rate_ratio")
            ),
            "cash_reserve_to_operating_burn_rate_ratio": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "cash_reserve_to_operating_burn_rate_ratio")
            ),
            "cash_reserve_to_free_cash_burn_rate_ratio": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "cash_reserve_to_free_cash_burn_rate_ratio")
            ),
            "working_capital_to_burn_rate_ratio": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "working_capital_to_burn_rate_ratio")
            ),
            "working_capital_to_operating_burn_rate_ratio": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "working_capital_to_operating_burn_rate_ratio")
            ),
            "working_capital_to_free_cash_burn_rate_ratio": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "working_capital_to_free_cash_burn_rate_ratio")
            ),
            "current_ratio": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "current_ratio")
            ),
            "cash_and_short_term_investments_to_current_assets_ratio": wb_serializer.FloatField(
                precision=1,
                read_only=True,
                **get_default_attrs(cls, "cash_and_short_term_investments_to_current_assets_ratio"),
            ),
            "rd_to_sales_ratio": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "rd_to_sales_ratio")
            ),
            "interest_coverage_ratio": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "interest_coverage_ratio")
            ),
            "return_on_equity": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "return_on_equity")
            ),
            "return_on_assets": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "return_on_assets")
            ),
            "return_on_capital_employed": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "return_on_capital_employed")
            ),
            "return_on_invested_capital": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "return_on_invested_capital")
            ),
            "revenue_to_employee_ratio": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "revenue_to_employee_ratio"),
            ),
            "capex_to_sales": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "capex_to_sales")
            ),
        }


class GeographicSegmentSerializerFieldMixin:
    @classmethod
    def get_number_serializer_fields(cls):
        return {
            "value": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "value")),
            "value_growth": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "value_growth")),
        }


class DailyFundamentalSerializerFieldMixin:
    @classmethod
    def get_number_serializer_fields(cls):
        return {
            "eps_ttm": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps_ttm"),
            ),
            "eps_ftw": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps_ftw"),
            ),
            "free_cash": wb_serializer.FloatField(
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash"),
            ),
            "free_cash_flow": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash_flow"),
            ),
            "free_cash_flow_ttm_growth": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_ttm_growth")
            ),
            "revenue_growth_3y_cagr": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "revenue_growth_3y_cagr")
            ),
            "eps_3y_cagr": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "eps_3y_cagr")
            ),
            "free_cash_flow_3y_cagr": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_3y_cagr")
            ),
        }


class ForecastSerializerFieldMixin:
    @classmethod
    def get_number_serializer_fields(cls):
        return {
            "revenue_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "revenue_y1"),
            ),
            "revenue_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "revenue_y2"),
            ),
            "revenue_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "revenue_y3"),
            ),
            "revenue_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "revenue_y4"),
            ),
            "revenue_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "revenue_y5"),
            ),
            "revenue_growth_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "revenue_growth_y1")
            ),
            "revenue_growth_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "revenue_growth_y2")
            ),
            "revenue_growth_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "revenue_growth_y3")
            ),
            "revenue_growth_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "revenue_growth_y4")
            ),
            "revenue_growth_y5": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "revenue_growth_y5")
            ),
            "deprecation_and_amortization_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "deprecation_and_amortization_y1"),
            ),
            "deprecation_and_amortization_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "deprecation_and_amortization_y2"),
            ),
            "deprecation_and_amortization_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "deprecation_and_amortization_y3"),
            ),
            "deprecation_and_amortization_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "deprecation_and_amortization_y4"),
            ),
            "deprecation_and_amortization_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "deprecation_and_amortization_y5"),
            ),
            "gross_profit_margin_without_depreciation_y1": wb_serializer.FloatField(
                percent=True,
                precision=3,
                read_only=True,
                **get_default_attrs(cls, "gross_profit_margin_without_depreciation_y1"),
            ),
            "gross_profit_margin_without_depreciation_y2": wb_serializer.FloatField(
                percent=True,
                precision=3,
                read_only=True,
                **get_default_attrs(cls, "gross_profit_margin_without_depreciation_y2"),
            ),
            "gross_profit_margin_without_depreciation_y3": wb_serializer.FloatField(
                percent=True,
                precision=3,
                read_only=True,
                **get_default_attrs(cls, "gross_profit_margin_without_depreciation_y3"),
            ),
            "gross_profit_margin_without_depreciation_y4": wb_serializer.FloatField(
                percent=True,
                precision=3,
                read_only=True,
                **get_default_attrs(cls, "gross_profit_margin_without_depreciation_y4"),
            ),
            "gross_profit_margin_without_depreciation_y5": wb_serializer.FloatField(
                percent=True,
                precision=3,
                read_only=True,
                **get_default_attrs(cls, "gross_profit_margin_without_depreciation_y5"),
            ),
            "gross_profit_margin_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "gross_profit_margin_y1")
            ),
            "gross_profit_margin_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "gross_profit_margin_y2")
            ),
            "gross_profit_margin_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "gross_profit_margin_y3")
            ),
            "gross_profit_margin_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "gross_profit_margin_y4")
            ),
            "gross_profit_margin_y5": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "gross_profit_margin_y5")
            ),
            "gross_profit_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "gross_profit_y1"),
            ),
            "gross_profit_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "gross_profit_y2"),
            ),
            "gross_profit_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "gross_profit_y3"),
            ),
            "gross_profit_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "gross_profit_y4"),
            ),
            "gross_profit_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "gross_profit_y5"),
            ),
            "reported_net_profit_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "reported_net_profit_y1"),
            ),
            "reported_net_profit_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "reported_net_profit_y2"),
            ),
            "reported_net_profit_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "reported_net_profit_y3"),
            ),
            "reported_net_profit_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "reported_net_profit_y4"),
            ),
            "reported_net_profit_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "reported_net_profit_y5"),
            ),
            "adjusted_net_profit_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "adjusted_net_profit_y1"),
            ),
            "adjusted_net_profit_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "adjusted_net_profit_y2"),
            ),
            "adjusted_net_profit_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "adjusted_net_profit_y3"),
            ),
            "adjusted_net_profit_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "adjusted_net_profit_y4"),
            ),
            "adjusted_net_profit_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "adjusted_net_profit_y5"),
            ),
            "net_profit_margin_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "net_profit_margin_y1")
            ),
            "net_profit_margin_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "net_profit_margin_y2")
            ),
            "net_profit_margin_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "net_profit_margin_y3")
            ),
            "net_profit_margin_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "net_profit_margin_y4")
            ),
            "net_profit_margin_y5": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "net_profit_margin_y5")
            ),
            "ebitda_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebitda_y1"),
            ),
            "ebitda_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebitda_y2"),
            ),
            "ebitda_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebitda_y3"),
            ),
            "ebitda_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebitda_y4"),
            ),
            "ebitda_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebitda_y5"),
            ),
            "ebitda_margin_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebitda_margin_y1")
            ),
            "ebitda_margin_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebitda_margin_y2")
            ),
            "ebitda_margin_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebitda_margin_y3")
            ),
            "ebitda_margin_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebitda_margin_y4")
            ),
            "ebitda_margin_y5": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebitda_margin_y5")
            ),
            "ebit_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebit_y1"),
            ),
            "ebit_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebit_y2"),
            ),
            "ebit_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebit_y3"),
            ),
            "ebit_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebit_y4"),
            ),
            "ebit_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "ebit_y5"),
            ),
            "ebit_margin_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebit_margin_y1")
            ),
            "ebit_margin_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebit_margin_y2")
            ),
            "ebit_margin_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebit_margin_y3")
            ),
            "ebit_margin_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebit_margin_y4")
            ),
            "ebit_margin_y5": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "ebit_margin_y5")
            ),
            "eps_y1": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps_y1"),
            ),
            "eps_y2": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps_y2"),
            ),
            "eps_y3": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps_y3"),
            ),
            "eps_y4": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps_y4"),
            ),
            "eps_y5": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps_y5"),
            ),
            "eps_growth_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "eps_growth_y1")
            ),
            "eps_growth_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "eps_growth_y2")
            ),
            "eps_growth_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "eps_growth_y3")
            ),
            "eps_growth_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "eps_growth_y4")
            ),
            "eps_growth_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "eps_growth_y5"),
            ),
            "net_debt_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "net_debt_y1"),
            ),
            "net_debt_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "net_debt_y2"),
            ),
            "net_debt_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "net_debt_y3"),
            ),
            "net_debt_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "net_debt_y4"),
            ),
            "net_debt_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "net_debt_y5"),
            ),
            "net_debt_to_ebitda_ratio_y1": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "net_debt_to_ebitda_ratio_y1")
            ),
            "net_debt_to_ebitda_ratio_y2": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "net_debt_to_ebitda_ratio_y2")
            ),
            "net_debt_to_ebitda_ratio_y3": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "net_debt_to_ebitda_ratio_y3")
            ),
            "net_debt_to_ebitda_ratio_y4": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "net_debt_to_ebitda_ratio_y4")
            ),
            "net_debt_to_ebitda_ratio_y5": wb_serializer.FloatField(
                precision=1, read_only=True, **get_default_attrs(cls, "net_debt_to_ebitda_ratio_y5")
            ),
            "entreprise_value_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "entreprise_value_y1"),
            ),
            "entreprise_value_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "entreprise_value_y2"),
            ),
            "entreprise_value_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "entreprise_value_y3"),
            ),
            "entreprise_value_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "entreprise_value_y4"),
            ),
            "entreprise_value_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "entreprise_value_y5"),
            ),
            "free_cash_flow_y1": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash_flow_y1"),
            ),
            "free_cash_flow_y2": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash_flow_y2"),
            ),
            "free_cash_flow_y3": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash_flow_y3"),
            ),
            "free_cash_flow_y4": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash_flow_y4"),
            ),
            "free_cash_flow_y5": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "free_cash_flow_y5"),
            ),
            "free_cash_flow_growth_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_growth_y1")
            ),
            "free_cash_flow_growth_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_growth_y2")
            ),
            "free_cash_flow_growth_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_growth_y3")
            ),
            "free_cash_flow_growth_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_growth_y4")
            ),
            "free_cash_flow_growth_y5": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_growth_y5")
            ),
            "free_cash_flow_to_sales_ratio_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_to_sales_ratio_y1")
            ),
            "free_cash_flow_to_sales_ratio_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_to_sales_ratio_y2")
            ),
            "free_cash_flow_to_sales_ratio_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_to_sales_ratio_y3")
            ),
            "free_cash_flow_to_sales_ratio_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_to_sales_ratio_y4")
            ),
            "free_cash_flow_to_sales_ratio_y5": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "free_cash_flow_to_sales_ratio_y5")
            ),
            "expected_book_value_per_share_y1": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "expected_book_value_per_share_y1"),
            ),
            "expected_book_value_per_share_y2": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "expected_book_value_per_share_y2"),
            ),
            "expected_book_value_per_share_y3": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "expected_book_value_per_share_y3"),
            ),
            "expected_book_value_per_share_y4": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "expected_book_value_per_share_y4"),
            ),
            "expected_book_value_per_share_y5": wb_serializer.FloatField(
                precision=2,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "expected_book_value_per_share_y5"),
            ),
            "capital_expenditures_y1": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "capital_expenditures_y1"),
            ),
            "capital_expenditures_y2": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "capital_expenditures_y2"),
            ),
            "capital_expenditures_y3": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "capital_expenditures_y3"),
            ),
            "capital_expenditures_y4": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "capital_expenditures_y4"),
            ),
            "capital_expenditures_y5": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=1,
                decorators=[
                    wb_serializer.decorator(decorator_type="text", position="left", value="{{currency_repr}}")
                ],
                read_only=True,
                **get_default_attrs(cls, "capital_expenditures_y5"),
            ),
            "capex_to_sales_y1": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "capex_to_sales_y1")
            ),
            "capex_to_sales_y2": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "capex_to_sales_y2")
            ),
            "capex_to_sales_y3": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "capex_to_sales_y3")
            ),
            "capex_to_sales_y4": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "capex_to_sales_y4")
            ),
            "capex_to_sales_y5": wb_serializer.FloatField(
                percent=True, precision=3, read_only=True, **get_default_attrs(cls, "capex_to_sales_y5")
            ),
            "return_on_equity_y1": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_equity_y1")
            ),
            "return_on_equity_y2": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_equity_y2")
            ),
            "return_on_equity_y3": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_equity_y3")
            ),
            "return_on_equity_y4": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_equity_y4")
            ),
            "return_on_equity_y5": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_equity_y5")
            ),
            "return_on_assets_y1": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_assets_y1")
            ),
            "return_on_assets_y2": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_assets_y2")
            ),
            "return_on_assets_y3": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_assets_y3")
            ),
            "return_on_assets_y4": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_assets_y4")
            ),
            "return_on_assets_y5": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_assets_y5")
            ),
            "return_on_capital_employed_y1": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_capital_employed_y1")
            ),
            "return_on_capital_employed_y2": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_capital_employed_y2")
            ),
            "return_on_capital_employed_y3": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_capital_employed_y3")
            ),
            "return_on_capital_employed_y4": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_capital_employed_y4")
            ),
            "return_on_capital_employed_y5": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_capital_employed_y5")
            ),
            "return_on_invested_capital_y1": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_invested_capital_y1")
            ),
            "return_on_invested_capital_y2": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_invested_capital_y2")
            ),
            "return_on_invested_capital_y3": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_invested_capital_y3")
            ),
            "return_on_invested_capital_y4": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_invested_capital_y4")
            ),
            "return_on_invested_capital_y5": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "return_on_invested_capital_y5")
            ),
            "interest_coverage_ratio_y1": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "interest_coverage_ratio_y1")
            ),
            "interest_coverage_ratio_y2": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "interest_coverage_ratio_y2")
            ),
            "interest_coverage_ratio_y3": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "interest_coverage_ratio_y3")
            ),
            "interest_coverage_ratio_y4": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "interest_coverage_ratio_y4")
            ),
            "interest_coverage_ratio_y5": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "interest_coverage_ratio_y5")
            ),
        }


class InstrumentPriceSerializerFieldMixin:
    @classmethod
    def get_number_serializer_fields(cls):
        return {
            "net_value": wb_serializer.FloatField(precision=2, read_only=True, **get_default_attrs(cls, "net_value")),
            "gross_value": wb_serializer.FloatField(
                precision=2, read_only=True, **get_default_attrs(cls, "gross_value")
            ),
            "outstanding_shares": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED,
                precision=2,
                read_only=True,
                **get_default_attrs(cls, "outstanding_shares"),
            ),
            "outstanding_shares_consolidated": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "outstanding_shares_consolidated")
            ),
            "volume": wb_serializer.FloatField(
                display_mode=DisplayMode.SHORTENED, precision=2, read_only=True, **get_default_attrs(cls, "volume")
            ),
            "volume_50d": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "volume_50d")),
            "volume_200d": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "volume_200d")),
            "market_capitalization": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "market_capitalization")
            ),
            "market_capitalization_consolidated": wb_serializer.FloatField(
                read_only=True, **get_default_attrs(cls, "market_capitalization_consolidated")
            ),
            "sharpe_ratio": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "sharpe_ratio")),
            "correlation": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "correlation")),
            "beta": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "beta")),
            # "custom_beta_180d": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "custom_beta_180d")),
            # "custom_beta_1y": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "custom_beta_1y")),
            # "custom_beta_2y": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "custom_beta_2y")),
            # "custom_beta_3y": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "custom_beta_3y")),
            # "custom_beta_5y": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "custom_beta_5y")),
            # "performance_1d": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "performance_1d")),
            # "performance_7d": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "performance_7d")),
            # "performance_30d": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "performance_30d")),
            # "performance_90d": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "performance_90d")),
            # "performance_365d": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "performance_365d")),
            # "performance_ytd": wb_serializer.FloatField(read_only=True, **get_default_attrs(cls, "performance_ytd")),
            # "performance_inception": wb_serializer.FloatField(
            #     read_only=True, **get_default_attrs(cls, "performance_inception")
            # ),
        }
