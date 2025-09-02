from wbcore.metadata.configs.endpoints import EndpointViewConfig


class UserActivityModelEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class UserActivityUserModelEndpointConfig(UserActivityModelEndpointConfig):
    pass


class UserActivityTableEndpointConfig(UserActivityModelEndpointConfig):
    pass
