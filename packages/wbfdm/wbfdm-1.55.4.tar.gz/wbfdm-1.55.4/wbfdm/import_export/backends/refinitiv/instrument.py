from datetime import datetime
from io import BytesIO
from typing import Optional

from django.db import models
from wbcore.contrib.io.backends import AbstractDataBackend, register

from .mixin import DataBackendMixin
from .utils import Controller

DEFAULT_MAPPING = {
    "ISOCUR": "currency__key",
    "RIC": "refinitiv_identifier_code",
    "MNEM": "refinitiv_mnemonic_code",
    "ISIN": "isin",
    "GGISO": "country",
    # "NPCUR": "currency__key",
    "BNAM": "borrower",
    "ITYP": "issuer_type",
    "EXCHB": "exchanges",
    "CTYP": "coupon_type",
    "BTYP": "bond_type",
    "WC06092": "description",
    "SEGM": "exchange",
    "NAME": "name",
    "WC05601": "ticker",
    "GDIGC": "gics_classification",
    "TR5": "trbc_classification",
    "TYPE": "instrument_type",
    "WC18272": "inception_date",
    "WC18273": "inception_date",
    "WC07015": "delisted_date",
}


@register("Instrument", provider_key="refinitiv", save_data_in_import_source=False, passive_only=False)
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
        if obj_external_ids:
            df = self.controller.get_data(obj_external_ids, list(DEFAULT_MAPPING.keys()))
            if not df.empty:
                content_file = BytesIO()
                df.to_json(content_file, orient="records")
                file_name = f"instrument_{datetime.timestamp(execution_time)}.json"
                yield file_name, content_file
