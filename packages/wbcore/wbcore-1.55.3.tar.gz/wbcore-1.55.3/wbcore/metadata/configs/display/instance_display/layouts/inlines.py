import typing
from dataclasses import dataclass

from wbcore.metadata.utils import prefix_key

if typing.TYPE_CHECKING:
    from ..display import Display, SerializedDisplay


type SerializedInline = dict[str, str | SerializedDisplay | list[str] | bool]


@dataclass
class Inline:
    """An inline can be used to display a different endpoint in a form

    When generating a form, only fields of the original endpoint can be displayed. An inline allows you to specify
    remote content, for example a chart or a table, which the form asynchronously loads. This is very useful to
    create dashboard like views and to seperate the load to multiple endpoints

    Attributes:
        key: A reference for the positioning on the grid
        endpoint: A reference to the endpoint in the additional resources
        display: An optional `Display` to override the `display` behind the `endpoint` in the additional resources

    """

    key: str
    endpoint: str
    title: str | None = None
    display: typing.Optional["Display"] = None
    aligned_keys: list[str] | None = None
    hide_controls: bool = False

    def serialize(self, key_prefix: str | None = None) -> SerializedInline:
        """Serializes this `Inline`
        Attributes:
            key_prefix(Optional): if specified, append a prefix to the inline key
        Returns:
            A dictionairy containing all serialized fields

        """
        serialized_inline: SerializedInline = {
            "key": self.key,
            "endpoint": prefix_key(self.endpoint, key_prefix),
            "hide_controls": self.hide_controls,
        }

        if self.title is not None:
            serialized_inline["title"] = self.title

        if self.display:
            serialized_inline["display"] = self.display.serialize()

        if self.aligned_keys:
            serialized_inline["aligned_keys"] = self.aligned_keys

        return serialized_inline
