from wbcore.metadata.configs.display.instance_display.layouts.layouts import Layout


class TestLayout:
    def test_minimal_init(self):
        assert Layout([[]]) is not None

    def test_minimal_serialize(self):
        assert Layout([[]]).serialize() == {
            "gridTemplateAreas": "''",
            "sections": [],
            "inlines": [],
            "gap": "10px",
            "gridAutoRows": "min-content",
        }
