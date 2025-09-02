from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Geography


@admin.register(Geography)
class GeographyAdmin(MPTTModelAdmin):
    search_fields = ("name", "code_2", "code_3")
    list_display = ("name", "code_2", "code_3", "parent")
    raw_id_fields = ["parent"]
    readonly_fields = ["level"]
    fieldsets = (
        (
            "Main information",
            {
                "fields": (
                    ("name", "short_name", "alternative_names", "representation"),
                    ("code_2", "code_3", "code"),
                    ("population", "ranking", "time_zone"),
                    (
                        "parent",
                        "level",
                    ),
                    ("search_vector",),
                )
            },
        ),
    )
    list_filter = ("level",)
