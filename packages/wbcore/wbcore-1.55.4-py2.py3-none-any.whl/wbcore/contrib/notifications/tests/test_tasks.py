import pytest
from bs4 import BeautifulSoup
from django.core import mail
from django.test.utils import override_settings

from wbcore.contrib.notifications import tasks


@pytest.fixture
def patched_send_notification_email(mocker):
    return mocker.patch("wbcore.contrib.notifications.tasks.send_notification_email")


@pytest.fixture
def patched_import_string(mocker):
    return mocker.patch("wbcore.contrib.notifications.tasks.import_string")


@pytest.fixture
def mock_backend():
    from wbcore.contrib.notifications.backends.abstract_backend import (
        AbstractNotificationBackend,
    )

    class MockedBackend(AbstractNotificationBackend):
        @classmethod
        def send_notification(cls, notification):
            pass

        @classmethod
        def get_configuration(cls) -> dict:
            return {}

    return MockedBackend


@pytest.mark.django_db
def test_send_notification_task(
    notification, mock_backend, mocker, patched_send_notification_email, patched_import_string
):
    notification.user.wbnotification_user_settings.update(enable_email=True)
    spy = mocker.spy(mock_backend, "send_notification")
    patched_import_string.return_value = mock_backend

    tasks.send_notification_task(notification.pk)

    patched_send_notification_email.assert_called_once_with(notification)
    patched_import_string.assert_called_once()
    spy.assert_called_once_with(notification)


@pytest.mark.django_db
def test_send_notification_task_without_mail(
    notification, mock_backend, patched_send_notification_email, patched_import_string
):
    notification.user.wbnotification_user_settings.update(enable_email=False)
    patched_import_string.return_value = mock_backend

    tasks.send_notification_task(notification.pk)

    assert not patched_send_notification_email.called


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
@pytest.mark.parametrize("notification__endpoint", ["/wbcore/notifications/"])
def test_send_notification_email(notification):
    assert len(mail.outbox) == 0
    tasks.send_notification_email(notification)
    assert len(mail.outbox) == 1
    soup = BeautifulSoup(mail.outbox[0].alternatives[0][0], "html.parser")
    assert soup.find("a", href=notification.get_full_endpoint(as_shareable_internal_link=True))
