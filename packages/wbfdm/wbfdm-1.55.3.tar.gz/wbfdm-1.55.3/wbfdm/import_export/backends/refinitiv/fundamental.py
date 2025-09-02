from datetime import datetime
from io import BytesIO
from typing import List, Optional

import pandas as pd
from django.db import models
from wbcore.contrib.io.backends import AbstractDataBackend, register

from .mixin import DataBackendMixin
from .utils import Controller

DEFAULT_MAPPING = {
    # Income Statement
    "WC01001": "revenue",
    "WC01051": "cost_of_good_sold_without_depreciation",
    "WC18198": "ebitda",
    "WC18191": "ebit",
    "WC01651": "net_profit",
    "WC08346": "company_tax_rate",
    "WC01201": "cost_research_development",
    "WC01251": "interest_expense",
    "WC01101": "sga",
    # Balance Sheet
    "WC03501": "shareholder_equity",
    "WC02999": "total_assets",
    "WC03101": "current_liabilities",
    "WC03351": "total_liabilities",
    "WC03255": "total_debt",
    "WC02003": "cash_and_cash_equivalents",
    "WC02005": "cash_and_short_term_investments",
    "WC18199": "net_debt",
    "WC02051": "receivables",
    "WC02101": "inventories",
    "WC03040": "payables",
    "WC02201": "current_assets",
    "WC07011": "employee_count",
    "WC18100": "entreprise_value",
    "WC03151": "working_capital",
    "WC05491": "book_value_per_share",
    "WC10010": "eps",
    "WC10030": "diluted_eps",
    "WC01151": "deprecation_and_amortization",
    # Annual data
    "WC04870": "investment_cash",
    "WC04860": "cash_from_operation",
    "WC04890": "financing_cash",
    "WC04601": "capital_expenditures",
    "WC05350": "period__period_end_date",
    "WC05200": "period__period_type",
    # 'WC19109': "net_profit",
    # 'WC19110': "net_profit",
    # 'WC19111': "net_profit",
    # 'WC19112': "net_profit",
}

ANNUAL_FIELDS = ["WC04870", "WC04890", "WC04860", "WC04601"]


@register("Fundamental", provider_key="refinitiv", save_data_in_import_source=False, passive_only=False)
class DataBackend(DataBackendMixin, AbstractDataBackend):
    CHUNK_SIZE = 10
    FISCAL_INTERVAL = 1

    def __init__(self, import_credential: Optional[models.Model] = None, **kwargs):
        self.controller = Controller(import_credential.username, import_credential.password)

    def get_files(
        self,
        execution_time: datetime,
        obj_external_ids: list[str] = None,
        fields: List[str] = None,
        **kwargs,
    ) -> BytesIO:
        execution_date = execution_time.date()

        if not fields:
            fields = list(DEFAULT_MAPPING.keys())
        if obj_external_ids:
            df_interim = self.controller.get_interim_fundamental_data(
                obj_external_ids,
                fields,
                initial_start=kwargs.get("start", None),
                initial_end=execution_date,
            )
            df_annual = self.controller.get_annual_fundamental_data(
                obj_external_ids,
                fields,
                initial_start=kwargs.get("start", None),
                initial_end=execution_date,
            )
            df = pd.concat([df_interim, df_annual], axis=0)
            df = df.dropna(
                how="all",
                subset=df.columns.difference(["Instrument", "Dates", "period__period_interim", "WC05200", "WC05350"]),
            )
            if not df.empty:
                content_file = BytesIO()
                df.to_json(content_file, orient="records")
                if start := kwargs.get("start", execution_date):
                    file_name = f"fundamental_{start:%Y-%m-%d}_{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
                else:
                    file_name = f"fundamental_{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
                yield file_name, content_file
