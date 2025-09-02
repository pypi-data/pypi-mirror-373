import random

import factory

from wbcore.contrib.example_app.models import Event, EventType
from wbcore.contrib.icons.icons import WBIcon


class EventTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Event %d" % n)
    sport = factory.SubFactory("wbcore.contrib.example_app.factories.SportFactory")
    points = factory.Faker("pyint", min_value=0, max_value=3)
    icon = factory.LazyAttribute(lambda x: WBIcon[random.choice(WBIcon.names)].icon)
    color = factory.Faker("color")

    class Meta:
        model = EventType


class EventFactory(factory.django.DjangoModelFactory):
    person = factory.SubFactory("wbcore.contrib.example_app.factories.SportPersonFactory")
    match = factory.SubFactory("wbcore.contrib.example_app.factories.MatchFactory")
    minute = factory.Faker("random_int", min=1, max=factory.SelfAttribute("..match.league.sport.match_duration"))
    event_type = factory.SubFactory(EventTypeFactory, sport=factory.SelfAttribute("..match.sport"))

    class Meta:
        model = Event
