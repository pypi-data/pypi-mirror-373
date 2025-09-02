import factory
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from wbcore.contrib.directory.factories import PersonFactory
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import PersonModelSerializer
from wbcore.contrib.workflow.models import Process, ProcessStep, Step


def _get_person_dict() -> dict:
    data = PersonModelSerializer(PersonFactory()).data
    # Serializer throws error when both fields are blank
    data["primary_email"] = None
    data["primary_telephone"] = None
    return data


class ProcessFactory(factory.django.DjangoModelFactory):
    id = factory.Faker("uuid4")
    workflow = factory.SubFactory("wbcore.contrib.workflow.factories.WorkflowFactory")
    started = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    finished = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    instance = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")
    instance_id = factory.SelfAttribute("instance.pk")
    content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(Person))
    preserved_instance = factory.Maybe(
        "preserve_instance_activated",
        yes_declaration=factory.LazyAttribute(lambda x: _get_person_dict()),
        no_declaration=None,
    )
    state = factory.Iterator(Process.ProcessState.values)

    class Meta:
        model = Process

    class Params:
        preserve_instance_activated = factory.SelfAttribute("workflow.preserve_instance")


class ProcessStepFactory(factory.django.DjangoModelFactory):
    id = factory.Faker("uuid4")
    process = factory.SubFactory(ProcessFactory)
    step = factory.SubFactory("wbcore.contrib.workflow.factories.RandomChildStepFactory")
    started = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    finished = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    assignee = factory.Maybe(
        "is_userstep",
        yes_declaration=factory.LazyAttribute(lambda x: x.step.get_casted_step().get_assigned_user()),
        no_declaration=None,
    )
    group = factory.Maybe(
        "is_userstep",
        yes_declaration=factory.LazyAttribute(lambda x: x.step.get_casted_step().get_assigned_group()),
        no_declaration=None,
    )
    state = factory.Iterator(ProcessStep.StepState.values)
    status = factory.SelfAttribute("step.status")
    error_message = factory.Maybe(
        "step_failed",
        yes_declaration=factory.Faker("text", max_nb_chars=128),
        no_declaration=None,
    )

    class Params:
        is_userstep = factory.LazyAttribute(lambda x: x.step.step_type == Step.StepType.USERSTEP)
        step_failed = factory.LazyAttribute(lambda x: x.state == ProcessStep.StepState.FAILED)

    class Meta:
        model = ProcessStep
