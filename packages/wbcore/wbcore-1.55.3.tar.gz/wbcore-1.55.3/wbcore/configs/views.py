from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from wbcore.configs.registry import ConfigRegistry


class ConfigAPIView(APIView):
    permission_classes = []

    def get(self, request: Request) -> Response:
        return Response(ConfigRegistry(request=request).get_config_dict())
