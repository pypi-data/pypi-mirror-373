from django.apps import AppConfig
from django.db.models.signals import post_migrate


class WbmailingConfig(AppConfig):
    name = "wbmailing"

    def ready(self) -> None:
        from wbmailing.management import initialize_task

        post_migrate.connect(
            initialize_task,
            dispatch_uid="wbmailing.initialize_task",
        )
