from django.contrib import admin
from django.db.models import Q
from django.forms import ModelForm
from reversion.admin import VersionAdmin

from ..models import (
    ClientManagerRelationship,
    EmployerEmployeeRelationship,
    Position,
    Relationship,
    RelationshipType,
)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("id", "title")


@admin.register(Relationship)
class RelationshipModelAdmin(VersionAdmin):
    list_display = ("id", "relationship_type", "from_entry", "to_entry")
    autocomplete_fields = ("relationship_type",)

    def reversion_register(self, model, **options):
        options = {
            "follow": (
                "from_entry",
                "to_entry",
                "relationship_type",
            )
        }
        super().reversion_register(model, **options)


class RelationshipTypeModelAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["counter_relationship"].queryset = RelationshipType.objects.filter(
            ~Q(id=self.instance.id) & (Q(counter_relationship=self.instance) | Q(counter_relationship=None))
        )


@admin.register(RelationshipType)
class RelationshipTypeModelAdmin(VersionAdmin):
    form = RelationshipTypeModelAdminForm
    list_display = ("title", "counter_relationship")
    search_fields = ("title",)

    def reversion_register(self, model, **options):
        options = {"follow": ("counter_relationship",)}
        super().reversion_register(model, **options)


@admin.register(ClientManagerRelationship)
class ClientManagerRelationshipModelAdmin(VersionAdmin):
    search_fields = ("relationship_manager__computed_str", "client__computed_str")
    list_display = ("id", "relationship_manager", "client", "primary", "status", "created")

    def reversion_register(self, model, **options):
        options = {
            "follow": (
                "client",
                "relationship_manager",
            )
        }
        super().reversion_register(model, **options)


@admin.register(EmployerEmployeeRelationship)
class EmployerEmployeeRelationshipAdmin(admin.ModelAdmin):
    list_display = ("id", "employer", "employee", "primary", "position", "position_name")
