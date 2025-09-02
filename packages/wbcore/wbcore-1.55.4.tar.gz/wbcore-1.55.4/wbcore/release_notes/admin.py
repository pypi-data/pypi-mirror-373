from django.contrib import admin
from django.utils.html import format_html

from .models import ReleaseNote


@admin.register(ReleaseNote)
class ReleaseNoteModelAdmin(admin.ModelAdmin):
    list_display = (
        "version",
        "release_date",
        "summary",
        "module",
    )
    list_filter = ("module", "release_date")

    fields = (("version", "module", "release_date"), "summary", "rendered_notes")

    @staticmethod
    def rendered_notes(obj):
        return format_html(obj.notes)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
