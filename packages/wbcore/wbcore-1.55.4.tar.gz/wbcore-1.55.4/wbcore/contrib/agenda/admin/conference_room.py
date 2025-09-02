from django.contrib import admin

from wbcore.contrib.agenda.models import Building, ConferenceRoom


@admin.register(ConferenceRoom)
class ConferenceRoomModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("building",)
    list_display = ["name", "email", "capacity", "building", "is_videoconference_capable"]
    search_fields = ("name", "email", "building__name")
    raw_id_fields = ["building"]


@admin.register(Building)
class BuildingModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("address",)
    list_display = ["name", "address"]
    search_fields = ("name",)
    raw_id_fields = ["address"]
