from pytest_factoryboy import register
from wbcore.tests.conftest import *

from ..factories import TagFactory, TagGroupFactory

register(TagFactory)
register(TagGroupFactory)
