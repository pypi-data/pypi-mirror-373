from pytest_factoryboy import register
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.tests.conftest import *

from ..factories import (
    InternalUserFactory,
    SuperUserFactory,
    TokenFactory,
    UserActivityFactory,
    UserFactory,
)

register(UserFactory, _name="user")
register(SuperUserFactory, _name="superuser")
register(InternalUserFactory, _name="internal_user")
register(UserActivityFactory)
register(PersonFactory)
register(TokenFactory)
