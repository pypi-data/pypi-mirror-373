from dataclasses import dataclass
from typing import TYPE_CHECKING

from .layouts.layouts import Layout, SerializedLayout

if TYPE_CHECKING:
    from .display import Display, SerializedDisplay


type SerializedPage = dict[str, None | str | dict[str, SerializedLayout] | SerializedDisplay]


@dataclass
class Page:
    """Represents a page, which may include an optional title and a dictionary defining layout boundaries along with a Layout. Alternatively, a list of subpages can also be specified."""

    title: str | None = None
    layouts: dict[str, Layout] | None = None
    display: "Display | None" = None

    def serialize(self, key_prefix: str | None = None, view_config=None, view=None, request=None) -> SerializedPage:
        """Serializes the `Page` into a dictionairy

        Returns:
            A dictionairy containing all fields of a `Page`

        """
        page: SerializedPage = {
            "title": self.title,
        }

        if self.layouts is not None:
            page["layouts"] = {key: layout.serialize(key_prefix=key_prefix) for key, layout in self.layouts.items()}

        elif self.display is not None:
            page["display"] = self.display.serialize(
                view_config=view_config, view=view, request=request, key_prefix=key_prefix, parent_page=self
            )

        return page
