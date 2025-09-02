from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from wbcore import serializers
from wbcore.contrib.agenda.models import Building, ConferenceRoom
from wbcore.contrib.directory.serializers.contacts import (
    AddressContactRepresentationSerializer,
)


class BuildingRepresentationSerializer(serializers.RepresentationSerializer):
    endpoint = "wbcore:agenda:buildingrepresentation-list"
    _detail = serializers.HyperlinkField(reverse_name="wbcore:agenda:building-detail")
    _address = AddressContactRepresentationSerializer(source="address")

    class Meta:
        model = Building
        fields = (
            "id",
            "name",
            "address",
            "_address",
            "_detail",
        )


class ConferenceRoomRepresentationSerializer(serializers.RepresentationSerializer):
    endpoint = "wbcore:agenda:conferenceroomrepresentation-list"
    _detail = serializers.HyperlinkField(reverse_name="wbcore:agenda:conferenceroom-detail")
    _building = BuildingRepresentationSerializer(source="building")

    class Meta:
        model = ConferenceRoom
        fields = (
            "id",
            "name",
            "building",
            "_building",
            "_detail",
        )


class BuildingModelSerializer(serializers.ModelSerializer):
    _address = AddressContactRepresentationSerializer(source="address")

    class Meta:
        model = Building
        fields = (
            "id",
            "name",
            "address",
            "_address",
        )

    def validate(self, data):
        name = data.get("name", None)
        address = data.get("address", None)

        if address:
            building = Building.objects.filter(name=name, address=address)
        else:
            building = Building.objects.filter(name=name)
        if obj := self.instance:
            building = building.exclude(id=obj.id)
        if building.exists():
            raise ValidationError({"name": _("A building with this name and address already exists.")})
        return data


class ConferenceRoomModelSerializer(serializers.ModelSerializer):
    _building = BuildingRepresentationSerializer(source="building")

    class Meta:
        model = ConferenceRoom
        fields = (
            "id",
            "name",
            "email",
            "building",
            "_building",
            "capacity",
            "is_videoconference_capable",
        )

    def validate(self, data):
        name = data.get("name", None)
        building = data.get("building", None)
        email = data.get("email", None)

        mail_dupl = ConferenceRoom.objects.filter(email=email)
        conference_room_dupl = ConferenceRoom.objects.filter(name=name, building=building)
        if obj := self.instance:
            mail_dupl = mail_dupl.exclude(id=obj.id)
            conference_room_dupl = conference_room_dupl.exclude(id=obj.id)
        if mail_dupl.exists():
            raise ValidationError({("email"): _("A conference room with this email address already exists.")})
        if conference_room_dupl.exists():
            raise ValidationError({("name"): _("A conference room with this name already exists in this building.")})
        return data
