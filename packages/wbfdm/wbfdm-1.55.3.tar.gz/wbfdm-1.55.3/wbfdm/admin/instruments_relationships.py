from django.contrib import admin

from wbfdm.models import (
    InstrumentClassificationThroughModel,
    InstrumentFavoriteGroup,
    RelatedInstrumentThroughModel,
)


@admin.register(InstrumentFavoriteGroup)
class InstrumentFavoriteGroupModelAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "public", "primary")
    autocomplete_fields = ["instruments", "owner"]


class InstrumentClassificationThroughModelAdmin(admin.TabularInline):
    list_display = ("classification", "is_favorite")
    model = InstrumentClassificationThroughModel
    fk_name = "instrument"
    autocomplete_fields = ["classification"]


class RelatedInstrumentThroughModelInlineAdmin(admin.TabularInline):
    model = RelatedInstrumentThroughModel
    fk_name = "instrument"
    autocomplete_fields = ["related_instrument"]
