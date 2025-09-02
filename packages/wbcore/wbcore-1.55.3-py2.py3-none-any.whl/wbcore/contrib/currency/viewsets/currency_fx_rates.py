from rest_framework import filters

from wbcore import viewsets
from wbcore.filters import DjangoFilterBackend

from ..models import CurrencyFXRates
from ..serializers import CurrencyFXRatesModelSerializer
from .display import CurrencyFXRatesCurrencyDisplayConfig
from .endpoints import CurrencyFXRatesCurrencyEndpointConfig
from .titles import CurrencyFXRatesCurrencyTitleConfig


class CurrencyFXRatesCurrencyModelViewSet(viewsets.ModelViewSet):
    display_config_class = CurrencyFXRatesCurrencyDisplayConfig
    endpoint_config_class = CurrencyFXRatesCurrencyEndpointConfig
    title_config_class = CurrencyFXRatesCurrencyTitleConfig

    serializer_class = CurrencyFXRatesModelSerializer
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)

    ordering = ordering_fields = ["-date"]

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    queryset = CurrencyFXRates.objects.all()

    filterset_fields = {"date": ["gte", "exact", "lte"], "value": ["gte", "exact", "lte"]}
    ordering_fields = ("date", "value")

    ordering = ["-date"]

    def get_queryset(self):
        _id = self.kwargs["currency_id"]
        return CurrencyFXRates.objects.filter(currency__id=_id).all()
