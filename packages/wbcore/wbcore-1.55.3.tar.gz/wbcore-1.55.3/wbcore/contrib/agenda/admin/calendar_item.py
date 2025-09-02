from django.contrib import admin

from wbcore.contrib.agenda.models import CalendarItem


@admin.register(CalendarItem)
class CalendarItemModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("entities",)
    list_display = ["item_type", "title", "period", "is_active"]
    search_fields = ("entities__computed_str",)
    raw_id_fields = ["entities"]

    def get_queryset(self, request):
        return CalendarItem.all_objects.all()
