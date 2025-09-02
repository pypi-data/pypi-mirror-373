from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import models

from .imports import ImportExportHandler
from .models import Source


class ImportMixin(models.Model):
    import_export_handler_class: type[ImportExportHandler] | None = None
    import_source = models.ForeignKey(
        "io.ImportSource",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @classmethod
    def import_data(cls, execution_time: datetime | None = None, synchronous: bool = False, **kwargs):
        """
        Allow Resource to trigger the workflow from the instance
        Args:
            execution_time: The time at which the task needs to be trigger
            **kwargs: keyword arguments passed down the workflow
        """
        content_type = ContentType.objects.get_for_model(cls)
        model_name = f"{content_type.app_label}.{content_type.model}"
        for source in Source.objects.filter(
            parser_handler__handler__iexact=model_name, data_backend__passive_only=False, is_active=True
        ):
            source.trigger_workflow(
                execution_time=execution_time, synchronous=synchronous, only_handler=model_name, **kwargs
            )

    class Meta:
        abstract = True
