from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
    create_simple_section,
)


def test_create_simple_display():
    assert create_simple_display([["field1", "field2"], ["field3", "field4"]]).serialize() == {
        "navigationType": "tab",
        "pages": [
            {
                "layouts": {
                    "default": {
                        "gridTemplateAreas": "'field1 field2' 'field3 field4'",
                        "inlines": [],
                        "sections": [],
                        "gap": "10px",
                        "gridAutoColumns": "1fr",
                        "gridAutoRows": "min-content",
                    }
                },
                "title": None,
            }
        ],
    }


def test_create_simple_section():
    section = create_simple_section(
        key="key", title="title", grid_template_areas=[["field1", "field2"]], inline_key="field1", collapsible=False
    ).serialize()
    assert section["key"] == "key"
    assert section["title"] == "title"
    assert section["display"]["pages"][0]["layouts"]["default"]["gridTemplateAreas"] == "'field1 field2'"  # type: ignore
    assert section["display"]["pages"][0]["layouts"]["default"]["inlines"] == (  # type: ignore
        [{"key": "field1", "endpoint": "field1", "hide_controls": False}]
    )
    assert not section["collapsible"]
