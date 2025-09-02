from dataclasses import dataclass


@dataclass
class Person:
    first_name: str
    last_name: str
    email: str
    id: str = None

    def __eq__(self, other):
        if other and (
            (self.id and other.id and self.id == other.id)
            or (self.email and other.email and self.email == other.email)
        ):
            return True
        return super().__eq__(other)
