from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate


class WbhumanResourcesConfig(AppConfig):
    name = "wbhuman_resources"

    def ready(self) -> None:
        from wbcore.signals.filters import add_filters

        from wbhuman_resources.management import initialize_task

        from .filters.signals import add_position_filter

        if apps.is_installed("wbcrm"):
            from wbcrm.filters import ActivityFilter

            add_filters.connect(add_position_filter, sender=ActivityFilter)

        post_migrate.connect(
            initialize_task,
            dispatch_uid="wbhuman_resources.initialize_task",
        )
