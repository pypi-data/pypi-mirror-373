from dynamic_preferences.registries import global_preferences_registry


def get_timedelta_import_currency_fx_rates():
    return global_preferences_registry.manager()["currency__timedelta_import_currency_fx_rates"]
