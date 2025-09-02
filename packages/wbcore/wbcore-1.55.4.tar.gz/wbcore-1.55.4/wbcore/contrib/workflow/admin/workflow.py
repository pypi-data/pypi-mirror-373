from django.contrib import admin

from wbcore.contrib.workflow.models import Workflow


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "single_instance_execution", "model", "status_field", "preserve_instance")
