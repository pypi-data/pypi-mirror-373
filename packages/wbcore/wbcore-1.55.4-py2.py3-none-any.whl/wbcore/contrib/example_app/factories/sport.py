import factory

from wbcore.contrib.example_app.models import Sport


class SportFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Sport %d" % n)

    rules = factory.Faker("text", max_nb_chars=100)
    match_duration = factory.Faker("pyint", min_value=1, max_value=250)

    class Meta:
        model = Sport
