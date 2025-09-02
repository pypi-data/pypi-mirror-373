from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView

from .hashes import get_hash_from_user


class GleapUserIdentityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(
            (
                str(request.user.id),
                {"email": request.user.email, "name": request.user.get_full_name()},
                get_hash_from_user(request.user.id, settings.GLEAP_IDENTITY_VERIFICATION_SECRET),
            )
        )


class GleapAPITokenAPIView(APIView):
    permission_classes = []

    def get(self, request: Request) -> Response:
        try:
            return Response({"api_token": settings.GLEAP_API_TOKEN})
        except AttributeError:
            return Response({"error": "Gleap is not setup for this server"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
