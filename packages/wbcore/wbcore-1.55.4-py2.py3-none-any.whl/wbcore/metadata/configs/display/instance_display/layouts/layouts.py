from dataclasses import dataclass, field

from wbcore.metadata.configs.display.instance_display.styles import Style
from wbcore.metadata.configs.display.instance_display.utils import grid_definition

from .inlines import Inline, SerializedInline
from .sections import Section, SerializedSection

type SerializedLayout = dict[str, str | list[SerializedInline] | list[SerializedSection]]


@dataclass
class Layout:
    """A layout contains all the information on how a form is build.

    A form is rendered based on a grid, which is closely modelled after a CSS Grid. Essentially, we can define
    rows and columns and places fields on this grid, either in one cell, or spanning multiple rows and columns.

    In the future we will add all other features of css grid to ensure full control over the grid.

    Attributes:
        grid_template_areas: A 2D string Array containing the areas on the grid. The strings are the keys references to all fields
        grid_template_columns: A string array containing the column definitions for the width of each column
        grid_template_rows: A string array containing the row definitions for the height of each row
        sections: A list of sections that can be positioned in `grid_template_areas`
        inlines: A list of inlines that can be positioned in `grid_template_areas`
        gap: A string specifying the gap between all rows and columns. Should be used with a helper method like `Style.px(10)`

    """

    grid_template_areas: list[list[str]]
    grid_auto_columns: str | None = None
    grid_template_columns: list[str] | None = None
    grid_auto_rows: str = Style.MIN_CONTENT
    grid_template_rows: list[str] | None = None

    sections: list[Section] = field(default_factory=list)
    inlines: list[Inline] = field(default_factory=list)

    gap: str = Style.px(10)
    row_gap: str | None = None
    column_gap: str | None = None

    def serialize(self, key_prefix: str | None = None) -> SerializedLayout:
        """Serializes this `Layout`
        Attributes:
            key_prefix(Optional): if specified, append a prefix to underlying inlines key
        Returns:
            A dictionairy containing all serialized fields

        """
        serialized_layout = {
            "gridTemplateAreas": " ".join([f"'{' '.join(row)}'" for row in self.grid_template_areas]),
            "sections": [section.serialize(key_prefix=key_prefix) for section in self.sections],
            "inlines": [inline.serialize(key_prefix=key_prefix) for inline in self.inlines],
            "gap": self.gap,
        }

        if self.row_gap:
            serialized_layout["rowGap"] = self.row_gap

        if self.column_gap:
            serialized_layout["columnGap"] = self.column_gap

        if self.grid_auto_columns:
            serialized_layout["gridAutoColumns"] = self.grid_auto_columns

        if self.grid_template_columns:
            serialized_layout["gridTemplateColumns"] = grid_definition(*self.grid_template_columns)

        if self.grid_auto_rows:
            serialized_layout["gridAutoRows"] = self.grid_auto_rows

        if self.grid_template_rows:
            serialized_layout["gridTemplateRows"] = grid_definition(*self.grid_template_rows)

        return serialized_layout
