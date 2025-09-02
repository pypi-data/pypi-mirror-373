from wbcore.metadata.configs.titles import TitleViewConfig


class GeographyTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Geographies"

    def get_create_title(self):
        return "New Geography"

    def get_instance_title(self):
        if "pk" in self.view.kwargs:
            return f"Geography: {self.view.get_object()}"
        return "Geography"
