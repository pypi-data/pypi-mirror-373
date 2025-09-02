from dataclasses import dataclass

from wbcore.enums import Operator


@dataclass(unsafe_hash=True)
class Condition:
    operator: Operator
    value: str | float | int | bool

    def __post_init__(self) -> None:
        if self.operator == Operator.EXISTS:
            assert isinstance(self.value, bool), f"{Operator.EXISTS.value} is only compatible with bool"


@dataclass(unsafe_hash=True)
class FormattingRule:
    style: dict | None = None
    condition: Condition | tuple | list[tuple] | None = None

    def __post_init__(self) -> None:
        assert self.style, "style cannot both be None."

    def __iter__(self):
        yield "style", self.style
        if self.condition:
            if isinstance(self.condition, tuple):
                yield "condition", self.condition
            elif isinstance(self.condition, list):
                yield "condition", [tuple(cond) for cond in self.condition]
            else:
                yield "condition", (self.condition.operator.value, self.condition.value)


@dataclass(unsafe_hash=True)
class Formatting:
    formatting_rules: list[FormattingRule]
    column: str | None = None

    def __post_init__(self) -> None:
        if self.column is None:
            assert all(
                [not bool(rule.condition) for rule in self.formatting_rules]
            ), "Specifying conditions, without a reference column is not possible."

    def __iter__(self):
        yield "column", self.column
        yield "formatting_rules", [dict(rule) for rule in self.formatting_rules]
