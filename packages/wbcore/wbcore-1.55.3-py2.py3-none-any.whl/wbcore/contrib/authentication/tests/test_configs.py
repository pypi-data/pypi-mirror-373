from wbcore.configs.registry import ConfigRegistry


def test_authentication_config(config_registry: ConfigRegistry):
    authentication = config_registry.get_config_dict()["authentication"]
    assert authentication
