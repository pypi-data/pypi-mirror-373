from django.apps import AppConfig


class TagsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wbcore.contrib.tags"

    def ready(self):
        import wbcore.contrib.tags.signals  # noqa: F401
