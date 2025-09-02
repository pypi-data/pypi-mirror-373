import factory
from django.db.models import signals

from wbcore.contrib.icons import WBIcon
from wbcore.contrib.workflow.models import Transition


@factory.django.mute_signals(signals.post_save)
class TransitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transition
        exclude = ("_workflow",)

    _workflow = factory.SubFactory("wbcore.contrib.workflow.factories.WorkflowFactory")

    from_step = factory.SubFactory(
        "wbcore.contrib.workflow.factories.StartStepFactory",
        workflow=factory.SelfAttribute(".._workflow"),
    )
    to_step = factory.SubFactory(
        "wbcore.contrib.workflow.factories.FinishStepFactory",
        workflow=factory.SelfAttribute(".._workflow"),
    )

    icon = factory.Iterator(WBIcon.values)

    name = factory.Sequence(lambda n: f"Transition #{n}")
