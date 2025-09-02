from wbcore.configs.registry import ConfigRegistry


def test_workflow_config(config_registry: ConfigRegistry):
    workflow = config_registry.get_config_dict()["workflow"]
    assert workflow["endpoint"]
