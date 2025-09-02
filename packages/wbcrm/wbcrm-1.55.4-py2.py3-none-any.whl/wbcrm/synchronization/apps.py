from django.apps import AppConfig
from django.db.models.signals import post_migrate


class WbSyncConfig(AppConfig):
    name = "wbcrm.synchronization"

    def ready(self) -> None:
        from wbcrm.synchronization.management import initialize_task

        post_migrate.connect(
            initialize_task,
            dispatch_uid="wbcrm.synchronization.initialize_task",
        )
