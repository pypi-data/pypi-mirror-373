from .components import Component


class Offset(Component):
    name_part: str

    def __init__(self, name_part: str, amount: int = 1):
        self.name_part = name_part
        self.amount = amount

    def __call__(self, amount: int) -> "Offset":
        return self.__class__(self.name_part, amount)

    @property
    def name(self) -> str:
        return f"{self.amount}{self.name_part}"


Second = Offset("seconds")
Minute = Offset("minutes")
Hour = Offset("hours")
Day = Offset("days")
BusinessDay = Offset("bdays")
Week = Offset("weeks")
Month = Offset("months")
Quarter = Offset("quarters")
Year = Offset("years")
