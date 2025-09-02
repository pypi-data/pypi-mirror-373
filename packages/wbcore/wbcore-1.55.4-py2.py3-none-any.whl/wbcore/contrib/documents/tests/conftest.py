import pytest
from django.apps import apps
from django.db import connection
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.documents.factories import (
    DocumentFactory,
    DocumentTypeFactory,
    ShareableLinkAccessFactory,
    ShareableLinkFactory,
)
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbcore.tests.conftest import *

register(DocumentFactory)
register(DocumentTypeFactory)
register(ShareableLinkAccessFactory)
register(ShareableLinkFactory)


@pytest.fixture(
    autouse=True, scope="session"
)  # Might want to find a way to registered default conftest logic automatically
def django_test_environment(django_test_environment):
    from django.apps import apps

    get_models = apps.get_models

    for m in [m for m in get_models() if not m._meta.managed]:
        m._meta.managed = True
