import pytest
from django.apps import apps
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import InternalUserFactory, UserFactory
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbcore.tests.conftest import *


pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("geography"))
