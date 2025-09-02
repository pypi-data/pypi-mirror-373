from django.db.models.query import QuerySet
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from wbcore import viewsets
from wbcore.contrib.notifications.models import Notification
from wbcore.contrib.notifications.serializers import NotificationModelSerializer
from wbcore.contrib.notifications.viewsets.configs.notifications import (
    NotificationButtonConfig,
    NotificationDisplayConfig,
)


class NotificationModelViewSet(viewsets.ModelViewSet):
    ordering = ("-created",)
    search_fields = ("title", "notification_type__title")

    queryset = Notification.objects.all()

    serializer_class = NotificationModelSerializer
    display_config_class = NotificationDisplayConfig
    button_config_class = NotificationButtonConfig

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        obj = self.get_object()
        if not obj.read:
            obj.read = timezone.now()
            obj.save()
        return super().retrieve(request, *args, **kwargs)

    def create(self, request: Request) -> Response:
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request: Request, pk=None) -> Response:
        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request: Request, pk=None) -> Response:
        return Response(status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self) -> QuerySet[Notification]:
        return super().get_queryset().filter(user=self.request.user)

    @action(methods=["GET"], detail=False)
    def unread_count(self, request, pk=None):
        return Response({"count": Notification.objects.filter(user=request.user, read__isnull=True).count()})

    @action(methods=["PATCH"], detail=False)
    def read_all(self, request: Request, pk=None) -> Response:
        self.get_queryset().filter(read__isnull=True).update(read=timezone.now())
        return Response({})

    @action(methods=["PATCH"], detail=False)
    def delete_all_read(self, request: Request, pk=None) -> Response:
        self.get_queryset().filter(read__isnull=False).delete()
        return Response({})
