from datetime import date

from django.db import models

from wbfdm.models.instruments import Instrument


class DataBackendMixin:
    def is_object_valid(self, obj: models.Model) -> bool:
        return super().is_object_valid(obj) and obj.is_active_at_date(date.today())

    def get_provider_id(self, obj: models.Model) -> str:
        return self.client.fetch_org_id(org_name=obj.name, org_urls=[obj.primary_url, *obj.additional_urls])

    def get_default_queryset(self):
        return Instrument.objects.filter(instrument_type__key="private_equity")
