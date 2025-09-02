import pytest
from django.apps import apps
from django.db.models.signals import pre_migrate
from wbcore.contrib.example_app.tests.signals import app_pre_migration

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("geography"))


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-extensions")
    return chrome_options
