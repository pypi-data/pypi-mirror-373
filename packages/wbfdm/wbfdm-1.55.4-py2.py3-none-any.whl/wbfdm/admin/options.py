from django.contrib import admin

from wbfdm.models import Option, OptionAggregate


@admin.register(OptionAggregate)
class OptionAggregateModelAdmin(admin.ModelAdmin):
    list_display = ("type", "instrument", "date")

    ordering = ("-date",)

    autocomplete_fields = ["instrument"]
    fieldsets = (
        (
            "Main Data",
            {"fields": (("type", "instrument", "date", "import_source"),)},
        ),
        (
            "Base Metrics",
            {
                "fields": (
                    (
                        "volume",
                        "volume_5d",
                        "volume_10d",
                        "volume_20d",
                        "volume_50d",
                    ),
                    (
                        "open_interest",
                        "open_interest_5d",
                        "open_interest_10d",
                        "open_interest_20d",
                        "open_interest_50d",
                    ),
                    ("volatility", "volatility_30d", "volatility_60d", "volatility_90d"),
                )
            },
        ),
    )

    raw_id_fields = ["import_source", "instrument"]


@admin.register(Option)
class OptionModelAdmin(admin.ModelAdmin):
    list_display = ("type", "contract_identifier", "instrument", "date", "expiration_date", "strike")

    ordering = ("-date",)

    autocomplete_fields = ["instrument"]
    fieldsets = (
        (
            "Main Data",
            {
                "fields": (
                    (
                        "type",
                        "instrument",
                        "contract_identifier",
                        "strike",
                    ),
                    ("date", "expiration_date", "import_source"),
                )
            },
        ),
        (
            "EOD",
            {
                "fields": (
                    (
                        "open",
                        "high",
                        "low",
                    ),
                    ("close", "bid", "ask"),
                )
            },
        ),
        (
            "Base Metrics",
            {
                "fields": (
                    ("volume", "open_interest"),
                    ("volatility_30d", "volatility_60d", "volatility_90d"),
                )
            },
        ),
        (
            "Risk Metrics",
            {
                "fields": (
                    ("risk_delta", "risk_theta", "risk_gamma"),
                    ("risk_vega", "risk_rho", "risk_lambda"),
                    ("risk_epsilon", "risk_vomma", "risk_vera"),
                    ("risk_speed", "risk_zomma", "risk_color", "risk_ultima"),
                )
            },
        ),
    )

    raw_id_fields = ["import_source", "instrument"]
