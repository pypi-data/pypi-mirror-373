from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .management import create_wbcore_permissions


class WBCoreConfig(AppConfig):
    name = "wbcore"

    def ready(self):
        """
        We load received after all apps are ready in order to be able to discover all subclasses
        """
        post_migrate.connect(
            create_wbcore_permissions,
            dispatch_uid="wbcore.management.create_wbcore_permissions",
        )
