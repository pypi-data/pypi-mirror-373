from wbcore.metadata.configs.display.instance_display import operators as op
from wbcore.metadata.configs.display.instance_display.layouts.layouts import Layout
from wbcore.metadata.configs.display.instance_display.pages import Page


class TestPage:
    def test_init(self):
        assert Page(layouts={op.default(): Layout([[]])}) is not None
