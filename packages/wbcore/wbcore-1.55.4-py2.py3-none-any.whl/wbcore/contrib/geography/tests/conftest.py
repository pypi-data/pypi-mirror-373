import pytest

from django.apps import apps
from django.db import connection
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from rest_framework.test import APIRequestFactory, APIClient
from wbcore.contrib.authentication.factories import UserFactory

from ..factories import ContinentFactory
from .signals import app_pre_migration

register(ContinentFactory)


pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("geography"))


@pytest.fixture()
def request_factory():
    return APIRequestFactory()


@pytest.fixture()
def super_user():
    return UserFactory(is_superuser=True)
