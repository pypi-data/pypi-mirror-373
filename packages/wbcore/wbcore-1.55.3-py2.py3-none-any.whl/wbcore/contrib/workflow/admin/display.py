from django.contrib import admin

from wbcore.contrib.workflow.models import Display


@admin.register(Display)
class DisplayAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "grid_template_areas")
