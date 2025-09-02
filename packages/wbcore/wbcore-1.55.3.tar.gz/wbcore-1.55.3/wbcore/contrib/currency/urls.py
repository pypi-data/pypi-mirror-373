from django.urls import include, path

from wbcore.routers import WBCoreRouter

from .viewsets import (
    CurrencyFXRatesCurrencyModelViewSet,
    CurrencyModelViewSet,
    CurrencyRepresentationViewSet,
)

router = WBCoreRouter()
router.register(r"currency", CurrencyModelViewSet, basename="currency")
router.register(r"currencyrepresentation", CurrencyRepresentationViewSet, basename="currencyrepresentation")


currency_router = WBCoreRouter()
currency_router.register(r"currencyfxrates", CurrencyFXRatesCurrencyModelViewSet, basename="currency-currencyfxrates")


urlpatterns = [path("", include(router.urls)), path("currency/<int:currency_id>/", include(currency_router.urls))]
