from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]

    @classmethod
    def model_choices(cls):
        return [(choice.value, choice.value) for choice in cls]

    @classmethod
    def names(cls):
        return [choice.name for choice in cls]

    @classmethod
    def values(cls):
        return [choice.value for choice in cls]

    @classmethod
    def to_dict(cls):
        return {choice.name: choice.value for choice in cls}
