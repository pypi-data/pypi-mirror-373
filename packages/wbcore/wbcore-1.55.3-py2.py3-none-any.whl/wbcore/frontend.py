from copy import copy

from django.conf import settings
from django.urls import path
from django.views.generic import TemplateView


class FrontendView(TemplateView):
    template_name = settings.FRONTEND_TEMPLATE

    def get_context_data(self, **kwargs):
        context = {**super().get_context_data(**kwargs), **copy(settings.FRONTEND_CONTEXT)}
        if version := self.request.GET.get("frontend_version", None):
            base_url = f"{settings.CDN_BASE_ENDPOINT_URL}/{version}/"
            context["JS_RUNTIME_URL"] = f"{base_url}runtime.js"
            context["JS_URL"] = f"{base_url}main.js"
            context["CSS_URL"] = f"{base_url}main.css"
        context["WBCORE_CONTEXT"] = context
        return context

    @classmethod
    def bundled_view(cls, url_path):
        return path(route=url_path, view=cls.as_view(), name="frontend")
