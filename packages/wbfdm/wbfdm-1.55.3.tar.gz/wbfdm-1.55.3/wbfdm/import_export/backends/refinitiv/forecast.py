from datetime import datetime
from io import BytesIO
from typing import Optional

from django.db import models
from pandas.tseries.offsets import BDay
from wbcore.contrib.io.backends import AbstractDataBackend, register

from .mixin import DataBackendMixin
from .utils import Controller

DEFAULT_MAPPING = {
    "SAL1MN": "revenue_y1",
    "SAL2MN": "revenue_y2",
    "SAL3MN": "revenue_y3",
    "SAL4MN": "revenue_y4",
    "SAL5MN": "revenue_y5",
    "GRM1MN": "gross_profit_margin_without_depreciation_y1",
    "GRM2MN": "gross_profit_margin_without_depreciation_y2",
    "GRM3MN": "gross_profit_margin_without_depreciation_y3",
    "GRM4MN": "gross_profit_margin_without_depreciation_y4",
    "GRM5MN": "gross_profit_margin_without_depreciation_y5",
    "NER1MN": "reported_net_profit_y1",
    "NER2MN": "reported_net_profit_y2",
    "NER3MN": "reported_net_profit_y3",
    "NER4MN": "reported_net_profit_y4",
    "NER5MN": "reported_net_profit_y5",
    "INC1MN": "adjusted_net_profit_y1",
    "INC2MN": "adjusted_net_profit_y2",
    "INC3MN": "adjusted_net_profit_y3",
    "INC4MN": "adjusted_net_profit_y4",
    "INC5MN": "adjusted_net_profit_y5",
    "EBD1MN": "ebitda_y1",
    "EBD2MN": "ebitda_y2",
    "EBD3MN": "ebitda_y3",
    "EBD4MN": "ebitda_y4",
    "EBD5MN": "ebitda_y5",
    "EBT1MN": "ebit_y1",
    "EBT2MN": "ebit_y2",
    "EBT3MN": "ebit_y3",
    "EBT4MN": "ebit_y4",
    "EBT5MN": "ebit_y5",
    "NDT1MN": "net_debt_y1",
    "NDT2MN": "net_debt_y2",
    "NDT3MN": "net_debt_y3",
    "NDT4MN": "net_debt_y4",
    "NDT5MN": "net_debt_y5",
    "EVT1MN": "entreprise_value_y1",
    "EVT2MN": "entreprise_value_y2",
    "EVT3MN": "entreprise_value_y3",
    "EVT4MN": "entreprise_value_y4",
    "EVT5MN": "entreprise_value_y5",
    "FCF1MN": "free_cash_flow_y1",
    "FCF2MN": "free_cash_flow_y2",
    "FCF3MN": "free_cash_flow_y3",
    "FCF4MN": "free_cash_flow_y4",
    "FCF5MN": "free_cash_flow_y5",
    "EPS1MN": "eps_y1",
    "EPS2MN": "eps_y2",
    "EPS3MN": "eps_y3",
    "EPS4MN": "eps_y4",
    "EPS5MN": "eps_y5",
    "CAP1MN": "capital_expenditures_y1",
    "CAP2MN": "capital_expenditures_y2",
    "CAP3MN": "capital_expenditures_y3",
    "CAP4MN": "capital_expenditures_y4",
    "CAP5MN": "capital_expenditures_y5",
    "BPS1MN": "expected_book_value_per_share_y1",
    "BPS2MN": "expected_book_value_per_share_y2",
    "BPS3MN": "expected_book_value_per_share_y3",
    "BPS4MN": "expected_book_value_per_share_y4",
    "BPS5MN": "expected_book_value_per_share_y5",
}

PER_SHARE_FIELDS = [
    "EPS1MN",
    "EPS2MN",
    "EPS3MN",
    "EPS4MN",
    "EPS5MN",
    "BPS1MN",
    "BPS2MN",
    "BPS3MN",
    "BPS4MN",
    "BPS5MN",
    "FCF1MN",
    "FCF2MN",
    "FCF3MN",
    "FCF4MN",
    "FCF5MN",
    "GRM1MN",
    "GRM2MN",
    "GRM3MN",
    "GRM4MN",
    "GRM5MN",
]


CURRENCY_BASED_FIELDS = [
    "SAL1MN",
    "SAL2MN",
    "SAL3MN",
    "SAL4MN",
    "SAL5MN",
    "NER1MN",
    "NER2MN",
    "NER3MN",
    "NER4MN",
    "NER5MN",
    "INC1MN",
    "INC2MN",
    "INC3MN",
    "INC4MN",
    "INC5MN",
    "EBD1MN",
    "EBD2MN",
    "EBD3MN",
    "EBD4MN",
    "EBD5MN",
    "EBT1MN",
    "EBT2MN",
    "EBT3MN",
    "EBT4MN",
    "EBT5MN",
    "NDT1MN",
    "NDT2MN",
    "NDT3MN",
    "NDT4MN",
    "NDT5MN",
    "EVT1MN",
    "EVT2MN",
    "EVT3MN",
    "EVT4MN",
    "EVT5MN",
    "CAP1MN",
    "CAP2MN",
    "CAP3MN",
    "CAP4MN",
    "CAP5MN",
    "FCF1MN",
    "FCF2MN",
    "FCF3MN",
    "FCF4MN",
    "FCF5MN",
]


@register("Forecast", provider_key="refinitiv", save_data_in_import_source=False, passive_only=False)
class DataBackend(DataBackendMixin, AbstractDataBackend):
    def __init__(self, import_credential: Optional[models.Model] = None, **kwargs):
        self.controller = Controller(import_credential.username, import_credential.password)

    def get_files(
        self,
        execution_time: datetime,
        obj_external_ids: list[str] = None,
        **kwargs,
    ) -> BytesIO:
        execution_date = execution_time.date()
        start = kwargs.get("start", (execution_date - BDay(1)).date())

        fields = list(DEFAULT_MAPPING.keys())
        if obj_external_ids:
            df = self.controller.get_data(
                obj_external_ids,
                fields,
                start,
                execution_date,
                ibes_non_per_share_fields=list(filter(lambda x: x not in PER_SHARE_FIELDS, fields)),
                ibes_currency_based_fields=CURRENCY_BASED_FIELDS,
            )
            if not df.empty:
                content_file = BytesIO()
                df.to_json(content_file, orient="records")
                file_name = (
                    f"forecast_{start:%Y-%m-%d}-{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
                )
                yield file_name, content_file
