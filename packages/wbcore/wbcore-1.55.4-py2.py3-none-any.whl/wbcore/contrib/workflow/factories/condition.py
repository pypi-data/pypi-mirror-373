import factory
from django.db.models import signals

from wbcore.contrib.workflow.models import Condition


@factory.django.mute_signals(signals.post_save)
class ConditionFactory(factory.django.DjangoModelFactory):
    attribute_name = factory.SelfAttribute("transition.to_step.workflow.status_field")
    expected_value = factory.Faker("text", max_nb_chars=64)
    transition = factory.SubFactory("wbcore.contrib.workflow.factories.TransitionFactory")
    operator = factory.Iterator(Condition.Operator.values)
    negate_operator = factory.Faker("pybool")

    class Meta:
        model = Condition
