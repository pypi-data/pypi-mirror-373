from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from ..models import InstrumentMetric


# Register your models here.
class InstrumentMetricGenericInline(GenericTabularInline):
    model = InstrumentMetric

    ordering = ["-date", "key"]
    ct_field = "basket_content_type"
    ct_fk_field = "basket_id"
    raw_id_fields = ["basket_content_type", "instrument", "parent_metric"]

    fields = [
        "date",
        "key",
        "metrics",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("basket_content_type", "instrument")


@admin.register(InstrumentMetric)
class InstrumentMetricModelAdmin(admin.ModelAdmin):
    list_filter = ("key",)
    search_fields = ("instrument__computed_str",)
    list_display = (
        "basket_content_type",
        "basket_id",
        "instrument",
        "date",
        "key",
    )

    autocomplete_fields = [
        "basket_content_type",
        "instrument",
    ]
    ordering = ("-date", "-key")
    raw_id_fields = ["basket_content_type", "instrument", "parent_metric"]
