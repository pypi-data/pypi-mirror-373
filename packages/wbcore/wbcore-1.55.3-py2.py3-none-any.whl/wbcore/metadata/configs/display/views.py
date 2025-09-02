from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from .models import AppliedPreset


class PresetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, display_identifier_path: str) -> Response:
        preset = get_object_or_404(
            AppliedPreset,
            display_identifier_path=display_identifier_path,
            user=request.user,
        )

        return Response(preset.display, status=HTTP_200_OK)

    def delete(self, request: Request, display_identifier_path: str) -> Response:
        preset = get_object_or_404(
            AppliedPreset,
            display_identifier_path=display_identifier_path,
            user=request.user,
        )

        preset.delete()

        return Response(status=HTTP_204_NO_CONTENT)

    def post(self, request: Request, display_identifier_path: str) -> Response:
        defaults = {}

        if display := self.request.data.get("display", None):
            defaults["display"] = display

        if preset := self.request.data.get("preset", None):
            defaults["preset"] = preset

        AppliedPreset.objects.update_or_create(
            user=request.user,
            display_identifier_path=display_identifier_path,
            defaults=defaults,
        )
        return Response(status=HTTP_201_CREATED)
