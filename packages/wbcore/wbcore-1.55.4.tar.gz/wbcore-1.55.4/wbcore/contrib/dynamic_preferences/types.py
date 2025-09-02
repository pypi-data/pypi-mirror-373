from django.forms import fields as form_fields
from dynamic_preferences.types import BooleanPreference as BaseBooleanPreference
from dynamic_preferences.types import ChoicePreference as BaseChoicePreference
from dynamic_preferences.types import DatePreference as BaseDatePreference
from dynamic_preferences.types import DateTimePreference as BaseDateTimePreference
from dynamic_preferences.types import DecimalPreference as BaseDecimalPreference
from dynamic_preferences.types import DurationPreference as BaseDurationPreference
from dynamic_preferences.types import FilePreference as BaseFilePreference
from dynamic_preferences.types import FloatPreference as BaseFloatPreference
from dynamic_preferences.types import IntegerPreference as BaseIntegerPreference
from dynamic_preferences.types import LongStringPreference as BaseLongStringPreference
from dynamic_preferences.types import ModelChoicePreference
from dynamic_preferences.types import MultipleChoicePreference as BaseMultipleChoicePreference
from dynamic_preferences.types import StringPreference as BaseStringPreference
from dynamic_preferences.types import TimePreference as BaseTimePreference

from wbcore.serializers import fields
from wbcore.serializers.fields import LanguageChoiceField

FIELD_MAPPING = {
    form_fields.BooleanField: fields.BooleanField,
    form_fields.IntegerField: fields.IntegerField,
    form_fields.FloatField: fields.FloatField,
    form_fields.DecimalField: fields.DecimalField,
    form_fields.CharField: fields.CharField,
    form_fields.ChoiceField: fields.ChoiceField,
    form_fields.FileField: fields.FileField,
    form_fields.DurationField: fields.DurationField,
    form_fields.DateField: fields.DateField,
    form_fields.DateTimeField: fields.DateTimeField,
    form_fields.TimeField: fields.TimeField,
    form_fields.MultipleChoiceField: fields.MultipleChoiceField,
}


class PreferenceMixin:
    weight: int = 0

    def get_api_additional_data(self):
        return {}

    def get_api_field_data(self):
        field_class = FIELD_MAPPING[self.field_class]
        kwargs = self.get_field_kwargs()
        del kwargs["widget"]
        rep = field_class(**kwargs, default=kwargs.get("initial")).get_representation(None, self.name)[1]
        rep["required"] = True
        return rep


class BooleanPreference(PreferenceMixin, BaseBooleanPreference):
    pass


class IntegerPreference(PreferenceMixin, BaseIntegerPreference):
    pass


class DecimalPreference(PreferenceMixin, BaseDecimalPreference):
    pass


class FloatPreference(PreferenceMixin, BaseFloatPreference):
    pass


class StringPreference(PreferenceMixin, BaseStringPreference):
    pass


class LongStringPreference(PreferenceMixin, BaseLongStringPreference):
    pass


class ChoicePreference(PreferenceMixin, BaseChoicePreference):
    pass


class FilePreference(PreferenceMixin, BaseFilePreference):
    pass


class DurationPreference(PreferenceMixin, BaseDurationPreference):
    pass


class DatePreference(PreferenceMixin, BaseDatePreference):
    pass


class DateTimePreference(PreferenceMixin, BaseDateTimePreference):
    pass


class TimePreference(PreferenceMixin, BaseTimePreference):
    pass


class MultipleChoicePreference(PreferenceMixin, BaseMultipleChoicePreference):
    pass


class LanguageChoicePreference(PreferenceMixin, BaseChoicePreference):
    def get_api_field_data(self):
        kwargs = self.get_field_kwargs()
        del kwargs["widget"]
        rep = LanguageChoiceField(**kwargs, default=kwargs.get("initial")).get_representation(None, self.name)[1]
        rep["required"] = True
        return rep


class CallableDefaultModelChoicePreference(ModelChoicePreference):
    """
    Propose a ModelChoicePreference class where default is allowed to be a callable property. This avoids unnecessary db calls at start

    This type expects a mandatory model attribute and a section of type dynamic_preferences.Section.
    """

    def __init__(self, registry=None):
        self.registry = registry
        self.queryset = self.model.objects.all()
        self.serializer = self.serializer_class(self.model)
        self._setup_signals()

    @property
    def default(self):
        raise NotImplementedError("Default property needs to be defined for this preference type")
