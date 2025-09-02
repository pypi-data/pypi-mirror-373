import json
from datetime import date, datetime
from io import BytesIO
from typing import Optional

from django.db import models
from wbcore.contrib.io.backends import AbstractDataBackend, register

from .mixin import DataBackendMixin
from .utils.client import Client

DEFAULT_MAPPING = {}


@register("Deals", provider_key="cbinsights")
class DataBackend(DataBackendMixin, AbstractDataBackend):
    def __init__(self, import_credential: Optional[models.Model] = None, **kwargs):
        self.client = Client(import_credential.username, import_credential.password)
        self.client.connect()
        super().__init__(**kwargs)

    def get_provider_id(self, obj: models.Model) -> str:
        return self.client.fetch_org_id(org_name=obj.name, org_urls=[obj.primary_url, *obj.additional_urls])

    def get_files(
        self,
        execution_time: datetime,
        start: Optional[date] = None,
        obj_external_ids: list[str] = None,
        debug: bool = False,
        **kwargs,
    ) -> BytesIO:
        if obj_external_ids:
            if start:
                res_json = self.client.fetch_deals(
                    obj_external_ids, start=start, end=execution_time.date(), debug=debug
                )
            else:
                res_json = self.client.fetch_deals(obj_external_ids, last_update_time=execution_time, debug=debug)
            if res_json:
                content_file = BytesIO()
                content_file.write(json.dumps(res_json).encode())
                file_name = f"cbinsight_deals_{datetime.timestamp(execution_time)}.json"
                yield file_name, content_file
