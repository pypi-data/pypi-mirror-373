from datetime import date

from django.db import models

from wbfdm.models.instruments import Instrument


class DataBackendMixin:
    def is_object_valid(self, obj: models.Model) -> bool:
        return (
            super().is_object_valid(obj)
            and obj.is_active_at_date(date.today())
            and (obj.refinitiv_identifier_code or obj.isin or obj.refinitiv_mnemonic_code)
        )

    def get_default_queryset(self):
        privates_equities = Instrument.objects.filter(instrument_type__key="private_equity")
        return Instrument.objects.exclude(id__in=privates_equities.values("id"))

    def get_provider_id(self, obj: models.Model) -> str:
        if perm_id := self.controller.fetch_perm_id(
            instrument_ric=obj.refinitiv_identifier_code,
            instrument_isin=obj.isin,
            instrument_mnemonic=obj.refinitiv_mnemonic_code,
        ):
            return perm_id
        elif (
            obj.refinitiv_identifier_code
        ):  # We default to the RIC in case permID can't be found because some instrument don't have any
            return obj.refinitiv_identifier_code
