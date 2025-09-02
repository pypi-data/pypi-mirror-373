from django.urls import include, path

from wbcore.routers import WBCoreRouter

from .viewsets import viewsets

router = WBCoreRouter()
router.register(r"tagrepresentation", viewsets.TagRepresentationViewSet, basename="tagrepresentation")
router.register(r"tag", viewsets.TagModelViewSet, basename="tag")
router.register(r"taggrouprepresentation", viewsets.TagGroupRepresentationViewSet, basename="taggrouprepresentation")
router.register(r"taggroup", viewsets.TagGroupModelViewSet, basename="taggroup")

group_router = WBCoreRouter()
group_router.register(r"tag", viewsets.TagTagGroupModelViewSet, basename="group-tag")
urlpatterns = [path("", include(router.urls)), path("group/<int:group_id>/", include(group_router.urls))]
