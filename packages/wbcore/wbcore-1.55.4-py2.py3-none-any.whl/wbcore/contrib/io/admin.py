from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django_admin_inline_paginator.admin import TabularInlinePaginated

from .models import (
    DataBackend,
    ExportSource,
    ImportCredential,
    ImportedObjectProviderRelationship,
    ImportSource,
    ParserHandler,
    Provider,
    Source,
    import_data_as_task,
)


def reprocess_import_source(modeladmin, request, queryset):
    for import_source in queryset:
        import_data_as_task.delay(import_source.id, force_reimport=True)


def reprocess_source(modeladmin, request, queryset):
    for source in queryset:
        source.trigger_workflow()


class ImportedObjectProviderRelationshipInline(TabularInlinePaginated):
    ordering = ["object_id"]
    model = ImportedObjectProviderRelationship
    extra = 0
    readonly_fields = ("content_type", "object_id")
    raw_id_fields = ["content_type", "provider"]
    per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("content_type", "provider")


class ProviderGenericInline(GenericTabularInline):
    model = ImportedObjectProviderRelationship


@admin.register(ParserHandler)
class ParserHandlerModelAdmin(admin.ModelAdmin):
    list_display = ["parser", "handler"]

    search_fields = ["parser", "handler"]


@admin.register(Provider)
class ProviderModelAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ["title"]
    inlines = [ImportedObjectProviderRelationshipInline]


@admin.register(DataBackend)
class DataBackendModelAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "save_data_in_import_source",
        "backend_class_path",
        "backend_class_name",
        "provider",
    ]
    search_fields = ["title"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("provider")


@admin.register(Source)
class SourceModelAdmin(admin.ModelAdmin):
    list_display = ["uuid", "title", "is_active", "crontab", "data_backend"]
    list_filter = ["data_backend", "is_active"]
    raw_id_fields = ["crontab", "periodic_task"]
    search_fields = ["uuid", "data_backend__title", "data_backend__provider__title", "parser_handler__parser"]
    readonly_fields = ["periodic_task"]

    actions = [reprocess_source]
    autocomplete_fields = ["parser_handler", "data_backend"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("data_backend", "periodic_task", "crontab")
            .prefetch_related("parser_handler", "credentials")
        )


@admin.register(ExportSource)
class ExportSourceModelAdmin(admin.ModelAdmin):
    list_display = ["status", "file", "resource_path", "content_type", "created", "last_updated", "creator"]
    list_filter = ["status", "resource_path", "content_type"]
    autocomplete_fields = ["creator", "content_type"]
    readonly_fields = ("created", "last_updated", "query_str", "query_params")
    fieldsets = (
        (
            "",
            {
                "fields": (
                    ("status", "created", "last_updated"),
                    ("content_type", "format"),
                    ("resource_path", "resource_kwargs"),
                    ("query_str", "query_params"),
                    ("file", "origin", "creator"),
                    ("data",),
                    ("log",),
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("content_type")


@admin.register(ImportSource)
class ImportSourceModelAdmin(admin.ModelAdmin):
    list_display = ["status", "file", "parser_handler", "source", "created", "last_updated"]
    list_filter = ["status", "source", "parser_handler__handler", "parser_handler__parser"]
    autocomplete_fields = ["source", "parser_handler"]
    actions = [reprocess_import_source]
    readonly_fields = ("created", "last_updated")
    fieldsets = (
        (
            "",
            {
                "fields": (
                    ("status", "created", "last_updated"),
                    ("parser_handler", "source", "origin"),
                    ("file", "save_data", "progress_index"),
                    ("creator",),
                    ("resource_kwargs",),
                    ("data",),
                    ("log",),
                    ("errors_log",),
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("source", "parser_handler")


@admin.register(ImportCredential)
class ImportCredentialModelAdmin(admin.ModelAdmin):
    list_display = ["key", "type", "username", "validity_start", "validity_end"]
