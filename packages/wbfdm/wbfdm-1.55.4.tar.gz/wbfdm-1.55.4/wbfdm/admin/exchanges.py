from django import forms
from django.contrib import admin

from wbfdm.models import Exchange


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(Exchange)
class ExchangeModelAdmin(admin.ModelAdmin):
    list_display = (
        "source_id",
        "name",
        "mic_code",
        "operating_mic_code",
        "bbg_exchange_codes",
        "bbg_composite",
        "country",
    )
    search_fields = (
        "name",
        "operating_mic_code",
        "mic_code",
        "bbg_exchange_codes",
        "bbg_composite",
        "refinitiv_identifier_code",
        "comments",
    )
    list_filter = ["country"]
    fieldsets = (
        (
            "Main Data",
            {
                "fields": (
                    (
                        "name",
                        "opening_time",
                        "closing_time",
                    ),
                    ("mic_code", "mic_name"),
                    ("operating_mic_code", "operating_mic_name"),
                    ("bbg_exchange_codes", "bbg_composite_primary", "bbg_composite"),
                    ("refinitiv_identifier_code", "refinitiv_mnemonic"),
                    ("country", "website", "apply_round_lot_size"),
                    ("comments",),
                )
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("country")
