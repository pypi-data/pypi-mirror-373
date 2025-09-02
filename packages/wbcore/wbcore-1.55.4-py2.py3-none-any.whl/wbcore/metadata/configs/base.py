from typing import TYPE_CHECKING, Any, Iterable

from django.utils.functional import cached_property
from rest_framework.request import Request
from rest_framework.views import View

if TYPE_CHECKING:
    from wbcore.contrib.authentication.models import User
    from wbcore.contrib.directory.models import Person


class WBCoreViewConfig:
    """A class to configure a View in the WBCore application"""

    metadata_key: str
    config_class_attribute: str

    def __init__(self, view: View, request: Request, instance: bool | None = None):
        """
        Initializes an instance of WBCoreViewConfig.

        Args:
            view (View): A Django Rest Framework view.
            request (Request): An HTTP request instance.
        """
        self.view = view
        self.request = request
        self.instance = instance if instance else "pk" in view.kwargs
        self.new_mode = request.GET.get("new_mode", "false") == "true"

    @cached_property
    def user(self) -> "User":
        return self.request.user

    @cached_property
    def profile(self) -> "Person":
        return self.user.profile

    def get_metadata(self) -> Any:
        raise NotImplementedError()

    def _get_metadata(self) -> Any:
        return self.get_metadata()

    @classmethod
    def get_all_configs(cls, view: View) -> Iterable[tuple[str, "WBCoreViewConfig"]]:
        """
        Returns an iterator of tuples containing all the WBCoreViewConfig
        instances associated with the given view.

        Args:
            view (View): A Django Rest Framework view.

        Returns:
            An iterator of tuples, where each tuple contains a string with the
            name of the configuration attribute and the corresponding
            WBCoreViewConfig instance.
        """
        yield from map(
            lambda c: (c.config_class_attribute, c),
            filter(lambda x: getattr(view, x.config_class_attribute), view.config_classes),
        )

    @classmethod
    def for_view(cls, view: View, request: Request) -> "WBCoreViewConfig":
        """
        Returns the WBCoreViewConfig instance associated with the given view.

        Args:
            view (View): A Django Rest Framework view.
            request (Request): An HTTP request instance.

        Returns:
            The WBCoreViewConfig instance associated with the given view.
        """
        return getattr(view, cls.config_class_attribute)(view, request)

    @classmethod
    def as_view_mixin(cls) -> type:
        """
        Returns a mixin class that adds the configuration attribute to a view.

        Returns:
            A mixin class that adds the configuration attribute to a view.
        """
        return type(f"{cls.__name__}Mixin", (), {cls.config_class_attribute: cls})
