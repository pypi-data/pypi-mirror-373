from typing import Any

from rest_framework.metadata import BaseMetadata
from rest_framework.request import Request
from rest_framework.views import View

from wbcore.metadata.configs.base import WBCoreViewConfig


class WBCoreMetadata(BaseMetadata):
    """A metadata class for WBCore application views."""

    def determine_metadata(self, request: Request, view: View) -> dict[str, Any]:
        """
        Returns a dictionary containing metadata for the given request and view.

        This method iterates over all the WBCoreViewConfig instances associated
        with the given view and adds their metadata to the returned dictionary.

        Args:
            request (Request): An HTTP request instance.
            view (View): A Django Rest Framework view.

        Returns:
            A dictionary containing metadata for the given request and view.
        """

        metadata = dict()

        for _, config_class in WBCoreViewConfig.get_all_configs(view):
            config = config_class.for_view(view, request)
            metadata[config.metadata_key] = config._get_metadata()

        return metadata
