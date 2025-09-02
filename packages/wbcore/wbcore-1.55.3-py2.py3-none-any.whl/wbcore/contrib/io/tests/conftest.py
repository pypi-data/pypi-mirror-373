import pytest
from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import SuperUserFactory, UserFactory
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.tests.conftest import *  # noqa

from ..factories import (
    CrontabScheduleFactory,
    DataBackendFactory,
    ExportSourceFactory,
    ImportCredentialFactory,
    ImportModelFactory,
    ImportSourceFactory,
    ParserHandlerFactory,
    ProviderFactory,
    SourceFactory,
)

register(CrontabScheduleFactory)
register(ImportSourceFactory)
register(ImportCredentialFactory)
register(SourceFactory)
register(ParserHandlerFactory)
register(ExportSourceFactory)
register(ImportModelFactory)
register(ProviderFactory)
register(DataBackendFactory)
register(UserFactory)
register(SuperUserFactory, "superuser")
register(PersonFactory)


@pytest.fixture(
    autouse=True, scope="session"
)  # Might want to find a way to registered default conftest logic automatically
def django_test_environment(django_test_environment):
    from django.apps import apps

    get_models = apps.get_models

    for m in [m for m in get_models() if not m._meta.managed]:
        m._meta.managed = True
