from abc import ABC, abstractclassmethod

from wbcore.contrib.notifications.models import Notification


class AbstractNotificationBackend(ABC):
    @abstractclassmethod
    def send_notification(cls, notification: Notification): ...

    @abstractclassmethod
    def get_configuration(cls) -> dict: ...
