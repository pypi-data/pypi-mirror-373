from django.contrib import admin

from wbfdm.models import InstrumentList, InstrumentListThroughModel


class InstrumentInstrumentList(admin.TabularInline):
    model = InstrumentListThroughModel
    fk_name = "instrument_list"
    fields = ["instrument_str", "instrument", "validated", "from_date", "to_date"]

    raw_id_fields = ["instrument", "instrument_list"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("instrument")


@admin.register(InstrumentList)
class InstrumentListAdmin(admin.ModelAdmin):
    search_fields = ("name", "instrument_list_type")
    list_display = ("name", "instrument_list_type")

    inlines = [
        InstrumentInstrumentList,
    ]
