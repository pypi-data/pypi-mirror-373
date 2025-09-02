from wbcore.configs.registry import ConfigRegistry


def test_profile_config(config_registry: ConfigRegistry):
    profile = config_registry.get_config_dict()["profile"]
    assert profile
