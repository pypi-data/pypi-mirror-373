from django.contrib import admin

from wbfdm.admin.instruments import InstrumentModelAdmin as BaseInstrumentModelAdmin
from wbfdm.models.instruments import Instrument

from .metrics import InstrumentMetricGenericInline

admin.site.unregister(Instrument)


@admin.register(Instrument)
class InstrumentModelAdmin(BaseInstrumentModelAdmin):
    inlines = (*BaseInstrumentModelAdmin.inlines, InstrumentMetricGenericInline)
