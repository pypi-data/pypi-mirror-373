from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.db import DEFAULT_DB_ALIAS
from django.apps import apps as global_apps


def initialize_task(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    PeriodicTask.objects.get_or_create(
        task="wbfdm.tasks.update_of_investable_universe_data",
        defaults={
            "name": "FDM: Periodic data update of investable universe",
            "interval": IntervalSchedule.objects.get_or_create(every=3, period=IntervalSchedule.HOURS)[0],
            "crontab": None,
        },
    )
    PeriodicTask.objects.get_or_create(
        task="wbfdm.tasks.synchronize_instruments_as_task",
        defaults={
            "name": "FDM: Synchronize Instrument",
            "interval": IntervalSchedule.objects.get_or_create(every=30, period=IntervalSchedule.MINUTES)[0],
            "crontab": None,
        },
    )
    PeriodicTask.objects.get_or_create(
        task="wbfdm.tasks.synchronize_exchanges_as_task",
        defaults={
            "name": "FDM: Synchronize Exchange",
            "interval": IntervalSchedule.objects.get_or_create(every=30, period=IntervalSchedule.MINUTES)[0],
            "crontab": None,
        },
    )
