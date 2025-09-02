from typing import Optional

from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Inline,
    Layout,
    Page,
    Section,
    Style,
)
from wbcore.metadata.configs.display.instance_display.operators import default


class WorkflowDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="single_instance_execution", label=_("Single Instance Execution")),
                dp.Field(key="model", label=_("Attached Model")),
                dp.Field(key="status_field", label=_("Model Status Field")),
                dp.Field(key="preserve_instance", label=_("Preserve Instance")),
            ),
        )

    def get_instance_display(self) -> Display:
        model_section = Section(
            key="model_section",
            collapsible=False,
            title=_("Attached Model"),
            display=Display(
                pages=[
                    Page(
                        title=_("Model"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["model", "status_field", "preserve_instance"]],
                                grid_template_columns=[
                                    "minmax(min-content, 2fr)",
                                    "minmax(min-content, 2fr)",
                                    "minmax(min-content, 1.5fr)",
                                    "minmax(min-content, 1.5fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                            )
                        },
                    ),
                ]
            ),
        )
        steps_section = Section(
            key="steps_section",
            collapsible=True,
            title=_("Steps"),
            display=Display(
                pages=[
                    Page(
                        title=_("Steps"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["steps_inline"]],
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="steps_inline", endpoint="steps")],
                            )
                        },
                    ),
                ]
            ),
        )
        transitions_section = Section(
            key="transitions_section",
            collapsible=True,
            title=_("Transitions"),
            display=Display(
                pages=[
                    Page(
                        title=_("Transitions"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["transitions_inline"]],
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="transitions_inline", endpoint="transitions")],
                            )
                        },
                    ),
                ]
            ),
        )
        processes_section = Section(
            key="processes_section",
            collapsible=True,
            title=_("Processes"),
            display=Display(
                pages=[
                    Page(
                        title=_("Processes"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["processes_inline"]],
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="processes_inline", endpoint="processes")],
                            )
                        },
                    ),
                ]
            ),
        )
        # data_section = Section(
        #     key="data_section",
        #     collapsible=True,
        #     title=_("Data"),
        #     display=Display(
        #         pages=[
        #             Page(
        #                 title=_("Data"),
        #                 layouts={
        #                     default(): Layout(
        #                         grid_template_areas=[["data_inline"]],
        #                         grid_auto_columns="minmax(min-content, 1fr)",
        #                         grid_auto_rows=Style.MIN_CONTENT,
        #                         inlines=[Inline(key="data_inline", endpoint="data")],
        #                     )
        #                 },
        #             ),
        #         ]
        #     ),
        # )
        grid_fields = [
            ["name", "single_instance_execution"],
            ["model_section", "."],
            ["graph", "graph"],
            ["steps_section", "steps_section"],
            ["transitions_section", "transitions_section"],
            ["processes_section", "processes_section"],
            # ["data_section", "data_section"],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:2]

        return Display(
            pages=[
                Page(
                    title=_("Workflow"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_template_columns=["minmax(min-content, 3fr)", "minmax(min-content, 1fr)"],
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                            sections=[
                                model_section,
                                steps_section,
                                processes_section,
                                # data_section,
                                transitions_section,
                            ],
                        ),
                    },
                ),
            ]
        )
