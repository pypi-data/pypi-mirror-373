from contextlib import suppress
from datetime import datetime
from typing import Any, Dict, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler

from .instrument import InstrumentImportHandler


class OptionAggregateImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbfdm.OptionAggregate"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)

    def _deserialize(self, data):
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()
        instrument = self.instrument_handler.process_object(data["instrument"], read_only=True)[0]
        if not instrument:
            raise DeserializationError("Instrument couldn't be found with given data")
        data["instrument"] = instrument

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        with suppress(ObjectDoesNotExist):
            return self.model.objects.get(instrument=data["instrument"], date=data["date"], type=data["type"])


class OptionImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbfdm.Option"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)

    def _deserialize(self, data):
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()
        data["expiration_date"] = datetime.strptime(data["expiration_date"], "%Y-%m-%d").date()
        instrument = self.instrument_handler.process_object(data["instrument"], read_only=True)[0]
        if not instrument:
            raise DeserializationError("Instrument couldn't be found with given data")
        data["instrument"] = instrument

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        with suppress(ObjectDoesNotExist):
            return self.model.objects.get(
                instrument=data["instrument"],
                contract_identifier=data["contract_identifier"],
                date=data["date"],
                type=data["type"],
            )
