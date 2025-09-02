from django.contrib import admin

from wbfdm.models import Instrument, InstrumentType
from wbfdm.models.instruments.instruments import import_prices_as_task

from .instruments_relationships import (
    InstrumentClassificationThroughModelAdmin,
    RelatedInstrumentThroughModelInlineAdmin,
)


class InstrumentInline(admin.TabularInline):
    verbose_name = "Child"
    verbose_names = "Children"
    model = Instrument
    fields = ("name", "exchange", "is_investable_universe", "is_security", "is_primary")
    autocomplete_fields = ("exchange",)
    show_change_link = True
    extra = 0


@admin.register(InstrumentType)
class InstrumentTypeModelAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "is_security", "is_classifiable")


@admin.register(Instrument)
class InstrumentModelAdmin(admin.ModelAdmin):
    list_display = (
        "_is_investable",
        "is_investable_universe",
        "is_security",
        "is_primary",
        "instrument_type",
        "name",
        "source",
        "source_id",
        "exchange",
        "ticker",
        "refinitiv_identifier_code",
        "refinitiv_mnemonic_code",
        "isin",
        "currency",
        "country",
    )
    list_filter = ["instrument_type", "is_investable_universe", "is_security", "is_managed", "is_primary"]
    fieldsets = (
        (
            "Instrument Information",
            {
                "fields": (
                    ("name", "name_repr", "computed_str"),
                    ("parent", "instrument_type", "is_primary"),
                    ("is_cash", "is_security", "is_managed", "is_cash_equivalent", "is_investable_universe"),
                    ("inception_date", "delisted_date"),
                    ("primary_url", "additional_urls"),
                    (
                        "ticker",
                        "identifier",
                        "refinitiv_identifier_code",
                        "refinitiv_mnemonic_code",
                    ),
                    (
                        "cusip",
                        "sedol",
                        "valoren",
                    ),
                    ("isin", "old_isins", "tags"),
                    ("currency", "country", "headquarter_city", "headquarter_address"),
                    (
                        "exchange",
                        "round_lot_size",
                        "import_source",
                        "base_color",
                    ),
                    ("description",),
                    ("dl_parameters", "source", "source_id"),
                )
            },
        ),
    )
    search_fields = (
        "name",
        "name_repr",
        "isin",
        "ticker",
        "computed_str",
        "refinitiv_identifier_code",
        "refinitiv_mnemonic_code",
        "cusip",
        "sedol",
        "valoren",
        "source_id",
    )

    autocomplete_fields = ["parent", "currency", "country", "headquarter_city", "related_instruments", "tags"]
    readonly_fields = ["computed_str", "last_update", "last_valuation_date"]
    inlines = [InstrumentInline, RelatedInstrumentThroughModelInlineAdmin, InstrumentClassificationThroughModelAdmin]
    raw_id_fields = [
        "import_source",
    ]

    actions = ["reimport_prices_since_inception"]

    def reimport_prices_since_inception(self, request, queryset):
        for instrument in queryset:
            for investable_children in instrument.get_descendants(include_self=True).filter(
                is_investable_universe=True
            ):  # trigger the recomputation for all children within the investable universe
                import_prices_as_task.delay(investable_children.id, clear=True)

    def isin(self, obj):
        return obj.isin

    def ric(self, obj):
        return obj.ric

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("currency", "country", "instrument_type")
