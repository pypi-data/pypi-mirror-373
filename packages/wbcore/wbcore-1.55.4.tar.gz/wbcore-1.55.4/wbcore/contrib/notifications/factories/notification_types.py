import factory

from wbcore.contrib.notifications.models import (
    NotificationType,
    NotificationTypeSetting,
)


class NotificationTypeModelFactory(factory.django.DjangoModelFactory):
    code = factory.Faker("pystr")
    title = factory.Faker("pystr")
    help_text = factory.Faker("pystr")

    class Meta:
        model = NotificationType


class NotificationTypeSettingModelFactory(factory.django.DjangoModelFactory):
    notification_type = factory.SubFactory(NotificationTypeModelFactory)
    user = factory.SubFactory("wbcore.contrib.authentication.factories.UserFactory")

    class Meta:
        model = NotificationTypeSetting
        django_get_or_create = ("user", "notification_type")
