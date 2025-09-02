from datetime import datetime
from io import BytesIO
from typing import Optional

import pandas as pd
from django.db import models
from pandas.tseries.offsets import YearEnd
from wbcore.contrib.io.backends import AbstractDataBackend, register

from .mixin import DataBackendMixin
from .utils import Controller

DEFAULT_MAPPING = {
    "IBEFPD": "period_type",  # Expected
    "IBQ1EEDT": "period_end_date",  # Expected Q1
    "IBQ1ERDT": "expected_report_date",  # Expected Q1
    "IBQ2EEDT": "period_end_date",  # Expected Q2
    "IBQ2ERDT": "expected_report_date",  # Expected Q2
    "IBFPD": "period_type",  # Company/Actual
    "IBQ1ENDT": "period_end_date",  # Company/Actual Q1
    "IBQ1CRDT": "expected_report_date",  # Company/Actual Q1
    "IBQ2ENDT": "period_end_date",  # Company/Actual Q2
    "IBQ2CRDT": "expected_report_date",  # Company/Actual Q1
}


@register("Fiscal Period", provider_key="refinitiv", save_data_in_import_source=False, passive_only=False)
class DataBackend(DataBackendMixin, AbstractDataBackend):
    CHUNK_SIZE = 20

    def __init__(self, import_credential: Optional[models.Model] = None, **kwargs):
        self.controller = Controller(import_credential.username, import_credential.password)

    def get_files(
        self,
        execution_time: datetime,
        obj_external_ids: list[str] = None,
        **kwargs,
    ) -> BytesIO:
        execution_date = execution_time.date()
        if obj_external_ids:
            df = self.controller.get_data(obj_external_ids, list(DEFAULT_MAPPING.keys()))
            if not df.empty:
                df_last_year_end = self.controller.get_data(
                    obj_external_ids,
                    ["WC05350", "WC05351"],
                    start=(execution_date - YearEnd(1)).date(),
                    end=(execution_date + YearEnd(0)).date(),
                    freq="Y",
                )
                # We do this to gather the last fiscal year end date to forward to the parser in order for figuring out what is the actual period index
                if not df_last_year_end.empty:
                    df_last_year_end = df_last_year_end.sort_values(by="WC05350").groupby(["Instrument"]).last()
                    df = pd.concat(
                        [df.set_index("Instrument"), df_last_year_end[df_last_year_end.columns.difference(["Dates"])]],
                        axis=1,
                    ).reset_index(names="Instrument")
                df = df.dropna(how="all", subset=df.columns.difference(["Instrument", "Dates"]))
                if not df.empty:
                    content_file = BytesIO()
                    df.to_json(content_file, orient="records")
                    file_name = f"fiscal_periods_{datetime.timestamp(execution_time)}.json"
                    yield file_name, content_file
