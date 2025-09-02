from .base import WBCoreViewConfig


class TitleViewConfig(WBCoreViewConfig):
    metadata_key = "titles"
    config_class_attribute = "title_config_class"

    # TODO: get_instance_title should only really ever be called if we are displaying an instance:
    # self.instance should always be True
    def get_instance_title(self) -> str | None:
        if (model := self.view.get_model()) and hasattr(self.view, "get_object"):
            name = model._meta.verbose_name  # type: ignore

            if self.instance:
                return f"{name}: {str(self.view.get_object())}"  # type: ignore
            return name
        return None

    def get_delete_title(self) -> str | None:
        if (model := self.view.get_model()) and hasattr(self.view, "get_object"):
            name = model._meta.verbose_name  # type: ignore

            if self.instance:
                return f"Delete {name}: {str(self.view.get_object())}"  # type: ignore
            return f"Delete {name}"
        return None

    def get_list_title(self) -> str | None:
        if model := self.view.get_model():
            return model._meta.verbose_name_plural  # type: ignore
        return None

    def get_create_title(self) -> str | None:
        if model := self.view.get_model():
            return f"Create {model._meta.verbose_name}"  # type: ignore
        return None

    # TODO: Rethink this strategy:
    # /<model>/ -> list endpoint, instance is not needed?
    # /<model>/<pk>/ -> instance endpoint, list is not needed?
    # /<model>/?new_mode=true -> only return create?
    def get_metadata(self) -> dict[str, str | None]:
        return {
            "instance": self.get_instance_title(),
            "list": self.get_list_title(),
            "create": self.get_create_title(),
            "delete": self.get_delete_title(),
        }
