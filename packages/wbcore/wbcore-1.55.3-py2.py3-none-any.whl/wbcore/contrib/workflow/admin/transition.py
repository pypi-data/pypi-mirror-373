from django.contrib import admin

from wbcore.contrib.workflow.models import Transition


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "from_step", "to_step", "icon")
