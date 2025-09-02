from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.db import DEFAULT_DB_ALIAS
from django.apps import apps as global_apps


def initialize_task(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    PeriodicTask.objects.update_or_create(
        task="wbcore.contrib.authentication.tasks.delete_unregistered_user_account",
        defaults={
            "name": "Authentication: Delete ghost user accounts",
            "interval": IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)[0],
            "crontab": None,
        },
    )
