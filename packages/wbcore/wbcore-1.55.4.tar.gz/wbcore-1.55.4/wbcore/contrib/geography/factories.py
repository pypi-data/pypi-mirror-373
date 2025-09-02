from itertools import product
from string import ascii_uppercase

import factory

from .models import Geography

POSSIBLE_COUNTRY_CODE_2 = ["".join(i) for i in product(ascii_uppercase, repeat=2)]
POSSIBLE_COUNTRY_CODE_3 = ["".join(i) for i in product(ascii_uppercase, repeat=3)]


class ContinentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Geography

    name = factory.Faker("text", max_nb_chars=10)


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Geography

    code_3 = factory.Sequence(lambda n: POSSIBLE_COUNTRY_CODE_3[n % len(POSSIBLE_COUNTRY_CODE_3)])
    code_2 = factory.Sequence(lambda n: POSSIBLE_COUNTRY_CODE_2[n % len(POSSIBLE_COUNTRY_CODE_2)])
    parent = factory.LazyAttribute(lambda x: ContinentFactory.create())
    name = factory.Faker("country")


class StateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Geography

    code_3 = factory.Sequence(lambda n: POSSIBLE_COUNTRY_CODE_3[n % len(POSSIBLE_COUNTRY_CODE_3)])
    code_2 = factory.Sequence(lambda n: POSSIBLE_COUNTRY_CODE_2[n % len(POSSIBLE_COUNTRY_CODE_2)])
    parent = factory.SubFactory(CountryFactory)
    name = factory.Faker("state")


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Geography

    code_3 = factory.Sequence(lambda n: POSSIBLE_COUNTRY_CODE_3[n % len(POSSIBLE_COUNTRY_CODE_3)])
    code_2 = factory.Sequence(lambda n: POSSIBLE_COUNTRY_CODE_2[n % len(POSSIBLE_COUNTRY_CODE_2)])
    parent = factory.SubFactory(StateFactory)
    name = factory.Faker("city")
