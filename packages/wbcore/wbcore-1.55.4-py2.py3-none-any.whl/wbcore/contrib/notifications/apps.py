from django.apps import AppConfig
from django.db import DEFAULT_DB_ALIAS
from django.db.models.signals import post_migrate


def notification_type_post_migrate(app_config, using=DEFAULT_DB_ALIAS, **kwargs):
    from django.contrib.contenttypes.models import ContentType

    from wbcore.contrib.notifications.models import NotificationType

    ContentType.objects.clear_cache()
    # For each model in an app, generate all notification types listed in the meta class of each model
    for klass in app_config.get_models():
        # Get the contenttype and set all notification types for this content type to stale
        # All "touched" notification types will be automatically set to stale=False
        contenttype = ContentType.objects.db_manager(using).get_for_model(klass, for_concrete_model=False)  # type: ignore
        NotificationType.objects.db_manager(using).filter(contenttype=contenttype).update(stale=True)

        for code, title, help_text, web, mobile, email, resource_button_label, is_lock in getattr(
            klass._meta, "notification_types", []
        ):
            NotificationType.objects.using(using).update_or_create(
                code=code,
                defaults={
                    "contenttype": contenttype,
                    "title": title,
                    "help_text": help_text,
                    "default_enable_web": web,
                    "default_enable_mobile": mobile,
                    "default_enable_email": email,
                    "resource_button_label": resource_button_label,
                    "stale": False,
                    "is_lock": is_lock,
                },
            )


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "wbcore.contrib.notifications"

    def ready(self):
        post_migrate.connect(notification_type_post_migrate)
