from wbcore.metadata.configs.display.list_display import (
    ListDisplay,
    TreeGroupLevelOption,
)


def test_tree_group_open_level_list_display():
    ld = dict(
        ListDisplay(
            fields=[],
            tree=True,
            tree_group_field="field",
            tree_group_open_level=3,
            tree_group_level_options=[TreeGroupLevelOption(list_endpoint="endpoint")],
        )
    )
    assert ld["tree_group"]["open_level"] == 3


def test_not_tree_group_open_level_list_display():
    ld = dict(
        ListDisplay(
            fields=[],
            tree=False,
            tree_group_field="field",
            tree_group_open_level=3,
        )
    )
    assert "tree_group" not in ld
