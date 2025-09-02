from dataclasses import dataclass


@dataclass
class ConferenceRoom:
    name: str
    email: str
    name_building: str = None
    capacity: int = None
    is_videoconference_capable: bool = True
    id: str = None

    def __eq__(self, other):
        if other and (
            (self.id and other.id and self.id == other.id)
            or (self.email and other.email and self.email == other.email)
        ):
            return True
        return super().__eq__(other)
