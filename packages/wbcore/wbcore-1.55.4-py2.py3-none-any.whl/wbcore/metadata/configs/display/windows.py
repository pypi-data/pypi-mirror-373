from dataclasses import dataclass


@dataclass
class Window:
    """A window that can specify the minimum and maximum width and height of a window"""

    min_width: int | None = None
    max_width: int | None = None
    min_height: int | None = None
    max_height: int | None = None

    def serialize(self) -> dict[str, int]:
        window = {}

        if self.min_width:
            window["min_width"] = self.min_width

        if self.max_width:
            window["max_width"] = self.max_width

        if self.min_height:
            window["min_height"] = self.min_height

        if self.max_height:
            window["max_height"] = self.max_height

        return window
