from wbcore.metadata.configs.endpoints import EndpointViewConfig


class DataEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs) -> str:
        endpoint: str = super().get_create_endpoint(**kwargs)
        if workflow_id := self.view.kwargs.get("workflow_id"):
            endpoint += f"?workflow={workflow_id}"
        return endpoint
