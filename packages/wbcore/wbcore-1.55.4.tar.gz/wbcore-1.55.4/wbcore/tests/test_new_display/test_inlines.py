from wbcore.metadata.configs.display.instance_display.layouts.inlines import Inline


class TestInline:
    def test_init(self):
        inline = Inline(key="key", endpoint="endpoint")
        assert inline is not None

    def test_serialize(self):
        inline = Inline(key="key", endpoint="endpoint")
        assert inline.serialize() == {"key": "key", "endpoint": "endpoint", "hide_controls": False}

    # TODO: Test with display
