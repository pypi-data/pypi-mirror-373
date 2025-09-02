from typing import Optional

from django.utils.translation import gettext as _
from django.utils.translation import pgettext

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
                        grid_template_columns=[
                            "minmax(min-content, 1fr)",
                        ],
                        grid_auto_rows=Style.MIN_CONTENT,
                        inlines=[Inline(key="transitions_inline", endpoint="transitions")],
                    )
                },
            ),
        ]
    ),
)
process_steps_section = Section(
    key="process_steps_section",
    collapsible=True,
    title=_("Process Steps"),
    display=Display(
        pages=[
            Page(
                title=_("Process Steps"),
                layouts={
                    default(): Layout(
                        grid_template_areas=[["process_steps_inline"]],
                        grid_template_columns=[
                            "minmax(min-content, 1fr)",
                        ],
                        grid_auto_rows=Style.MIN_CONTENT,
                        inlines=[Inline(key="process_steps_inline", endpoint="process_steps")],
                    )
                },
            ),
        ]
    ),
)


class StepDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="name", label=_("Name")),
            dp.Field(key="step_type", label=_("Step Type")),
            dp.Field(key="workflow", label=_("Workflow")),
            dp.Field(key="status", label=_("Status")),
            dp.Field(key="code", label=_("Code")),
            dp.Field(key="permission", label=_("Permission")),
        ]

        if "workflow_id" in self.view.kwargs:
            fields.pop(2)

        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["name", "step_type", "workflow"],
            ["status", "code", "permission"],
            [
                "transitions_section",
                "transitions_section",
                "transitions_section",
            ],
            [
                "process_steps_section",
                "process_steps_section",
                "process_steps_section",
            ],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:2]

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[transitions_section, process_steps_section],
                        )
                    },
                ),
            ]
        )


class UserStepDisplayConfig(StepDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        if step_display := super().get_list_display():
            step_display.fields.pop(1)
            userstep_fields = [
                dp.Field(key="assignee", label=_("Assignee")),
                dp.Field(key="group", label=_("Group")),
                dp.Field(key="assignee_method", label=_("Assignee Method")),
                dp.Field(key="notify_user", label=_("Notify User")),
                # dp.Field(key="display", label=_("Display")),
            ]
            return dp.ListDisplay(
                fields=step_display.fields + userstep_fields,
            )
        return None

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["name", "workflow", "status"],
            ["code", "assignee", "notify_user"],
            ["group", "assignee_method", "permission"],
            # ["display", ".", "."],
            [
                "transitions_section",
                "transitions_section",
                "transitions_section",
            ],
            [
                "process_steps_section",
                "process_steps_section",
                "process_steps_section",
            ],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:3]

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[transitions_section, process_steps_section],
                        )
                    },
                ),
            ]
        )


class BaseStepDisplayConfig(StepDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        if step_display := super().get_list_display():
            step_display.fields.pop(1)
            return dp.ListDisplay(
                fields=step_display.fields,
            )
        return None

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["name", "workflow", "code"],
            ["status", "permission", "."],
            [
                "transitions_section",
                "transitions_section",
                "transitions_section",
            ],
            [
                "process_steps_section",
                "process_steps_section",
                "process_steps_section",
            ],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:2]

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[transitions_section, process_steps_section],
                        )
                    },
                ),
            ]
        )


class JoinStepDisplayConfig(BaseStepDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        if base_display := super().get_list_display():
            base_display.fields.insert(2, dp.Field(key="wait_for_all", label=_("Wait For All")))
            return dp.ListDisplay(
                fields=base_display.fields,
            )
        return None

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["name", "workflow", "wait_for_all"],
            ["status", "permission", "code"],
            [
                "transitions_section",
                "transitions_section",
                "transitions_section",
            ],
            [
                "process_steps_section",
                "process_steps_section",
                "process_steps_section",
            ],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:2]

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[transitions_section, process_steps_section],
                        )
                    },
                ),
            ]
        )


class ScriptStepDisplayConfig(BaseStepDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        if base_display := super().get_list_display():
            base_display.fields.insert(2, dp.Field(key="script", label=_("Script")))
            return dp.ListDisplay(
                fields=base_display.fields,
            )
        return None

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["name", "workflow", "code"],
            ["status", "permission", "."],
            ["script", "script", "script"],
            [
                "transitions_section",
                "transitions_section",
                "transitions_section",
            ],
            [
                "process_steps_section",
                "process_steps_section",
                "process_steps_section",
            ],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:3]

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[transitions_section, process_steps_section],
                        )
                    },
                ),
            ]
        )


class EmailStepDisplayConfig(BaseStepDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        if base_display := super().get_list_display():
            base_display.fields = (
                base_display.fields[:1]
                + [
                    dp.Field(
                        key="to",
                        label=pgettext("Email context", "To"),
                    ),
                    dp.Field(key="subject", label=_("Subject")),
                    dp.Field(key="template", label=_("Template")),
                    dp.Field(key="cc", label=_("Cc")),
                    dp.Field(key="bcc", label=_("BCC")),
                ]
                + base_display.fields[1:]
            )
            return dp.ListDisplay(
                fields=base_display.fields,
            )
        return None

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["name", "workflow", "code"],
            ["subject", "template", "."],
            ["to", "cc", "bcc"],
            ["status", "permission", "."],
            [
                "transitions_section",
                "transitions_section",
                "transitions_section",
            ],
            [
                "process_steps_section",
                "process_steps_section",
                "process_steps_section",
            ],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:4]

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[transitions_section, process_steps_section],
                        )
                    },
                ),
            ]
        )


class FinishDisplayConfig(BaseStepDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        if base_display := super().get_list_display():
            base_display.fields.insert(
                2, dp.Field(key="write_preserved_instance", label=_("Write Preserved Instance"))
            )
            return dp.ListDisplay(
                fields=base_display.fields,
            )
        return None

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["name", "workflow", "code"],
            ["status", "permission", "write_preserved_instance"],
            [
                "transitions_section",
                "transitions_section",
                "transitions_section",
            ],
            [
                "process_steps_section",
                "process_steps_section",
                "process_steps_section",
            ],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:2]

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[transitions_section, process_steps_section],
                        )
                    },
                ),
            ]
        )


class StartStepDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="name", label=_("Name")),
            dp.Field(key="workflow", label=_("Workflow")),
            dp.Field(key="status", label=_("Status")),
            dp.Field(key="code", label=_("Code")),
        ]

        if "workflow_id" in self.view.kwargs:
            fields.pop(1)

        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["name", "workflow"],
            ["status", "code"],
            [
                "transitions_section",
                "transitions_section",
            ],
            [
                "process_steps_section",
                "process_steps_section",
            ],
        ]
        if "pk" not in self.view.kwargs:
            grid_fields = grid_fields[:2]

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[transitions_section, process_steps_section],
                        )
                    },
                ),
            ]
        )
