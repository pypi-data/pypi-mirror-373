from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class MetricConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wbfdm.contrib.metric"

    def ready(self) -> None:
        autodiscover_modules("metric.backends")
