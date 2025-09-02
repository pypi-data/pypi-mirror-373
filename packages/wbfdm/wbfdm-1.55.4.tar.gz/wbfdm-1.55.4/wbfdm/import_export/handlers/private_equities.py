from datetime import datetime
from typing import Any, Dict, Optional

from django.db import models
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler

from .instrument import InstrumentImportHandler


class DealImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbfdm.Deal"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)

    def _deserialize(self, data):
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()
        equity = self.instrument_handler.process_object(
            {**data["equity"], "instrument_type": "private_equity"}, read_only=True
        )[0]
        if not equity:
            raise DeserializationError("Private Equity couldn't be found with given data")
        data["equity"] = equity

        if investors := data.pop("investors", []):
            data["investors"] = [
                self.instrument_handler.process_object(investor_data, read_only=True)[0] for investor_data in investors
            ]

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        if external_id := data.get("external_id", None):
            return self.model.objects.filter(external_id=external_id).first()
        qs = self.model.objects.filter(
            equity=data["equity"], date=data["date"], transaction_amount=data["transaction_amount"]
        )
        if qs.count() == 1:
            return qs.first()

    def _create_instance(self, data: Dict[str, Any], **kwargs) -> models.Model:
        investors = data.pop("investors", None)
        obj = self.model.objects.create(
            **data,
            import_source=self.import_source,
        )
        if investors:
            obj.investors.set([i for i in investors if i])
        return obj
