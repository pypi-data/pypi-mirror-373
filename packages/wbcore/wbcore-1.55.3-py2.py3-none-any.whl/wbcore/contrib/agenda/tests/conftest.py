from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.directory.factories import EntryFactory, PersonFactory
from wbcore.tests.conftest import *

from ..factories import BuildingFactory, CalendarItemFactory, ConferenceRoomFactory
from .signals import *

register(CalendarItemFactory)
register(BuildingFactory)
register(EntryFactory)
register(PersonFactory)
register(UserFactory)
register(ConferenceRoomFactory)
