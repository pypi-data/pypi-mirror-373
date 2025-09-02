from django.contrib import admin

from wbfdm.models import InstrumentRequest


@admin.register(InstrumentRequest)
class InstrumentRequestModelAdmin(admin.ModelAdmin):
    search_fields = (
        "created_instrument__computed_str",
        "requester__comptuted_str",
    )
    raw_id_fields = ["created_instrument", "requester"]
    list_display = (
        "status",
        "requester",
        "handler",
        "notes",
        "created",
        "created_instrument",
    )
    readonly_fields = ["created"]
    fieldsets = (
        (
            "Main Data",
            {
                "fields": (
                    ("status", "created", "created_instrument"),
                    ("requester", "handler"),
                    ("notes",),
                    ("instrument_data",),
                )
            },
        ),
    )
