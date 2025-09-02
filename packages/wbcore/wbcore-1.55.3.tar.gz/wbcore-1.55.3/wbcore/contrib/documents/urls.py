from django.urls import include, path

from wbcore.routers import WBCoreRouter

from . import viewsets

router = WBCoreRouter()

router.register(r"document", viewsets.DocumentModelViewSet, basename="document")
router.register(r"documenttype", viewsets.DocumentTypeModelViewSet, basename="documenttype")
router.register(r"link", viewsets.ShareableLinkModelViewSet, basename="link")
router.register(r"linkaccess", viewsets.ShareableLinkAccessModelViewSet, basename="linkaccess")
router.register(
    r"documentmodelrelationship", viewsets.DocumentModelRelationshipModelViewSet, basename="documentmodelrelationship"
)

# Representations
router.register(r"documentrepresentation", viewsets.DocumentRepresentationViewSet, basename="documentrepresentation")
router.register(
    r"documenttyperepresentation", viewsets.DocumentTypeRepresentationViewSet, basename="documenttyperepresentation"
)
router.register(r"linkrepresentation", viewsets.ShareableLinkRepresentationViewSet, basename="linkrepresentation")
router.register(
    r"linkaccessrepresentation", viewsets.ShareableLinkAccessRepresentationViewSet, basename="linkaccessrepresentation"
)

document_router = WBCoreRouter()
document_router.register(
    r"documentmodelrelationship",
    viewsets.DocumentModelRelationshipModelViewSet,
    basename="document-documentmodelrelationship",
)

urlpatterns = [
    path("", include(router.urls)),
    path("document/<int:document_id>/", include(document_router.urls)),
    path("download/<uuid:uuid>/", viewsets.DownloadShareableLinkView.as_view(), name="download"),
    path(
        "contentdocument/<int:content_type>/<str:content_id>/",
        viewsets.DocumentModelViewSet.as_view({"get": "list", "post": "create"}),
        name="document_content_object",
    ),
]
