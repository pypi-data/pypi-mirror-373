import pytest
from django.conf import settings

from wbcore.configs.decorators import register_config
from wbcore.configs.registry import ConfigRegistry
from wbcore.configs.views import ConfigAPIView


def test_registry(config_registry: ConfigRegistry):
    configs = config_registry.get_config_dict()
    assert configs.keys()


def test_release_note_config(config_registry: ConfigRegistry):
    release_notes = config_registry.get_config_dict()["release_notes"]
    assert release_notes["endpoint"]
    assert release_notes["unread_release_notes"]


def test_menu_config(config_registry: ConfigRegistry):
    menu = config_registry.get_config_dict()["menu"]
    assert menu


def test_share_config(config_registry: ConfigRegistry):
    share = config_registry.get_config_dict()["share"]
    assert share


def test_markdown_config(config_registry: ConfigRegistry):
    markdown = config_registry.get_config_dict()["markdown"]
    assert markdown["blockdiag"]


def test_menu_calendar_config(config_registry: ConfigRegistry):
    menu_calendar = config_registry.get_config_dict()["menu_calendar"]
    assert menu_calendar


@pytest.mark.parametrize("text, version", [("Foo bar", "Foo")])
def test_beta_button_config(config_registry: ConfigRegistry, text, version):
    settings.BETA_BUTTON_VERSION = version
    settings.BETA_BUTTON_TEXT = text
    beta_calendar = config_registry.get_config_dict()["beta_button"]
    assert beta_calendar["url"] == f"{settings.CDN_BASE_ENDPOINT_URL}/{version}/main.js"
    assert beta_calendar["text"] == text


def test_config_registry_decorator():
    def some_callable():
        pass

    assert not hasattr(some_callable, "_is_config")
    some_callable = register_config(some_callable)
    assert getattr(some_callable, "_is_config")


def test_config_view(rf):
    request = rf.get("/")
    view = ConfigAPIView.as_view()
    response = view(request)

    assert response.status_code == 200
