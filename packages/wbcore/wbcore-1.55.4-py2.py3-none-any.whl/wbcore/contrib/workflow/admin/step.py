from django.contrib import admin

from wbcore.contrib.workflow.models import (
    DecisionStep,
    EmailStep,
    FinishStep,
    JoinStep,
    ScriptStep,
    SplitStep,
    StartStep,
    UserStep,
)

STEP_BASE_FIELDS = (
    "id",
    "name",
    "workflow",
    "status",
    "code",
    "permission",
)


@admin.register(StartStep)
class StartStepAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = STEP_BASE_FIELDS


@admin.register(SplitStep)
class SplitStepAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = STEP_BASE_FIELDS


@admin.register(UserStep)
class UserStepAdmin(admin.ModelAdmin):
    search_fields = ("name", "assignee", "group")
    list_display = (
        "assignee",
        "group",
        "assignee_method",
        "notify_user",
        "display",
        "kwargs",
    ) + STEP_BASE_FIELDS


@admin.register(DecisionStep)
class DecisionStepAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = STEP_BASE_FIELDS


@admin.register(JoinStep)
class JoinStepAdmin(admin.ModelAdmin):
    search_fields = ("name", "wait_for_all")
    list_display = ("wait_for_all",) + STEP_BASE_FIELDS


@admin.register(ScriptStep)
class ScriptStepAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("script",) + STEP_BASE_FIELDS


@admin.register(EmailStep)
class EmailStepAdmin(admin.ModelAdmin):
    search_fields = (
        "to",
        "subject",
        "name",
    )
    list_display = ("subject", "template") + STEP_BASE_FIELDS
    fields = (
        "to",
        "subject",
        "name",
        "template",
        "cc",
        "bcc",
        "workflow",
        "status",
        "code",
        "permission",
    )


@admin.register(FinishStep)
class FinishStepAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("write_preserved_instance",) + STEP_BASE_FIELDS
