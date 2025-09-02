from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.agenda.models import Building, ConferenceRoom
from wbcore.contrib.directory.models import AddressContact


class ConferenceRoomFilter(filters.FilterSet):
    building = filters.ModelMultipleChoiceFilter(
        label=_("Buildings"),
        queryset=Building.objects.all(),
        endpoint=Building.get_representation_endpoint(),
        value_key=Building.get_representation_value_key(),
        label_key=Building.get_representation_label_key(),
        field_name="building",
    )

    class Meta:
        model = ConferenceRoom
        fields = {
            "name": ["exact", "icontains"],
            "is_videoconference_capable": ["exact"],
            "email": ["exact", "icontains"],
            "capacity": ["exact", "lte", "gte"],
        }


class BuildingFilter(filters.FilterSet):
    address = filters.ModelMultipleChoiceFilter(
        label=_("Addresses"),
        queryset=AddressContact.objects.all(),
        endpoint=AddressContact.get_representation_endpoint(),
        value_key=AddressContact.get_representation_value_key(),
        label_key=AddressContact.get_representation_label_key(),
        field_name="address",
    )

    class Meta:
        model = Building
        fields = {
            "name": ["exact", "icontains"],
        }
