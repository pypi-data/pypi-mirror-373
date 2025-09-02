from wbcore.contrib.currency.models import Currency
from wbcore.metadata.configs.titles import TitleViewConfig


class CurrencyFXRatesCurrencyTitleConfig(TitleViewConfig):
    def get_list_title(self):
        currency = Currency.objects.get(id=self.view.kwargs["currency_id"])
        return f"Rates for {currency.key} ({currency.symbol})"
