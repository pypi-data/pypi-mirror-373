from datetime import datetime
from typing import List

from django.core.exceptions import ValidationError
from django.db import models
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler

from wbfdm.import_export.handlers.instrument import InstrumentImportHandler

MAX_NB_DATES_BEFORE_HISTORICAL_IMPORT = 3


class InstrumentPriceImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbfdm.InstrumentPrice"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)
        self.updated_instruments = set()

    def _deserialize(self, data):
        if data.get("instrument", None) is None or data.get("date", None) is None:
            raise DeserializationError("Instrument or Date is empty")
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()

        instrument = self.instrument_handler.process_object(data["instrument"], only_security=False, read_only=True)[0]
        if not instrument:
            raise DeserializationError("Instrument couldn't be found with given data")
        self.updated_instruments.add(instrument)
        data["instrument"] = instrument
        if data.get("net_value", None) is None:
            # casted_instrument = instrument.get_casted_instrument()
            # # we try to find the primary field among the data to set the net value from it
            # if primary_field_value := data.pop(casted_instrument.primary_field, None):
            #     data["net_value"] = primary_field_value
            # # in a last case, we try to find the close value and set it as the net value
            if close := data.pop("close", None):
                data["net_value"] = close
        else:
            if data.get("gross_value", None) is None:
                data["gross_value"] = data["net_value"]

        # Backward compatibility with refinitiv parser.
        for forbbiden_field in ["close", "price_index", "yield_redemption", "net_return", "offered_rate"]:
            data.pop(forbbiden_field, None)

        # We do this to ensure an invalid number won't make the import fails
        for k, v in data.items():
            if v and (field := self.model._meta.get_field(k)) and hasattr(field, "max_digits"):
                try:
                    field.clean(value=str(round(v, field.decimal_places)), model_instance=None)
                except ValidationError:
                    data[k] = None

        if data.get("net_value", None) is None:
            raise DeserializationError("Net value not set.")

    def _get_instance(self, data, history=None, **kwargs):
        self.import_source.log += f"\nParameter: Instrument={data['instrument']} Date={data['date']}"
        price = data["instrument"].prices.filter(date=data["date"], calculated=False)
        if price.exists():
            return price.first()

    def _save_object(self, _object, **kwargs):
        _object.compute_and_update_statistics()  # compute beta, correlation, sharpe and annualized daily volatility everytime object changes
        return super()._save_object(_object, **kwargs)

    def _post_processing_objects(
        self,
        created_objs: List[models.Model],
        modified_objs: List[models.Model],
        unmodified_objs: List[models.Model],
    ):
        for instrument in self.updated_instruments:
            instrument.update_last_valuation_date()
