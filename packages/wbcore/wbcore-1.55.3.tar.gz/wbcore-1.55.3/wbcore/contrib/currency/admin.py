from typing import Any

from django.contrib import admin
from dynamic_preferences.registries import global_preferences_registry

from wbcore.contrib.io.admin import ProviderGenericInline

from .models import Currency, CurrencyFXRates


@admin.register(Currency)
class CurrencyModelAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "title",
    )
    search_fields = ("key", "title", "symbol")
    raw_id_fields = ["import_source"]

    def refetch_import_data(self: Any, request: Any, queryset: Any) -> Any:
        default_start_date = global_preferences_registry.manager()["currency__default_start_date_historical_import"]
        CurrencyFXRates.import_data(start=default_start_date, queryset=queryset)

    actions = [refetch_import_data]
    inlines = [ProviderGenericInline]


@admin.register(CurrencyFXRates)
class CurrencyFXRatesModelAdmin(admin.ModelAdmin):
    list_display = ("currency", "date", "value")
    search_fields = ("currency__key", "currency__title", "currency__symbol")
    list_filter = ["currency"]
    raw_id_fields = ["import_source"]
