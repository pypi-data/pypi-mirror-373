from django.contrib import admin

from wbcore.contrib.workflow.models import Condition


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "transition", "attribute_name", "operator", "negate_operator", "expected_value")
