import importlib
import sys
from contextlib import suppress

from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .registry import default_registry


class MenuAPIView(APIView):
    @property
    def permission_classes(self):
        wbcore_auth = import_string(settings.WBCORE_DEFAULT_AUTH_CONFIG)(None)

        if wbcore_auth["type"] is None:
            return []

        return [IsAuthenticated]

    def get(self, request: Request) -> Response:
        # Default menu is imported from menu. In case we need multiple menus (or provide a temporary new menu) we can
        # steer this through an optional GET parameter

        mod_name = f"{settings.PROJECT_NAME}.{request.COOKIES.get('menu', 'menu')}"

        default_registry.clear()

        # Trying to import the menu from the project folder (only if it is called config)
        with suppress(ModuleNotFoundError):
            if mod := sys.modules.get(mod_name, None):
                importlib.reload(mod)
            else:
                importlib.import_module(mod_name)

        default_registry.request = request
        return Response(list(default_registry))
