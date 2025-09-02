from typing import Iterable

from django.contrib.messages.storage.base import BaseStorage, Message
from django.contrib.messages.storage.fallback import FallbackStorage
from rest_framework_simplejwt.settings import api_settings

MESSAGE_TYPE_MAPPING = {
    10: "debug",
    20: "info",
    25: "success",
    30: "warning",
    40: "error",
}


class InMemoryMessageStorage(BaseStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._messages = []

    def _get(self, *args, **kwargs):
        """
        Retrieve a list of messages. Returns a tuple of (messages, all_retrieved).
        """
        return self._messages, True

    def _store(self, messages, *args, **kwargs):
        """
        Store a list of messages.
        """
        self._messages = messages

    def add(self, level, message, extra_tags="", *args, **kwargs):
        """
        Adds a message to the storage.
        """
        if not message:
            return
        message_instance = Message(level, message, extra_tags=extra_tags)
        self._messages.append(message_instance)

    def __iter__(self):
        return iter(self._messages)

    def serialize_messages(self) -> Iterable[dict[str, str | int]]:
        for message in self._messages:
            extra_parameters = dict([param.split("=") for param in message.extra_tags.split(" ") if param != ""])
            auto_close = int(extra_parameters.get("auto_close", "5")) * 1000
            yield {
                "message": message.message,
                "type": MESSAGE_TYPE_MAPPING[message.level],
                "auto_close": auto_close,
            }


def route_message_storage(request):
    # This is a simple hack to detect when the request is initiated by our frontend client or by a session based page (e.g. Admin)
    if request.META.get(api_settings.AUTH_HEADER_NAME):
        return InMemoryMessageStorage(request)
    return FallbackStorage(request)
