import factory

from wbcore.contrib.example_app.models import League


class LeagueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = League

    # country = factory.SubFactory("wbcore.contrib.geography.factories.CountryFactory")
    name = factory.Sequence(lambda n: "League %d" % n)
    points_per_win = factory.Faker("pyint", min_value=2, max_value=3)
    sport = factory.SubFactory("wbcore.contrib.example_app.factories.SportFactory")
    commissioner = factory.SubFactory("wbcore.contrib.example_app.factories.SportPersonFactory")
    established_date = factory.Faker("date_object")
    website = factory.Faker("url")
