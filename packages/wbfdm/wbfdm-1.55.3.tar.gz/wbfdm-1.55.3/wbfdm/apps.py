from django.apps import AppConfig
from django.db.models.signals import post_migrate


class WBFDMAppConfig(AppConfig):
    name = "wbfdm"

    def ready(self):
        from wbfdm.management import initialize_task

        post_migrate.connect(
            initialize_task,
            dispatch_uid="wbfdm.initialize_task",
        )
