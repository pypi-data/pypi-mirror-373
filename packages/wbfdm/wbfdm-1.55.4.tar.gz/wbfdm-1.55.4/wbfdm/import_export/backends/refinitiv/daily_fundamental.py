from datetime import datetime
from io import BytesIO
from typing import Optional

from django.db import models
from pandas.tseries.offsets import BDay
from wbcore.contrib.io.backends import AbstractDataBackend, register

from .mixin import DataBackendMixin
from .utils import Controller

DEFAULT_MAPPING = {"DWFC": "free_cash", "EPS": "eps_ttm", "EPS1FD12": "eps_ftw"}


@register("Daily Fundamental", provider_key="refinitiv", save_data_in_import_source=False, passive_only=False)
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
            df = self.controller.get_data(obj_external_ids, fields, start, execution_date)
            if not df.empty:
                content_file = BytesIO()
                df.to_json(content_file, orient="records")
                file_name = f"daily_fundamental_{start:%Y-%m-%d}-{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
                yield file_name, content_file
