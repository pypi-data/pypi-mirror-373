from contextlib import suppress

from django.db.utils import ProgrammingError
from dynamic_preferences.registries import global_preferences_registry

from wbcore.contrib.directory.models import Company


def get_main_company() -> Company | None:
    with suppress(RuntimeError, ProgrammingError, Company.DoesNotExist):
        return Company.objects.get(id=global_preferences_registry.manager()["directory__main_company"])
