from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from wbfdm.models import Classification, ClassificationGroup


class ClassificationInLine(admin.TabularInline):
    model = Classification
    fields = ["code_aggregated", "name"]
    extra = 0


@admin.register(ClassificationGroup)
class ClassificationGroupAdmin(CompareVersionAdmin):
    list_display = ["name", "max_depth", "is_primary"]

    search_fields = ["name"]
    ordering = ["name"]

    def reversion_register(self, model, **options):
        options = {
            "ignore_duplicates": True,
        }
        super().reversion_register(model, **options)


@admin.register(Classification)
class ClassificationAdmin(CompareVersionAdmin):
    list_display = ["code_aggregated", "name", "level"]

    search_fields = ["code_aggregated", "name"]
    inlines = [ClassificationInLine]
    ordering = ["code_aggregated"]
    list_filter = ("height", "level", "group")

    def reversion_register(self, model, **options):
        options = {
            "ignore_duplicates": True,
        }
        super().reversion_register(model, **options)
