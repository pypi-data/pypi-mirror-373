from django.core.cache import cache
from django.http import HttpRequest
from rest_framework import permissions, status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from wbcore.contrib.authentication.authentication import JWTCookieAuthentication


@api_view(["PATCH"])
@permission_classes([permissions.IsAdminUser])
@authentication_classes([JWTCookieAuthentication])
def clear_cache(request: HttpRequest, cache_key: str, *args, **kwargs):
    cache.delete(cache_key)
    return Response(status=status.HTTP_204_NO_CONTENT)
