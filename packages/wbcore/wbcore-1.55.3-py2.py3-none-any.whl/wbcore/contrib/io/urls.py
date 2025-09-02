from django.urls import include, path

from wbcore.routers import WBCoreRouter

from . import viewsets

router = WBCoreRouter()

# Representation viewsets
router.register(r"sourcerepresentation", viewsets.SourceRepresentationViewSet, basename="sourcerepresentation")
router.register(
    r"importsourcerepresentation", viewsets.ImportSourceRepresentationViewSet, basename="importsourcerepresentation"
)
router.register(
    r"parserhandlerrepresentation", viewsets.ParserHandlerRepresentationViewSet, basename="parserhandlerrepresentation"
)
router.register(
    r"databackendrepresentation", viewsets.DataBackendRepresentationViewSet, basename="databackendrepresentation"
)

# Models viewsets
router.register(r"parserhandler", viewsets.ParserHandlerModelViewSet, basename="parserhandler")
router.register(r"importsource", viewsets.ImportSourceModelViewSet, basename="importsource")
router.register(r"source", viewsets.SourceModelViewSet, basename="source")


urlpatterns = [
    path("", include(router.urls)),
]
