from django.urls import include, path

from wbcore.routers import WBCoreRouter

from .viewsets import GeographyModelViewSet, GeographyRepresentationViewSet

router = WBCoreRouter()
router.register(r"geographyrepresentation", GeographyRepresentationViewSet, basename="geographyrepresentation")
router.register(r"geography", GeographyModelViewSet, basename="geography")

urlpatterns = [
    path("", include(router.urls)),
]
