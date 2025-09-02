from configurations import values
from django.db.models import options


class NotificationConfiguration:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("notification_types",)
    NOTIFICATION_BACKEND = values.Value(
        "wbcore.contrib.notifications.backends.firebase.NotificationBackend", environ_prefix=None
    )
