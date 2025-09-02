from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Delete all objects (obtained using content type and object id) whose related item was deleted"

    def add_arguments(self, parser):
        parser.add_argument("app", type=str)
        parser.add_argument("model", type=str)
        parser.add_argument("--field", type=str)

    def handle(self, *args, **options):
        model_class = apps.get_model(app_label=options["app"], model_name=options["model"])
        field = options["field"] if options["field"] else "content_object"

        for object in model_class.objects.all():
            if not getattr(object, field, None):
                object.delete()

        self.stdout.write("Deletion completed")
