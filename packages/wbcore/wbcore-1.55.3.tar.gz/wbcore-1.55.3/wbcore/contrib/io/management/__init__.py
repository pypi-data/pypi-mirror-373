from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.db import DEFAULT_DB_ALIAS
from django.apps import apps as global_apps
from django.conf import settings

from wbcore.contrib.io.models import Source


def load_sources_from_settings(
    app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs
):
    if module_settings := getattr(settings, "DEFAULT_REGISTERED_DATA_BACKEND", None):
        Source.load_sources_from_settings(module_settings)
