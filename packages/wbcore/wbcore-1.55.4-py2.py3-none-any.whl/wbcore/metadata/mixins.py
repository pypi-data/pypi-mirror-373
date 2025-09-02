from contextlib import suppress
from typing import Type

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from wbcore.metadata.configs.buttons import ButtonViewConfig
from wbcore.metadata.configs.display import (
    DisplayIdentifierViewConfig,
    DisplayViewConfig,
)
from wbcore.metadata.configs.documentations import DocumentationViewConfig
from wbcore.metadata.configs.endpoints import EndpointViewConfig
from wbcore.metadata.configs.fields import FieldsViewConfig
from wbcore.metadata.configs.filter_fields import FilterFieldsViewConfig
from wbcore.metadata.configs.identifiers import (
    DependantIdentifierViewConfig,
    IdentifierViewConfig,
)
from wbcore.metadata.configs.ordering_fields import OrderingFieldsViewConfig
from wbcore.metadata.configs.paginations import PaginationViewConfig
from wbcore.metadata.configs.preview import PreviewViewConfig
from wbcore.metadata.configs.primary_keys import PrimaryKeyViewConfig
from wbcore.metadata.configs.search_fields import SearchFieldsViewConfig
from wbcore.metadata.configs.titles import TitleViewConfig
from wbcore.metadata.configs.window_types import WindowTypeViewConfig

from .metadata import WBCoreMetadata


class WBCoreMetadataConfigViewMixin(
    FieldsViewConfig.as_view_mixin(),
    DocumentationViewConfig.as_view_mixin(),
    FilterFieldsViewConfig.as_view_mixin(),
    IdentifierViewConfig.as_view_mixin(),
    DependantIdentifierViewConfig.as_view_mixin(),
    PrimaryKeyViewConfig.as_view_mixin(),
    PaginationViewConfig.as_view_mixin(),
    WindowTypeViewConfig.as_view_mixin(),
    SearchFieldsViewConfig.as_view_mixin(),
    TitleViewConfig.as_view_mixin(),
    OrderingFieldsViewConfig.as_view_mixin(),
    EndpointViewConfig.as_view_mixin(),
    ButtonViewConfig.as_view_mixin(),
    DisplayViewConfig.as_view_mixin(),
    PreviewViewConfig.as_view_mixin(),
    DisplayIdentifierViewConfig.as_view_mixin(),
):
    metadata_class = WBCoreMetadata
    WIDGET_TYPE = None
    config_classes = [
        FieldsViewConfig,
        DocumentationViewConfig,
        FilterFieldsViewConfig,
        IdentifierViewConfig,
        DependantIdentifierViewConfig,
        PrimaryKeyViewConfig,
        PaginationViewConfig,
        WindowTypeViewConfig,
        SearchFieldsViewConfig,
        TitleViewConfig,
        OrderingFieldsViewConfig,
        EndpointViewConfig,
        ButtonViewConfig,
        DisplayViewConfig,
        PreviewViewConfig,
        DisplayIdentifierViewConfig,
    ]

    @property
    def new_mode(self):
        return self.request.GET.get("new_mode", "false") == "true" or self.action == "create"

    @property
    def inline(self):
        return self.request.GET.get("inline", "false").lower() == "true"

    def get_ordering_fields(self) -> list[str]:
        return getattr(self, "ordering_fields", [])

    def get_object(self) -> Model | None:
        # we cache the object in this method
        if hasattr(self, "_object"):
            return self._object
        else:
            with suppress(AttributeError):
                self._object = super().get_object()
                return self._object

    @classmethod
    def get_model(cls) -> Type[Model] | None:
        try:
            if hasattr(cls, "queryset") and cls.queryset is not None:
                return cls.queryset.model
            elif hasattr(cls, "serializer_class"):
                return cls.serializer_class.Meta.model
            else:
                return None
        except AttributeError:
            return None

    @classmethod
    def get_content_type(cls) -> ContentType | None:
        if model := cls.get_model():
            return ContentType.objects.get_for_model(model)
        return None
