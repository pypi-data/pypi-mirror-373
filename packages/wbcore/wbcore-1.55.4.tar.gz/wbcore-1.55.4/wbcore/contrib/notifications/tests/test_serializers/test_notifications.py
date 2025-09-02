import pytest

from wbcore.contrib.notifications.serializers import (
    NotificationModelSerializer,
    NotificationTypeRepresentationSerializer,
)


@pytest.mark.django_db
class TestNotificationModelSerializer:
    def test_serialize_instance(self, notification, request_with_user):
        serializer = NotificationModelSerializer(notification, context={"request": request_with_user})
        assert serializer.data == {
            "id": notification.id,
            "title": notification.title,
            "notification_type": notification.notification_type.id,
            "_notification_type": NotificationTypeRepresentationSerializer(notification.notification_type).data,
            "body": notification.body,
            "user": notification.user.pk,
            "endpoint": notification.endpoint,
            "sent": notification.sent,
            "read": notification.read,
            "_additional_resources": {},
        }
