from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from wbcore.shares.signals import handle_widget_sharing
from wbcore.utils.urls import clean_shareable_url

from .sites import share_site


class ShareAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        if widget_endpoint := request.POST.get("widget_endpoint"):
            serializer = share_site.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            handle_widget_sharing.send(
                sender=self.__class__,
                request=request,
                widget_relative_endpoint=clean_shareable_url(widget_endpoint),
                **serializer.validated_data.copy(),
            )
        return Response({})
