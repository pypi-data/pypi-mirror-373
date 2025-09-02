from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from wbcore import viewsets
from wbcore.contrib.i18n.translation import translate_model_as_task


class ModelTranslateMixin(viewsets.ModelViewSet):
    @action(methods=["POST"], detail=True)
    def auto_translate(self, request: Request, *args, **kwargs):
        """Initiates an asynchronous translation task for the specified model instance.

        This method retrieves the model instance based on the provided URL parameters,
        starts a background translation task, and returns a notification response.

        Args:
            request (Request): The HTTP request object containing the data for the translation.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            override_existing_data (bool): If True, existing content will not be overridden.

        Returns:
            Response: A response indicating the status of the translation initiation.
        """
        override_existing_data = request.data.get("override_existing_data", "false") == "true"

        obj = self.get_object()
        if obj:
            ct = ContentType.objects.get_for_model(obj)  # type: ignore
            translate_model_as_task.delay(ct.id, obj.id, override_existing_data)
            return Response({"__notification": "The translation started in the background."})

        return Response({"non_field_errors": ["The URL was malformatted."]}, status=status.HTTP_400_BAD_REQUEST)
