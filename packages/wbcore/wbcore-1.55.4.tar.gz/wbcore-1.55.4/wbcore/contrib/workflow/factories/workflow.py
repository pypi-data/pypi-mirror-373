import factory
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals

from wbcore.contrib.directory.models import Person
from wbcore.contrib.workflow.models import Workflow


@factory.django.mute_signals(signals.post_save)
class WorkflowFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    status_field = "first_name"
    single_instance_execution = factory.Faker("pybool")
    preserve_instance = factory.Faker("pybool")
    model = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(Person))
    graph = factory.django.ImageField()

    class Meta:
        model = Workflow
        django_get_or_create = ["name"]
