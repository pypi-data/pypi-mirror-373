import pytest

from wbcore.contrib.notifications.models import Notification
from wbcore.contrib.notifications.utils import base_domain


@pytest.mark.django_db
class TestNotification:
    def test_factory(self, notification: Notification):
        assert isinstance(notification, Notification)
        assert notification.pk is not None

    def test_to_str(self, notification: Notification):
        assert str(notification) == f"{notification.user} {notification.title}"

    def test_endpoint_basename(self):
        assert Notification.get_endpoint_basename() == "wbcore:notifications:notification"

    def test_representation_value_key(self):
        assert Notification.get_representation_value_key() == "id"

    def test_representation_label_key(self):
        assert Notification.get_representation_label_key() == "{{title}}"

    @pytest.mark.parametrize("notification__endpoint", ["/wbcore/notifications/"])
    def test_full_valid_internal_endpoint(self, notification):
        assert notification.get_full_endpoint() == f"{base_domain()}{notification.endpoint}"

    @pytest.mark.parametrize("notification__endpoint", ["/some_invalid_namespace/notifications/"])
    def test_full_invalid_internal_endpoint(self, notification):
        assert notification.get_full_endpoint() is None

    @pytest.mark.parametrize("notification__endpoint", ["/wbcore/notifications/"])
    def test_full_internal_endpoint_as_shareable_link(self, notification):
        assert (
            notification.get_full_endpoint(as_shareable_internal_link=True)
            == f"{base_domain()}?widget_endpoint={notification.endpoint}"
        )

    @pytest.mark.parametrize("notification__endpoint", ["https://www.google.com"])
    def test_full_valid_external_endpoint(self, notification):
        assert notification.get_full_endpoint() == notification.endpoint

    @pytest.mark.parametrize("notification__endpoint", ["https.www.google.com"])
    def test_full_invalid_external_endpoint(self, notification):
        assert notification.get_full_endpoint() is None
