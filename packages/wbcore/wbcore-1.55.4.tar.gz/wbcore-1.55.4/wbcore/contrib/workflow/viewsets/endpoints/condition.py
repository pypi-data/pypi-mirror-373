from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ConditionEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs) -> str:
        endpoint: str = super().get_create_endpoint(**kwargs)
        if transition_id := self.view.kwargs.get("transition_id"):
            endpoint += f"?transition={transition_id}"
        return endpoint
