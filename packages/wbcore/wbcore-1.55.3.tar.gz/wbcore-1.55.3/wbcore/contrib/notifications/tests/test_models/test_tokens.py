import pytest

from wbcore.contrib.notifications.factories.notification_types import (
    NotificationTypeSettingModelFactory,
)
from wbcore.contrib.notifications.models import NotificationUserToken


@pytest.mark.django_db
class TestNotificationUserToken:
    def test_factory(self, notification_user_token: NotificationUserToken):
        assert isinstance(notification_user_token, NotificationUserToken)
        assert notification_user_token.pk is not None

    def test_to_str(self, notification_user_token: NotificationUserToken):
        assert str(notification_user_token) == "{0.user}: {0.token} ({0.device_type})".format(notification_user_token)

    def test_filter_for_settings(self, notification_user_token: NotificationUserToken):
        setting = NotificationTypeSettingModelFactory(
            user=notification_user_token.user, enable_web=True, enable_mobile=True
        )
        assert setting.enable_web is False
        assert setting.enable_mobile is False
        assert not NotificationUserToken.objects.filter_for_user_settings(setting).exists()

        setting.enable_web = True
        setting.enable_mobile = True
        setting.save()

        assert NotificationUserToken.objects.filter_for_user_settings(setting).first() == notification_user_token  # type: ignore
