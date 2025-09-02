from django.contrib import admin

from .models import Tag, TagGroup


@admin.register(Tag)
class TagModelAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "color", "content_type")
    search_fields = ("title", "slug")
    readonly_fields = ("managed",)


@admin.register(TagGroup)
class TagGroupModelAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    readonly_fields = ("managed",)
