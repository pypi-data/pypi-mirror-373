import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from ..display import Display, SerializedDisplay


SerializedSection = dict[str, typing.Union[str, bool, "SerializedDisplay"]]


@dataclass
class Section:
    """A section makes it possible to grid certain fields together into an area inside a form

    Attributes:
        key: A reference for the positioning on the grid
        title: The title of the section, it will be displayed in on the top of a section
        display: The `Display` which holds the grid of the fields in this section
        collapsed: A flag to indicate whether this section is initially collapsed
        collapsible: A flag to indicate whether this section is collapsible

    """

    key: str
    title: str
    display: "Display"
    collapsed: bool = False
    collapsible: bool = True

    def serialize(self, key_prefix: str | None = None) -> SerializedSection:
        """Serializes this `Section`

        Returns:
            A dictionairy containing all serialized fields

        """
        return {
            "key": self.key,
            "title": self.title,
            "display": self.display.serialize(key_prefix=key_prefix),
            "collapsed": self.collapsed,
            "collapsible": self.collapsible,
        }
