from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from wbcore.admin import NonrelatedTabularInline
from wbcore.contrib.documents.models import (
    Document,
    DocumentModelRelationship,
    DocumentType,
    ShareableLink,
    ShareableLinkAccess,
)


class DocumentModelRelationshipInline(admin.TabularInline):
    model = DocumentModelRelationship
    extra = 0
    readonly_fields = ("content_type", "object_id")
    raw_id_fields = ["content_type", "document"]


class ShareableLinkInline(admin.TabularInline):
    model = ShareableLink
    fields = ("valid_until", "one_time_link", "manual_invalid", "uuid")
    readonly_fields = ("uuid",)
    extra = 0
    raw_id_fields = ["document"]
    show_change_link = True


class ShareableLinkAccessInline(admin.TabularInline):
    model = ShareableLinkAccess
    extra = 0
    readonly_fields = [f.name for f in ShareableLinkAccess._meta.get_fields()]
    can_delete = False


class DocumentInLine(NonrelatedTabularInline):
    model = Document
    extra = 0
    fields = ["name", "description", "document_type", "file", "created"]
    readonly_fields = ["created"]
    show_change_link = True

    def get_form_queryset(self, obj):
        return Document.get_for_object(obj)

    def save_new_instance(self, parent, instance):
        instance.save()
        instance.link(parent)


@admin.register(Document)
class DocumentModelAdmin(GuardedModelAdmin):
    inlines = [DocumentModelRelationshipInline, ShareableLinkInline]
    list_display = ["id", "name", "file", "document_type", "created", "updated"]
    search_fields = ["name"]
    raw_id_fields = ["creator"]

    autocomplete_fields = ["creator"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("document_type")


@admin.register(DocumentType)
class DocumentTypeModelAdmin(admin.ModelAdmin):
    pass


@admin.register(DocumentModelRelationship)
class DocumentModelRelationshipModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ShareableLink)
class ShareableLinkModelAdmin(admin.ModelAdmin):
    readonly_fields = ["uuid", "document"]
    fieldsets = ((None, {"fields": (("document", "uuid"), ("valid_until", "one_time_link", "manual_invalid"))}),)
    inlines = [ShareableLinkAccessInline]
    list_display = ["uuid", "document", "valid_until", "one_time_link", "manual_invalid"]
