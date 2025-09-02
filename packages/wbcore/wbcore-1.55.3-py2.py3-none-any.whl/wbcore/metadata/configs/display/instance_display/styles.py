class Style:
    """A convinience class to have all styles and helper methods contained in one place.

    Static CSS Variables may be used as classmembers, e.g.: `Style.MIN_CONTENT` or `Style.AUTO`
    Dynamic CSS Variables, such as specific sizes, may be used as static methods, e.g.: `Style.fr(5)`
    """

    MIN_CONTENT = "min-content"
    MAX_CONTENT = "max-content"
    AUTO = "auto"

    @staticmethod
    def fr(fractions: int) -> str:
        return Style._stringify(fractions, "fr")

    @staticmethod
    def px(pixels: int) -> str:
        return Style._stringify(pixels, "px")

    @staticmethod
    def pct(percent: float) -> str:
        return Style._stringify(percent, "%")

    @staticmethod
    def rem(rem: float) -> str:
        return Style._stringify(rem, "rem")

    @staticmethod
    def vh(vh: int) -> str:
        return Style._stringify(vh, "vh")

    @staticmethod
    def vw(vw: int) -> str:
        return Style._stringify(vw, "vw")

    @staticmethod
    def _stringify(value: int | float, unit: str) -> str:
        return f"{value}{unit}"

    @staticmethod
    def minmax(min_value: str, max_value: str) -> str:
        return f"minmax({min_value}, {max_value})"
