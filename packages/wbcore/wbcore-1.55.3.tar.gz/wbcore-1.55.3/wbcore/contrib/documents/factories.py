import factory

from wbcore.contrib.documents.models import (
    Document,
    DocumentType,
    ShareableLink,
    ShareableLinkAccess,
)


class DocumentTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=64)
    parent = None

    class Meta:
        model = DocumentType


class DocumentFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=64)
    file = factory.django.FileField(data="test")
    document_type = factory.SubFactory(DocumentTypeFactory)
    system_created = False
    system_key = None

    class Meta:
        model = Document


class ShareableLinkFactory(factory.django.DjangoModelFactory):
    document = factory.SubFactory(DocumentFactory)
    manual_invalid = False
    valid_until = None
    one_time_link = False

    class Meta:
        model = ShareableLink


class ShareableLinkAccessFactory(factory.django.DjangoModelFactory):
    shareable_link = factory.SubFactory(ShareableLinkFactory)

    class Meta:
        model = ShareableLinkAccess
