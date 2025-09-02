from django.db.models import TextChoices
from wbcore.utils.enum import ChoiceEnum


class StatementType(ChoiceEnum):
    INCOME_STATEMENT = "incomestatment"
    BALANCE_SHEET = "balancesheet"
    CASHFLOW_STATEMENT = "cashflowstatement"


class MarketData(ChoiceEnum):
    """This enum holds the datatypes about recurring periodic market data, usually daily such as pricing data"""

    OPEN = "open"
    CLOSE = "close"
    HIGH = "high"
    LOW = "low"
    BID = "bid"
    ASK = "ask"
    VWAP = "vwap"
    VOLUME = "volume"
    SHARES_OUTSTANDING = "outstanding_shares"
    MARKET_CAPITALIZATION = "market_capitalization"

    @classmethod
    def name_mapping(cls):
        return {
            cls.CLOSE.value: "Closing Price",
            cls.MARKET_CAPITALIZATION.value: "Market Cap.",
        }


class Frequency(ChoiceEnum):
    """This enum holds the information about the frequency of returned market data"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Financial(ChoiceEnum):
    """This enum holds the datatypes about recurring financial data, such as revenue"""

    REVENUE = "revenue"
    TOTAL_OPERATING_EXPENSES = "operating_expenses"
    OPERATING_INCOME = "operating_income"
    GROSS_PROFIT = "gross_profit"
    NET_INCOME_BEFORE_TAXES = "pbt"
    NET_INCOME = "net_income"
    EPS = "eps"
    FREE_CASH_FLOW = "free_cash_flow"
    EBITDA = "ebitda"
    EBITDA_PER_SHARE = "ebitda_sh"
    NET_DEBT = "net_debt"
    ENTERPRISE_VALUE = "ev"
    SHARES_OUTSTANDING = "shares_outstanding"
    COST_OF_GOODS_SOLD = "cogs"
    GROSS_PROFIT_MARGIN = "gross_profit_margin"
    SELLING_MARKETING_EXPENSES = "selling_marketing_expenses"
    SGA_EXPENSES = "sga_expenses"
    GENERAL_ADMIN_EXPENSES = "general_admin_expenses"
    RND_EXPENSES = "rnd_expenses"
    STOCK_COMPENSATION = "stock_compensation"
    DEPRECATION = "deprecation"
    AMORTIZATION = "amortization"
    EBIT = "ebit"
    INTEREST_EXPENSE = "interest_expense"
    TAX_PROVISION = "tax_provision"
    TAX_RATE = "tax_rate"
    EBITDA_REPORTED = "ebitda_reported"
    NET_INCOME_BEFORE_TAXES_REPORTED = "pbt_reported"
    NET_INCOME_REPORTED = "net_income_reported"
    EPS_REPORTED = "eps_reported"
    DIVIDEND_PER_SHARE = "dividend_per_share"
    WORKING_CAPITAL = "working_capital"
    INCOME_TAXES_PAID = "income_taxed_paid"
    CASH_FLOW_FROM_OPERATIONS = "cash_flow_from_operations"
    CAPEX = "capex"
    CASH_FLOW_FROM_INVESTING = "cash_flow_from_investing"
    FREE_CASH_FLOW_PER_SHARE = "free_cash_flow_per_share"
    TOTAL_DIVIDENDS = "total_dividends"
    CASH_FLOW_FROM_FINANCING = "cash_flow_from_financing"
    CASH_FLOW_PER_SHARE = "cash_flow_per_share"
    CASH_EQUIVALENTS = "cash_equivalents"
    INVENTORY = "inventory"
    CURRENT_ASSETS = "current_assets"
    TOTAL_ASSETS = "total_assets"
    CURRENT_LIABILITIES = "current_liabilities"
    CURRENT_DEFERRED_REVENUE = "current_deferred_revenue"
    TOTAL_DEBT = "total_debt"
    SHAREHOLDERS_EQUITY = "shareholders_equity"
    GOODWILL = "goodwill"
    NET_ASSET_VALUE = "net_asset_value"
    BOOK_VALUE_PER_SHARE = "book_value_per_share"
    TANGIBLE_BOOK_VALUE_PER_SHARE = "tangible_book_value_per_share"
    TANGIBLE_BOOK_VALUE = "tangible_book_value"
    RETURN_ON_ASSETS = "roa"
    RETURN_ON_CAPITAL = "roc"
    RETURN_ON_INVESTED_CAPITAL = "roic"
    RETURN_ON_EQUITY = "roe"

    EMPLOYEES = "employees"
    CASH_AND_SHORT_TERM_INVESTMENT = "cash_and_short_term_investment"
    DILUTED_WEIGHTED_AVG_SHARES = "diluded_weighted_avg_shares"

    @classmethod
    def name_mapping(cls):
        return {
            cls.REVENUE.value: "Revenue",
            cls.TOTAL_OPERATING_EXPENSES.value: "Total Operating Expenses",
            cls.OPERATING_INCOME.value: "Operating Income",
            cls.GROSS_PROFIT.value: "Gross Profit",
            cls.NET_INCOME_BEFORE_TAXES.value: "Net Income Before Taxes",
            cls.NET_INCOME.value: "Net Income",
            cls.EPS.value: "EPS",
            cls.FREE_CASH_FLOW.value: "Free Cash Flow",
            cls.EBITDA.value: "EBITDA",
            cls.EBITDA_PER_SHARE.value: "EBITDA per Share",
            cls.NET_DEBT.value: "Net Debt",
            cls.ENTERPRISE_VALUE.value: "Enterprise Value",
            cls.SHARES_OUTSTANDING.value: "Shares Outstanding",
            cls.COST_OF_GOODS_SOLD.value: "Cost of goods sold",
            cls.GROSS_PROFIT_MARGIN.value: "Gross Profit Margin",
            cls.SELLING_MARKETING_EXPENSES.value: "Selling/Marketing Expenses",
            cls.SGA_EXPENSES.value: "SG&A Expenses",
            cls.GENERAL_ADMIN_EXPENSES.value: "General & Admin. Expenses",
            cls.RND_EXPENSES.value: "R&D Expenses",
            cls.STOCK_COMPENSATION.value: "Stock based comp.",
            cls.DEPRECATION.value: "Deprecation",
            cls.AMORTIZATION.value: "Amortization",
            cls.EBIT.value: "EBIT",
            cls.INTEREST_EXPENSE.value: "Interest Expenses",
            cls.TAX_PROVISION.value: "Tax Provision",
            cls.TAX_RATE.value: "Tax Rate",
            cls.EBITDA_REPORTED.value: "EBITDA (Reported)",
            cls.NET_INCOME_BEFORE_TAXES_REPORTED.value: "Net Income Before Taxes (Reported)",
            cls.NET_INCOME_REPORTED.value: "Net Income (Reported)",
            cls.EPS_REPORTED.value: "EPS (Reported)",
            cls.DIVIDEND_PER_SHARE.value: "Dividend per Share",
            cls.WORKING_CAPITAL.value: "Working Capital",
            cls.INCOME_TAXES_PAID.value: "Income Taxes Paid",
            cls.CASH_FLOW_FROM_OPERATIONS.value: "Cash Flow from Operations",
            cls.CAPEX.value: "Capital Expenditures",
            cls.CASH_FLOW_FROM_INVESTING.value: "Cash Flow from Investing",
            cls.FREE_CASH_FLOW_PER_SHARE.value: "Free Cash Flow per Share",
            cls.TOTAL_DIVIDENDS.value: "Total Dividends",
            cls.CASH_FLOW_FROM_FINANCING.value: "Cash Flow from Financing",
            cls.CASH_FLOW_PER_SHARE.value: "Cash Flow per Share",
            cls.CASH_EQUIVALENTS.value: "Cash & Cash Equivalents",
            cls.INVENTORY.value: "Inventory",
            cls.CURRENT_ASSETS.value: "Current Assets",
            cls.TOTAL_ASSETS.value: "Total Assets",
            cls.CURRENT_LIABILITIES.value: "Current Liabilities",
            cls.CURRENT_DEFERRED_REVENUE.value: "Current deferred Revenue",
            cls.TOTAL_DEBT.value: "Total Debt",
            cls.SHAREHOLDERS_EQUITY.value: "Shareholders Equity",
            cls.GOODWILL.value: "Goodwill",
            cls.NET_ASSET_VALUE.value: "Net Asset Value",
            cls.BOOK_VALUE_PER_SHARE.value: "Book Value per Share",
            cls.TANGIBLE_BOOK_VALUE_PER_SHARE.value: "Tangible Book Value per Share",
            cls.TANGIBLE_BOOK_VALUE.value: "Tangible Book Value",
            cls.RETURN_ON_ASSETS.value: "Return of Assets (ROA)",
            cls.RETURN_ON_CAPITAL.value: "Return on Captial (ROC)",
            cls.RETURN_ON_INVESTED_CAPITAL.value: "Return on invested Capital (ROIC)",
            cls.RETURN_ON_EQUITY.value: "Return on Equity (ROE)",
            cls.EMPLOYEES.value: "# Employees",
            cls.CASH_AND_SHORT_TERM_INVESTMENT.value: "Cash & Short Term Investments",
            cls.DILUTED_WEIGHTED_AVG_SHARES.value: "Diluted Weighted Average Shares",
            "net_debt_ebitda_ratio": "Net Debt/EBITDA",
            "total_debt_ebitda_ratio": "Total Debt/EBITDA",
            "fcf_total_debt_ratio": "FCF/Total Debt",
            "cfo_total_debt_ratio": "CFO/Total Debt",
            "total_debt_equity_ratio": "Total Debt / Equity",
            "total_debt_capital_ratio": "Total Debt / Capital",
            "current_ratio": "Current Ratio",
            "cash_from_operation_current_liabilities_ratio": "Cash from Ops. To Curr Liab.",
            "asset_turnover": "Asset Turnover",
            "current_liability_coverage_ratio": "Current Liability Coverage Ratio",
            "cash_flow_margin": "Cash Flow Margin (%)",
            "asset_efficiency_margin": "Asset Efficiency (%)",
            "net_debt_coverage_ratio": "Net Debt Coverage Ratio",
            "gross_margin": "Gross Margin (%)",
            "sga_margin": "SG&A Margin (%)",
            "ebitda_margin": "EBITDA Margin (%)",
            "ebit_margin": "EBIT Margin (%)",
            "net_income_margin": "Net Income Margin (%)",
            "free_cash_flow_margin": "Free Cash Flow Margin (%)",
            "price_sales_ratio": "Price / Sales",
            "price_earning_reported_ratio": "P / E(Reported)",
            "price_earning_ratio": "P/E",
            "ev_ebitda_ratio": "EV/EBITDA",
            "ev_ebit_ratio": "EV/EBIT",
            "price_to_cash_flow_ratio": "Price to Cash Flow",
            "price_to_book_ratio": "Price to Book",
            "roce": "ROCE",
            "price_to_tangible_bv_ratio": "Price to Tangible BV",
            "cash_shares_ratio": "Cash/Shares",
            "total_debt_shares_ratio": "Total Debt/Shares",
            "net_debt_shares_ratio": "Net Debt/Shares",
            "stock_compensation_employee_ratio": "Stock based comp. / Employee",
            "net_cash": "Net Cash",
        }


class ESG(ChoiceEnum):
    CARBON_EMISSIONS_SCOPE_1 = "carbon_emissions_scope_1"
    CARBON_EMISSIONS_SCOPE_1_KEY = "carbon_emissions_scope_1_key"
    CARBON_EMISSIONS_SCOPE_2 = "carbon_emissions_scope_2"
    CARBON_EMISSIONS_SCOPE_2_KEY = "carbon_emissions_scope_2_key"
    CARBON_EMISSIONS_SCOPE_3_TOTAL = "carbon_emissions_scope_3_total"
    CARBON_EMISSIONS_SCOPE_3_YEAR = "carbon_emissions_scope_3_year"
    CARBON_EMISSIONS_SOURCE = "carbon_emissions_source"
    CARBON_EMISSIONS_YEAR = "carbon_emissions_year"
    CARBON_EMISSIONS_SCOPE123_EVIC_EUR = "carbon_emissions_scope123_evic_eur"
    CARBON_EMISSIONS_SCOPE123 = "carbon_emissions_scope123"
    CARBON_EMISSIONS_SCOPE123_KEY = "carbon_emissions_scope123_key"
    CARBON_EMISSIONS_SALES_EUR_SCOPE_ALL = "carbon_emissions_sales_eur_scope_all"
    ACTIVE_FF_SECTOR_EXPOSURE = "active_ff_sector_exposure"
    ACTIVE_FF_SECTOR_EXPOSURE_SOURCE = "active_ff_sector_exposure_source"
    ACTIVE_FF_SECTOR_EXPOSURE_YEAR = "active_ff_sector_exposure_year"
    PCT_NON_RENEW_CONSUMPTION_PRODUCTION = "pct_non_renew_consumption_production"
    PCT_TOTAL_NON_RENEW_CONSUMPTION = "pct_total_non_renew_consumption"
    PCT_TOTAL_NON_RENEW_PRODUCTION = "pct_total_non_renew_production"
    TOTAL_RENEW_ENERGY_CONSUMPTION = "total_renew_energy_consumption"
    TOTAL_RENEW_ENERGY_CONSUMPTION_SOURCE = "total_renew_energy_consumption_source"
    TOTAL_RENEW_ENERGY_CONSUMPTION_YEAR = "total_renew_energy_consumption_year"
    TOTAL_NON_RENEW_ENERGY_CONSUMPTION = "total_non_renew_energy_consumption"
    TOTAL_NON_RENEW_ENERGY_CONSUMPTION_SOURCE = "total_non_renew_energy_consumption_source"
    TOTAL_NON_RENEW_ENERGY_CONSUMPTION_YEAR = "total_non_renew_energy_consumption_year"
    TOTAL_NON_RENEW_ENERGY_CONSUMPTION_PRODUCTION = "total_non_renew_energy_consumption_production"
    TOTAL_NON_RENEW_ENERGY_CONSUMPTION_PRODUCTION_SOURCE = "total_non_renew_energy_consumption_production_source"
    TOTAL_NON_RENEW_ENERGY_CONSUMPTION_PRODUCTION_YEAR = "total_non_renew_energy_consumption_production_year"
    TOTAL_ENERGY_CONSUMPTION = "total_energy_consumption"
    TOTAL_ENERGY_CONSUMPTION_SOURCE = "total_energy_consumption_source"
    TOTAL_ENERGY_CONSUMPTION_YEAR = "total_energy_consumption_year"
    ENERGY_CONSUMPTION_INTENSITY_EUR = "energy_consumption_intensity_eur"
    ENERGY_CONSUMPTION_INTENSITY_EUR_SOURCE = "energy_consumption_intensity_eur_source"
    ENERGY_CONSUMPTION_INTENSITY_EUR_YEAR = "energy_consumption_intensity_eur_year"
    OPS_BIODIV_CONTROVERSITIES = "ops_biodiv_controversities"
    OPS_BIODIV_AREAS = "ops_biodiv_areas"
    WATER_EMISSIONS = "water_emissions"
    WATER_EMISSIONS_YEAR = "water_emissions_year"
    WATER_EMISSIONS_SOURCE = "water_emissions_source"
    HAZARD_WASTE = "hazard_waste"
    HAZARD_WASTE_YEAR = "hazard_waste_year"
    HAZARD_WASTE_SOURCE = "hazard_waste_source"
    OECD_ALIGNMENT = "oecd_alignment"
    LABOR_DDP = "labor_ddp"
    COMPLIANCE_GLOBAL_IMPACT = "compliance_global_impact"
    GENDER_PAY_GAP_RATIO = "gender_pay_gap_ratio"
    GENDER_PAY_GAP_RATIO_YEAR = "gender_pay_gap_ratio_year"
    GENDER_PAY_GAP_RATIO_SOURCE = "gender_pay_gap_ratio_source"
    PCT_FEMALE_DIRECTORS = "pct_female_directors"
    CONTROVERSIAL_WEAPONS = "controversial_weapons"
    CONTROVERSIAL_WEAPONS_SOURCE = "controversial_weapons_source"
    CVI_FACTOR = "cvi_factor"
    EVIC_EUR = "evic_eur"
    NACE_SECTION_CODE = "nace_section_code"

    @classmethod
    def mapping(cls):
        return {
            cls.CARBON_EMISSIONS_SCOPE_1.value: (
                1,
                "GHG emissions",
                "Scope 1 GHC Emissions",
                "Carbon Emission Scope 1 (metric tons)",
            ),
            cls.CARBON_EMISSIONS_SCOPE_1_KEY.value: (
                1,
                "GHG emissions",
                "Scope 1 GHC Emissions",
                "Carbon Emissions - Scope 1 KEY",
            ),
            cls.CARBON_EMISSIONS_SCOPE_2.value: (
                1,
                "GHG emissions",
                "Scope 2 GHC Emissions",
                "Carbon Emission Scope 2 (metric tons)",
            ),
            cls.CARBON_EMISSIONS_SCOPE_2_KEY.value: (
                1,
                "GHG emissions",
                "Scope 2 GHC Emissions",
                "Carbon Emissions - Scope 2 KEY",
            ),
            cls.CARBON_EMISSIONS_SCOPE_3_TOTAL.value: (
                1,
                "GHG emissions",
                "Scope 3 Total GHC Emissions",
                "Scope 3 - Total Emissions Estimated",
            ),
            cls.CARBON_EMISSIONS_SCOPE_3_YEAR.value: (
                1,
                "GHG emissions",
                "Scope 3 Total GHC Emissions",
                "Scope 3 - Total Emissions Estimated Year",
            ),
            cls.CARBON_EMISSIONS_SOURCE.value: (
                1,
                "GHG emissions",
                "Total GHG emissions",
                "Carbon Emissions - Source",
            ),
            cls.CARBON_EMISSIONS_YEAR.value: (1, "GHG emissions", "Total GHG emissions", "Carbon Emissions - Year"),
            cls.CARBON_EMISSIONS_SCOPE123.value: (
                2,
                "Carbon footprint",
                "Scope 123 GHC Emissions",
                "Total GHG Emissions (Scopes 1, 2 and 3)",
            ),
            cls.CARBON_EMISSIONS_SCOPE123_KEY.value: (
                2,
                "Carbon footprint",
                "Scope 123 GHC Emissions",
                "Total GHG Emissions (Scopes 1, 2 and 3 Key)",
            ),
            cls.CARBON_EMISSIONS_SCOPE123_EVIC_EUR.value: (
                2,
                "Carbon footprint",
                "Carbon footprint",
                "Total GHG Emissions Intensity per EUR million EVIC (t/EUR million EVIC)",
            ),
            cls.CARBON_EMISSIONS_SALES_EUR_SCOPE_ALL.value: (
                3,
                "GHG intensity of investee companies",
                "GHG intensity of investee companies",
                "Total GHG Emissions Intensity per EUR million Sales (t/EUR million sales)",
            ),
            cls.ACTIVE_FF_SECTOR_EXPOSURE.value: (
                4,
                "Exposure to companies active in the fossil fuel sector",
                "Share of investments in companies active in the fossil fuel sector",
                "Active Fossil Fuel Sector Exposure",
            ),
            cls.ACTIVE_FF_SECTOR_EXPOSURE_SOURCE.value: (
                4,
                "Exposure to companies active in the fossil fuel sector",
                "Share of investments in companies active in the fossil fuel sector",
                "Active Fossil Fuel Sector Exposure - Source",
            ),
            cls.ACTIVE_FF_SECTOR_EXPOSURE_YEAR.value: (
                4,
                "Exposure to companies active in the fossil fuel sector",
                "Share of investments in companies active in the fossil fuel sector",
                "Active Fossil Fuel Sector Exposure - Year",
            ),
            cls.PCT_NON_RENEW_CONSUMPTION_PRODUCTION.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Percentage of non-renewable energy consumption and production",
            ),
            cls.PCT_TOTAL_NON_RENEW_CONSUMPTION.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Percentage of Total Energy Consumption from Non-renewable Sources",
            ),
            cls.PCT_TOTAL_NON_RENEW_PRODUCTION.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Percentage of Total Energy Production from Non-renewable Sources",
            ),
            cls.TOTAL_RENEW_ENERGY_CONSUMPTION.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total energy consumption from renewable sources (GWh)",
            ),
            cls.TOTAL_RENEW_ENERGY_CONSUMPTION_SOURCE.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total energy consumption from renewable sources (GWh) Source",
            ),
            cls.TOTAL_RENEW_ENERGY_CONSUMPTION_YEAR.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total energy consumption from renewable sources (GWh) Year",
            ),
            cls.TOTAL_NON_RENEW_ENERGY_CONSUMPTION.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total energy consumption from non-renewable sources (GWh)",
            ),
            cls.TOTAL_NON_RENEW_ENERGY_CONSUMPTION_SOURCE.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total energy consumption from non-renewable sources (GWh) Source",
            ),
            cls.TOTAL_NON_RENEW_ENERGY_CONSUMPTION_YEAR.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total energy consumption from non-renewable sources (GWh) Year",
            ),
            cls.TOTAL_NON_RENEW_ENERGY_CONSUMPTION_PRODUCTION.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total Energy Consumption and Production from Non-renewable Sources (GWh)",
            ),
            cls.TOTAL_NON_RENEW_ENERGY_CONSUMPTION_PRODUCTION_SOURCE.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total Energy Consumption and Production from Non-renewable Sources (GWh) Source",
            ),
            cls.TOTAL_NON_RENEW_ENERGY_CONSUMPTION_PRODUCTION_YEAR.value: (
                5,
                "Share of nonrenewable energy consumption and production",
                "Share of non-renewable energy consumption and non-renewable energy production of investee companies from non-renewable energy sources compared to renewable energy sources, expressed as a percentage",
                "Total Energy Consumption and Production from Non-renewable Sources (GWh) Year",
            ),
            cls.TOTAL_ENERGY_CONSUMPTION.value: (
                5,
                "Energy consumption intensity per high impact climate sector",
                "Total Energy consumption",
                "Total energy consumption (GWh)",
            ),
            cls.TOTAL_ENERGY_CONSUMPTION_SOURCE.value: (
                5,
                "Energy consumption intensity per high impact climate sector",
                "Total Energy consumption",
                "Total energy consumption (GWh) - Source",
            ),
            cls.TOTAL_ENERGY_CONSUMPTION_YEAR.value: (
                5,
                "Energy consumption intensity per high impact climate sector",
                "Total Energy consumption",
                "Total energy consumption (GWh) - Year",
            ),
            cls.ENERGY_CONSUMPTION_INTENSITY_EUR.value: (
                6,
                "Energy consumption intensity per high impact climate sector",
                "Energy consumption in GWh per million EUR of revenue of investee companies, per high impact climate sector",
                "Energy consumption intensity (GWh / EUR million sales)",
            ),
            cls.ENERGY_CONSUMPTION_INTENSITY_EUR_SOURCE.value: (
                6,
                "Energy consumption intensity per high impact climate sector",
                "Energy consumption in GWh per million EUR of revenue of investee companies, per high impact climate sector",
                "Energy consumption intensity (GWh / EUR million sales) - Source",
            ),
            cls.ENERGY_CONSUMPTION_INTENSITY_EUR_YEAR.value: (
                6,
                "Energy consumption intensity per high impact climate sector",
                "Energy consumption in GWh per million EUR of revenue of investee companies, per high impact climate sector",
                "Energy consumption intensity (GWh / EUR million sales) - Year",
            ),
            cls.OPS_BIODIV_CONTROVERSITIES.value: (
                7,
                "Activities negatively affecting biodiversity sensitive areas",
                "Share of investments in investee companies with sites/operations located in or near to biodiversitysensitive areas where activities of those investee companies negatively affect those areas",
                "Company has operations located in biodiversity sensitive areas and is involved in controversies with severe impact on the environment",
            ),
            cls.OPS_BIODIV_AREAS.value: (
                7,
                "Activities negatively affecting biodiversity sensitive areas",
                "Share of investments in investee companies with sites/operations located in or near to biodiversitysensitive areas where activities of those investee companies negatively affect those areas",
                "Operational sites owned, leased, managed in, or adjacent to, protected areas and areas of high biodiversity value outside protected areas",
            ),
            cls.WATER_EMISSIONS.value: (
                8,
                "Emissions to water",
                "Tonnes of emissions to water generated by investee companies per million EUR invested, expressed as a weighted average",
                "Water Emissions (metric tons)",
            ),
            cls.WATER_EMISSIONS_SOURCE.value: (
                8,
                "Emissions to water",
                "Tonnes of emissions to water generated by investee companies per million EUR invested, expressed as a weighted average",
                "Water Emissions (metric tons) - Source",
            ),
            cls.WATER_EMISSIONS_YEAR.value: (
                8,
                "Emissions to water",
                "Tonnes of emissions to water generated by investee companies per million EUR invested, expressed as a weighted average",
                "Water Emissions (metric tons) - Year",
            ),
            cls.HAZARD_WASTE.value: (
                9,
                "Hazardous waste ratio",
                "Tonnes of hazardous waste generated by investee companies per million EUR invested, expressed as a weighted average",
                "Hazardous Waste (metric tons)",
            ),
            cls.HAZARD_WASTE_YEAR.value: (
                9,
                "Hazardous waste ratio",
                "Tonnes of hazardous waste generated by investee companies per million EUR invested, expressed as a weighted average",
                "Hazardous Waste (metric tons) - Year",
            ),
            cls.OECD_ALIGNMENT.value: (
                10,
                "Violations of UN Global Compact principles and Organisation for Economic Cooperation and Development (OECD) Guidelines for Multinational Enterprises",
                "Share of investments in investee companies that have been involved in violations of the UNGC principles or OECD Guidelines for Multinational Enterprises",
                "OECD Alignment",
            ),
            cls.LABOR_DDP.value: (
                11,
                "Lack of processes and compliance mechanisms to monitor compliance with UN Global Compact principles and OECD Guidelines for Multinational Enterprises",
                "Share of investments in investee companies without policies to monitor compliance with the UNGC principles or OECD Guidelines for Multinational Enterprises or grievance /complaints handling mechanisms to address violations of the UNGC principles or OECD Guidelines for Multinational Enterprises",
                "Labor Due Diligence Policy (ILO)",
            ),
            cls.COMPLIANCE_GLOBAL_IMPACT.value: (
                11,
                "Lack of processes and compliance mechanisms to monitor compliance with UN Global Compact principles and OECD Guidelines for Multinational Enterprises",
                "Share of investments in investee companies without policies to monitor compliance with the UNGC principles or OECD Guidelines for Multinational Enterprises or grievance /complaints handling mechanisms to address violations of the UNGC principles or OECD Guidelines for Multinational Enterprises",
                "Mechanism to monitor compliance with UN Global Compact",
            ),
            cls.GENDER_PAY_GAP_RATIO.value: (
                12,
                "Unadjusted gender pay gap",
                "Average unadjusted gender pay gap of investee companies",
                "Gender pay gap ratio",
            ),
            cls.GENDER_PAY_GAP_RATIO_YEAR.value: (
                12,
                "Unadjusted gender pay gap",
                "Average unadjusted gender pay gap of investee companies",
                "Gender pay gap ratio - Year",
            ),
            cls.GENDER_PAY_GAP_RATIO_SOURCE.value: (
                12,
                "Unadjusted gender pay gap",
                "Average unadjusted gender pay gap of investee companies",
                "Gender pay gap ratio - Source",
            ),
            cls.PCT_FEMALE_DIRECTORS.value: (
                13,
                "Board gender diversity",
                "Average ratio of female to male board members in investee companies, expressed as a percentage of all board members",
                "Female Directors Percentage",
            ),
            cls.CONTROVERSIAL_WEAPONS.value: (
                14,
                "Exposure to controversial weapons (antipersonnel mines, cluster munitions, chemical weapons and biological weapons)",
                "Share of investments in investee companies involved in the manufacture or selling of controversial weapons",
                "Exposure to controversial weapons (landmines, cluster munitions, chemical weapons and biological weapons)",
            ),
            cls.CONTROVERSIAL_WEAPONS_SOURCE.value: (
                14,
                "Exposure to controversial weapons (antipersonnel mines, cluster munitions, chemical weapons and biological weapons)",
                "Share of investments in investee companies involved in the manufacture or selling of controversial weapons",
                "Exposure to controversial weapons (landmines, cluster munitions, chemical weapons and biological weapons) - Source",
            ),
            cls.CVI_FACTOR.value: (
                None,
                "Metadata",
                "Capital Value Investor Factor",
                "CVI Factor",
            ),
            cls.EVIC_EUR.value: (
                None,
                "Metadata",
                "Enterprise Value Including Cash",
                "Enterprise Value Including Cash (EUR)",
            ),
            cls.NACE_SECTION_CODE.value: (
                None,
                "Metadata",
                "NACE (Nomenclature of Economic Activities) is the European statistical classification of economic activities.",
                "Nomenclature of Economic Activities (NACE) Code",
            ),
        }


class PeriodType(ChoiceEnum):
    """This enum holds information about the periodicity of the required data"""

    ANNUAL = "annual"
    INTERIM = "interim"
    ALL = "all"


class CalendarType(TextChoices):
    """This enum holds information about the required calendar type"""

    FISCAL = "fiscal"
    CALENDAR = "calendar"


class SeriesType(ChoiceEnum):
    """This enum holds information about the series type"""

    COMPLETE = "complete"
    ACTUAL = "actual"
    ESTIMATE = "estimate"
    FULL_ESTIMATE = "full_estimate"


class DataType(TextChoices):
    """This enum helps to differenciate between reported and standardized data"""

    REPORTED = "reported"
    STANDARDIZED = "standardized"


class EstimateType(ChoiceEnum):
    """This enum helps to differentiate between only valid estimates or all estimates (historic)"""

    ALL = "all"
    VALID = "valid"


class MarketDataChartType(TextChoices):
    CLOSE = ("close", "Close")
    DRAWDOWN = ("drawdown", "Drawdown")
    RETURN = ("ret", "Return")
    LOG_RETURN = ("log-ret", "Log Return")
    CANDLESTICK = ("candlestick", "Candlestick")
    OHLC = ("ohlc", "OHLC")
    # BOLLINGER = ("bollinger", "Bollinger Bands")


class Indicator(TextChoices):
    SMA_50 = ("sma_50", "SMA 50")
    SMA_100 = ("sma_100", "SMA 100")
    SMA_120 = ("sma_120", "SMA 120")
    SMA_200 = ("sma_200", "SMA 200")


class MarketDataSeriesIndicator(ChoiceEnum):
    DRAWDOWN = "drawdown"


class ESGControveryStatus(TextChoices):
    ONGOING = "ONGOING", "Ongoing"
    PARTIALLY_CONCLUDED = "PARTIALLY_CONCLUDED", "Partially Concluded"
    CONCLUDED = "CONCLUDED", "Concluded"


class ESGControverySeverity(TextChoices):
    MINOR = "MINOR", "Minor"
    MODERATE = "MODERATE", "Moderate"
    SEVERE = "SEVERE", "Severe"
    VERY_SEVERE = "VERY_SEVERE", "Very Severe"


class ESGControveryType(TextChoices):
    STRUCTURAL = "STRUCTURAL", "Structural"
    NON_STRUCTURAL = "NON_STRUCTURAL", "Non Structural"


class ESGControveryFlag(TextChoices):
    GREEN = "GREEN", "Green"
    YELLOW = "YELLOW", "Yellow"
    ORANGE = "ORANGE", "Orange"
    RED = "RED", "Red"
    UNKNOWN = "UNKNOWN", "Unknown"
