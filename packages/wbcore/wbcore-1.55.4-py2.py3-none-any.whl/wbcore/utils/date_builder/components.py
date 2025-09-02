class Component:
    _name: str

    def __init__(self, _name: str | None = None):
        if _name:
            self._name = _name

    def arithmetic(self, other, operator) -> "Component":
        return Component(_name=f"{self.name}{operator}{other.name}")

    def __sub__(self, other) -> "Component":
        return self.arithmetic(other, "-")

    def __add__(self, other) -> "Component":
        return self.arithmetic(other, "+")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        return self._name


Now = Component("now")
SecondStart = Component("second_start")
SecondEnd = Component("second_end")
MinuteStart = Component("minute_start")
MinuteEnd = Component("minute_end")
HourStart = Component("hour_start")
HourEnd = Component("hour_end")
WeekStart = Component("week_start")
WeekEnd = Component("week_end")
MonthStart = Component("month_start")
MonthEnd = Component("month_end")
QuarterStart = Component("quarter_start")
QuarterEnd = Component("quarter_end")
YearStart = Component("year_start")
YearEnd = Component("year_end")
