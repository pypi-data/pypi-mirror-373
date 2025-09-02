from django.utils.translation import gettext_lazy as _

from wbcore import filters as wb_filters

from ..models import (
    ClientManagerRelationship,
    Entry,
    Person,
    Relationship,
    RelationshipType,
)


class RelationshipEntryFilter(wb_filters.FilterSet):
    relationship_type = wb_filters.ModelMultipleChoiceFilter(
        label=_("Relationship Types"),
        queryset=RelationshipType.objects.all(),
        endpoint=RelationshipType.get_representation_endpoint(),
        value_key=RelationshipType.get_representation_value_key(),
        label_key=RelationshipType.get_representation_label_key(),
    )

    to_entry = wb_filters.ModelMultipleChoiceFilter(
        label=_("Relationship To"),
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
    )

    class Meta:
        model = Relationship
        fields = {}


class RelationshipFilter(RelationshipEntryFilter):
    from_entry = wb_filters.ModelMultipleChoiceFilter(
        label=_("Relationship From"),
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
    )


class RelationshipTypeFilter(wb_filters.FilterSet):
    counter_relationship = wb_filters.ModelMultipleChoiceFilter(
        label=_("Counter Relationship Types"),
        queryset=RelationshipType.objects.all(),
        endpoint=RelationshipType.get_representation_endpoint(),
        value_key=RelationshipType.get_representation_value_key(),
        label_key=RelationshipType.get_representation_label_key(),
    )

    class Meta:
        model = RelationshipType
        fields = {"title": ["exact", "icontains"]}


class ClientManagerFilter(wb_filters.FilterSet):
    client = wb_filters.ModelMultipleChoiceFilter(
        label=_("Clients"),
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
    )
    relationship_manager = wb_filters.ModelMultipleChoiceFilter(
        label=_("Future Relationship Managers"),
        queryset=Person.objects.all(),
        endpoint=Person.get_representation_endpoint(),
        value_key=Person.get_representation_value_key(),
        label_key=Person.get_representation_label_key(),
    )
    status = wb_filters.ChoiceFilter(
        label=_("Status"),
        choices=ClientManagerRelationship.Status.choices,
    )

    def filter_already_in_charge(self, queryset, name, value):
        if value:
            return queryset.filter(relationship_managers__in=value)
        return queryset

    class Meta:
        model = ClientManagerRelationship
        fields = {
            "created": ["exact"],
            "primary": ["exact"],
        }
