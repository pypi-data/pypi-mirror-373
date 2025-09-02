from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class Profile(APIView):
    """Profile view to get the default user name, email and profile

    This view should be substituted by one from the authentication module
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(
            {
                "config": reverse("wbcore:frontenduserconfiguration-list", request=request),
                "name": import_string(settings.WBCORE_DEFAULT_USER_NAME)(request.user),
                "email": request.user.email,
                "profile": import_string(settings.WBCORE_PROFILE)(request),
            }
        )
