from django.contrib import admin

from wbcore.contrib.workflow.models import Process, ProcessStep


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    search_fields = ("id", "workflow")
    list_display = (
        "id",
        "workflow",
        "state",
        "started",
        "finished",
        "instance_id",
        "content_type",
        "instance",
        "preserved_instance",
    )


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    search_fields = ("id", "process", "step")
    list_display = (
        "id",
        "process",
        "step",
        "state",
        "error_message",
        "started",
        "finished",
        "assignee",
        "group",
        "permission",
        "status",
    )
