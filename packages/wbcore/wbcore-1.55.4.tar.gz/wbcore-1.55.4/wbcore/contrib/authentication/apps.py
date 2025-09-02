from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AuthenticationConfig(AppConfig):
    name = "wbcore.contrib.authentication"

    def ready(self):
        from wbcore.contrib.authentication.management import initialize_task

        post_migrate.connect(
            initialize_task,
            dispatch_uid="wbcore.contrib.authentication.initialize_task",
        )
