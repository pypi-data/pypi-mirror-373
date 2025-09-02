import pandas as pd
from django.contrib import admin
from wbcore.admin import ExportCsvMixin, ImportCsvMixin

from wbfdm.models import Instrument, InstrumentPrice


@admin.register(InstrumentPrice)
class InstrumentPriceAdmin(ExportCsvMixin, ImportCsvMixin, admin.ModelAdmin):
    change_list_template = "wbcore/admin/change_list.html"
    # fsm_field = ["status"]
    list_display = ("date", "instrument", "net_value", "gross_value", "calculated")

    ordering = ("-date",)

    autocomplete_fields = ["instrument"]
    fieldsets = (
        (
            "Main Data",
            {
                "fields": (
                    (
                        "instrument",
                        "date",
                        "import_source",
                        "calculated",
                    ),
                    ("net_value", "gross_value"),
                )
            },
        ),
        (
            "Extra Data",
            {
                "fields": (
                    ("volume", "volume_50d", "volume_200d"),
                    ("outstanding_shares", "market_capitalization", "market_capitalization_consolidated"),
                )
            },
        ),
        (
            "Computed fields",
            {
                "fields": (
                    "lock_statistics",
                    ("sharpe_ratio", "correlation", "beta"),
                )
            },
        ),
    )

    raw_id_fields = ["import_source", "instrument"]

    actions = ["export_as_csv"]

    def manipulate_df(self, df):
        df["instrument"] = df["instrument"].apply(lambda x: Instrument.objects.get(id=x))
        df["date"] = pd.to_datetime(df["date"])
        return df

    def process_model(self, model):
        query_params = {"instrument": model["instrument"], "date": model["date"]}
        self.model.objects.update_or_create(**query_params, defaults=model)
