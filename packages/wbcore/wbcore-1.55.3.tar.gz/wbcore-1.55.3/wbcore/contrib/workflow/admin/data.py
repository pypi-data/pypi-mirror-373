from django.contrib import admin

from wbcore.contrib.workflow.models import Data, DataValue


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    search_fields = ("label",)
    list_display = ("id", "label", "data_type", "workflow", "help_text", "required", "default")


@admin.register(DataValue)
class DataValueAdmin(admin.ModelAdmin):
    search_fields = ("value",)
    list_display = ("id", "value", "data")
