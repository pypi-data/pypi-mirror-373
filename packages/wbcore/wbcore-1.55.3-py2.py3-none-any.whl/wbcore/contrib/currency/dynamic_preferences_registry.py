from datetime import date

from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import (
    DatePreference,
    IntegerPreference,
    StringPreference,
)

currency_section = Section("currency")


@global_preferences_registry.register
class DefaultCurrency(StringPreference):
    section = currency_section
    name = "default_currency"
    default = "USD"

    verbose_name = "Default Currency Used"


@global_preferences_registry.register
class DefaultStartDateHistoricalImport(DatePreference):
    section = currency_section
    name = "default_start_date_historical_import"
    default = date(2000, 1, 1)

    verbose_name = "Default Start Date"
    help_text = "Default start date in historical import"


@global_preferences_registry.register
class TimedeltaImportCurrencyFXRate(IntegerPreference):
    section = currency_section
    name = "timedelta_import_currency_fx_rates"
    default = 2

    verbose_name = "The Timedelta for the currency rate import windows"
