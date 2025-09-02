from django.contrib import admin

from wbfdm.models import Controversy


@admin.register(Controversy)
class ControversyModelAdmin(admin.ModelAdmin):
    search_fields = (
        "headline",
        "description",
        "source",
    )
    raw_id_fields = ["instrument"]
    list_display = (
        "initiated",
        "review",
        "headline",
        "description",
        "source",
        "status",
        "type",
        "severity",
        "company_response",
    )
