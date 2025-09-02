from django.urls import include, path

from wbcore.contrib.notifications import viewsets
from wbcore.contrib.notifications.views import (
    NotificationTokenAPIView,
    service_worker_view,
)
from wbcore.routers import WBCoreRouter

router = WBCoreRouter()

router.register("notification", viewsets.NotificationModelViewSet, basename="notification")
router.register(
    "notification_type_representation",
    viewsets.NotificationTypeRepresentationViewSet,
    basename="notification_type_representation",
)
router.register(
    "notification_type_setting", viewsets.NotificationTypeSettingModelViewSet, basename="notification_type_setting"
)


urlpatterns = [
    path("service-worker/<str:service_worker_name>", service_worker_view, name="service-worker"),
    path("token/", NotificationTokenAPIView.as_view(), name="token"),
    path("", include(router.urls)),
]
