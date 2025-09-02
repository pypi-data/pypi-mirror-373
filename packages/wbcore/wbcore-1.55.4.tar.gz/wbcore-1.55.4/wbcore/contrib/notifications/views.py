from django.conf import settings
from django.contrib.staticfiles import finders
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from wbcore.contrib.notifications.models.tokens import NotificationUserToken


class NotificationTokenAPIView(APIView):
    """An APIView that returns the configuration needed for a frontend to generate a token and to upload said token"""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(import_string(settings.NOTIFICATION_BACKEND).get_configuration())

    def post(self, request: Request) -> Response:
        try:
            token: str = request.data["token"]  # type: ignore

            existing_instance = NotificationUserToken.objects.filter(
                user=request.user,
                token__startswith=token.split(":")[0],
            )

            if existing_instance.exists():
                existing_instance.update(token=token)
            else:
                NotificationUserToken.objects.create(
                    user=request.user,
                    token=token,
                    device_type=request.data["device_type"],  # type: ignore
                )
            return Response({}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({}, status=status.HTTP_200_OK)
        except KeyError:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request) -> Response:
        queryset = NotificationUserToken.objects.filter(user=request.user)

        if device_type := request.GET.get("device_type", None):  # type: ignore
            queryset = queryset.filter(device_type=device_type)

        queryset.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


def service_worker_view(request, service_worker_name: str | None = None):
    file_path = finders.find(f"notifications/{service_worker_name}")
    if file_path:
        with open(file_path) as f:
            response = HttpResponse(content=f.read(), content_type="application/javascript")
            response.headers["Service-Worker-Allowed"] = "../" * ((request.get_full_path()).count("/") - 1)
            return response
    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
