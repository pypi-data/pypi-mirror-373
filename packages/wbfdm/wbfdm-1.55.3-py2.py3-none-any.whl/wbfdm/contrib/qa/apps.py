from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Warning, register


@register()
def check_qa_db_available(app_configs, **kwargs):
    warnings = []

    if "qa" not in settings.DATABASES:
        warnings.append(
            Warning(
                "A database with the name qa needs to be installed in order to run QA",
            )
        )

    return warnings


class QAAppConfig(AppConfig):
    name = "wbfdm.contrib.qa"
    verbose_name = "Quantitative Analytics (QA)"
