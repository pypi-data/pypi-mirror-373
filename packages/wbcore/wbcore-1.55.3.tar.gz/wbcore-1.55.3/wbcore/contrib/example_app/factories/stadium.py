import factory

from wbcore.contrib.example_app.models import Stadium


class StadiumFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=16)
    standing_capacity = factory.Faker("pyint", min_value=100, max_value=100000)
    seating_capacity = factory.Faker("pyint", min_value=100, max_value=100000)
    # city = factory.SubFactory("wbcore.contrib.geography.factories.CityFactory")

    class Meta:
        model = Stadium
