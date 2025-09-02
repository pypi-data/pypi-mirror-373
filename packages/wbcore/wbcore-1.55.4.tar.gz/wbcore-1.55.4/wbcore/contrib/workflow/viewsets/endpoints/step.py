from wbcore.metadata.configs.endpoints import EndpointViewConfig


class StepEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs) -> str:
        if self.view.kwargs.get("workflow_id"):
            return ""
        return super().get_create_endpoint(**kwargs)

    def _get_instance_endpoint(self, **kwargs) -> str:
        return "{{casted_endpoint}}"

    def get_update_endpoint(self, **kwargs):
        if self.view.kwargs.get("workflow_id"):
            return ""
        return super().get_update_endpoint(**kwargs)


class DisplayEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs) -> None:
        return None

    def get_instance_endpoint(self, **kwargs) -> None:
        return None
