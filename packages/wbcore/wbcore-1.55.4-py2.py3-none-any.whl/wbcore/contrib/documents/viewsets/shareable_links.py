import json
from datetime import datetime
from uuid import UUID

from django.db.models import Q
from django.http.request import HttpRequest
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from wbcore import viewsets
from wbcore.contrib.documents.filters import (
    ShareableLinkAccessFilter,
    ShareableLinkFilter,
)
from wbcore.contrib.documents.models import ShareableLink, ShareableLinkAccess
from wbcore.contrib.documents.serializers import (
    ShareableLinkAccessModelSerializer,
    ShareableLinkAccessRepresentationSerializer,
    ShareableLinkModelSerializer,
    ShareableLinkRepresentationSerializer,
)
from wbcore.contrib.documents.viewsets.buttons import ShareableLinkModelButtonConfig
from wbcore.contrib.documents.viewsets.display import (
    ShareableLinkAccessModelDisplay,
    ShareableLinkModelDisplay,
)
from wbcore.contrib.documents.viewsets.endpoints import (
    ShareableLinkAccessEndpointConfig,
    ShareableLinkEndpointConfig,
)
from wbcore.contrib.documents.viewsets.titles import ShareableLinkModelTitleConfig


class DownloadShareableLinkView(View):
    def get(self, request: HttpRequest, uuid: UUID) -> HttpResponse:
        link = get_object_or_404(ShareableLink, uuid=uuid)
        if link.is_valid() and link.document.file.name:
            json_meta = json.loads(json.dumps(request.META, default=str))
            link.access(metadata=json_meta)
            if (content_type := link.document.content_type) and (filename := link.document.filename):
                with link.document.file.open("r") as f:
                    return FileResponse(f, as_attachment=True, filename=filename, content_type=content_type)
        return HttpResponse("Link invalid", status=status.HTTP_204_NO_CONTENT)


class ShareableLinkModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "documents/markdown/documentation/shareablelink.md"
    search_fields = ("uuid",)
    ordering = ["valid_until"]
    ordering_fields = (
        "valid_until",
        "one_time_link",
    )
    queryset = ShareableLink.objects.all()
    serializer_class = ShareableLinkModelSerializer
    title_config_class = ShareableLinkModelTitleConfig
    filterset_class = ShareableLinkFilter
    endpoint_config_class = ShareableLinkEndpointConfig
    button_config_class = ShareableLinkModelButtonConfig
    display_config_class = ShareableLinkModelDisplay

    @action(detail=True, methods=["PATCH"])
    def invalidate(self, request, pk=None):
        shareable_link = ShareableLink.objects.get(pk=pk)
        if shareable_link.manual_invalid:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        shareable_link.manual_invalid = True
        shareable_link.save()
        return Response({}, status=status.HTTP_200_OK)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                valid=Q(manual_invalid=False) & (Q(valid_until__isnull=True) | Q(valid_until__gte=datetime.now()))
            )
        )


class ShareableLinkRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = ShareableLinkRepresentationSerializer
    queryset = ShareableLink.objects.all()
    search_fields = ("document",)


class ShareableLinkAccessModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "documents/markdown/documentation/shareablelinkaccess.md"
    ordering = ["accessed"]
    ordering_fields = (
        "ipaddress",
        "metadata",
        "accessed",
    )
    queryset = ShareableLinkAccess.objects.all()
    serializer_class = ShareableLinkAccessModelSerializer
    endpoint_config_class = ShareableLinkAccessEndpointConfig
    filterset_class = ShareableLinkAccessFilter

    display_config_class = ShareableLinkAccessModelDisplay


class ShareableLinkAccessRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = ShareableLinkAccess.objects.all()
    serializer_class = ShareableLinkAccessRepresentationSerializer
    search_fields = ("ipaddress",)
