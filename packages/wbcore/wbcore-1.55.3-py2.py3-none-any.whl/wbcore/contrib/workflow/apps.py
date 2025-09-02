from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.module_loading import autodiscover_modules

from wbcore.signals import add_dynamic_button


class WorkflowConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wbcore.contrib.workflow"

    def ready(self):
        autodiscover_modules("workflows")
        from wbcore.contrib.workflow.dispatch import check_workflow_for_instance
        from wbcore.contrib.workflow.serializers.signals import (
            add_workflow_next_buttons_to_instance,
        )
        from wbcore.contrib.workflow.sites import workflow_site

        for model_class in (
            workflow_site.registered_model_classes_serializer_map.keys()
        ):  # we don't use items because the map is a custom cachedictionary where
            serializer_class = workflow_site.registered_model_classes_serializer_map[model_class]
            post_save.connect(check_workflow_for_instance, sender=model_class, weak=False)
            add_dynamic_button.connect(add_workflow_next_buttons_to_instance, sender=serializer_class)
