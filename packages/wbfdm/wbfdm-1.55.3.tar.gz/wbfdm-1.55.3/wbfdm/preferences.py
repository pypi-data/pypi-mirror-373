from contextlib import suppress

from django.db.utils import ProgrammingError
from dynamic_preferences.registries import global_preferences_registry


def get_default_classification_group(*args, **kwargs):
    from wbfdm.models.instruments.classifications import ClassificationGroup

    with suppress(RuntimeError, ProgrammingError):
        global_preferences = global_preferences_registry.manager()
        if group_id := global_preferences["wbfdm__default_classification_group"]:
            with suppress(ClassificationGroup.DoesNotExist):
                return ClassificationGroup.objects.get(id=group_id)
        return ClassificationGroup.objects.get_or_create(is_primary=True, defaults={"name": "Default"})[0]


def get_non_ticker_words(*args, **kwargs) -> list[str]:
    global_preferences = global_preferences_registry.manager()
    return global_preferences["wbfdm__non_ticker_words"].split(",")
    return list()
