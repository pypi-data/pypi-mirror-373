from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ProcessEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs) -> None:
        return None


class AssignedProcessStepEndpointConfig(ProcessEndpointConfig):
    def _get_instance_endpoint(self, **kwargs) -> str:
        return "{{instance_endpoint}}"
