from django.db import models
from django.utils.translation import gettext_lazy as _

from wbcore.contrib.agenda.typings import ConferenceRoom as ConferenceRoomDTO
from wbcore.models import WBModel


class Building(WBModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    address = models.ForeignKey(
        on_delete=models.SET_NULL,
        to="directory.AddressContact",
        verbose_name=_("Address"),
        related_name="conference_room_building",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.name}"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:agenda:building"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:agenda:buildingrepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

    class Meta:
        verbose_name = _("Building")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "address"],
                name="unique_building",
            ),
        ]


class ConferenceRoom(WBModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    email = models.EmailField(verbose_name=_("Email Address"), unique=True)
    building = models.ForeignKey(
        on_delete=models.CASCADE,
        to=Building,
        verbose_name=_("Building"),
        related_name="conference_room",
    )
    capacity = models.PositiveIntegerField(verbose_name=_("Capacity"), null=True, blank=True)
    is_videoconference_capable = models.BooleanField(verbose_name=_("Capable of Videoconferencing"), default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.building.name})"

    def _build_dto(self):
        return ConferenceRoomDTO(
            name=self.name,
            email=self.email,
            name_building=self.building.name,
            capacity=self.capacity,
            is_videoconference_capable=self.is_videoconference_capable,
            id=self.id,
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:agenda:conferenceroom"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:agenda:conferenceroomrepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}} ({{_building.name}})"

    class Meta:
        verbose_name = _("Conference Room")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "building"],
                name="unique_conference_room",
            ),
        ]
