from dataclasses import dataclass
from typing import Iterable

from wbcore.utils.importlib import parse_signal_received_for_module

from .enums import NavigationType
from .pages import Page, SerializedPage
from .signals import add_display_pages

type SerializedDisplay = dict[str, NavigationType | SerializedPage]


@dataclass
class Display:
    """A display contains multiple pages and a navigation type. When only 1 page is specified, the navigation type is irrelevant"""

    pages: Iterable[Page]
    navigation_type: NavigationType = NavigationType.TAB

    def serialize(
        self, view_config=None, view=None, request=None, key_prefix=None, parent_page=None
    ) -> SerializedDisplay:
        """Serializes a `Display`

        Returns:
            A dictionary with all pages and the navigation type

        """
        serialized_pages = [
            page.serialize(key_prefix=key_prefix, view_config=view_config, view=view, request=request)
            for page in self.pages
        ]
        # we only allow remote page registration if the display is the top display. We could argue that we want to allow dev to register pages for any nested display by passing down the page argument. This involves refactoring of the signal receivers
        if view_config and parent_page is None:
            for prefix, remote_pages in parse_signal_received_for_module(
                add_display_pages.send(view_config.__class__, request=request, view=view)
            ):
                for remote_page in remote_pages:
                    serialized_pages.append(remote_page.serialize(prefix, view_config, view, request))
        return {"navigationType": self.navigation_type.value, "pages": serialized_pages}
