import pytest

from wbcore.contrib.agenda.typings import ConferenceRoom as ConferenceRoomDTO


@pytest.mark.django_db
class TestDTO:
    @pytest.mark.parametrize(
        "id, name, email",
        [
            (None, None, None),
            (None, "test", None),
            (None, "test", "test@test.com"),
            (1, None, None),
            (1, "test", None),
            (1, "test", "test@test.com"),
        ],
    )
    def test_comparison(self, id, name, email):
        conf_room1 = ConferenceRoomDTO(1, "test", "test@test.com")
        conf_room2 = ConferenceRoomDTO(id=id, name=name, email=email)
        if (conf_room1.id == conf_room2.id is not None) or (conf_room1.email == conf_room2.email is not None):
            assert conf_room1 == conf_room2
        else:
            assert conf_room1 != conf_room2
        assert conf_room2 is not None
