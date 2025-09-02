from importlib import import_module
from os import environ

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bootstrap the current module"

    def handle(self, *args, **options):
        self.stdout.write("Migrating Database")
        call_command("migrate")
        settings = import_module(str(environ.get("DJANGO_SETTINGS_MODULE")))
        self.stdout.write("Loading Fixtures...")
        for fixture in getattr(settings, "BOOTSTRAP_FIXTURES", []):
            self.stdout.write(f"Load {fixture}: ", ending="")
            call_command("loaddata", fixture)
