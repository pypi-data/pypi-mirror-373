import factory

from wbcore.contrib.notifications.models.tokens import NotificationUserToken


class NotificationUserTokenModelFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory("wbcore.contrib.authentication.factories.UserFactory")
    token = factory.Faker("pystr")
    device_type = factory.Iterator(NotificationUserToken.NotificationDeviceType.choices, getter=lambda c: c[0])

    class Meta:
        model = NotificationUserToken
