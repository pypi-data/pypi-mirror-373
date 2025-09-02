import factory

from wbcore.contrib.agenda.models import Building, ConferenceRoom


class BuildingFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=32)

    class Meta:
        model = Building


class ConferenceRoomFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=32)
    email = factory.Faker("email")
    building = factory.SubFactory(BuildingFactory)

    class Meta:
        model = ConferenceRoom
        django_get_or_create = ["email"]
