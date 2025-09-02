import factory
import pytz

from ..models import (
    ClientManagerRelationship,
    EmployerEmployeeRelationship,
    Position,
    Relationship,
    RelationshipType,
)
from .entries import CompanyFactory, EntryFactory, PersonFactory


class PositionFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text", max_nb_chars=32)

    class Meta:
        model = Position


class RelationshipTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RelationshipType

    title = factory.Sequence(lambda n: f"Title {n}")
    counter_relationship = factory.SubFactory(
        "wbcore.contrib.directory.factories.ParentRelationshipTypeFactory", counter_relationship=None
    )


class ParentRelationshipTypeFactory(RelationshipTypeFactory):
    counter_relationship = None


class RelationshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Relationship

    relationship_type = factory.SubFactory(
        "wbcore.contrib.directory.factories.RelationshipTypeFactory",
    )
    from_entry = factory.SubFactory(EntryFactory)
    to_entry = factory.SubFactory(EntryFactory)


class EmployerEmployeeRelationshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmployerEmployeeRelationship

    employer = factory.SubFactory(CompanyFactory)
    employee = factory.SubFactory(PersonFactory)
    position = factory.SubFactory(PositionFactory)
    position_name = factory.Faker("text", max_nb_chars=64)
    primary = False


class ClientManagerRelationshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClientManagerRelationship

    status = ClientManagerRelationship.Status.APPROVED
    client = factory.SubFactory(EntryFactory)
    relationship_manager = factory.SubFactory(PersonFactory)
    created = factory.Faker("date_time", tzinfo=pytz.utc)
    primary = False


class UserIsClientPersonFactory(PersonFactory):
    @factory.post_generation
    def relationships(self, create, extracted, **kwargs):
        ClientManagerRelationshipFactory(relationship_manager=self)


class UserIsManagerEntryFactory(EntryFactory):
    @factory.post_generation
    def relationships(self, create, extracted, **kwargs):
        ClientManagerRelationshipFactory(client=self)
