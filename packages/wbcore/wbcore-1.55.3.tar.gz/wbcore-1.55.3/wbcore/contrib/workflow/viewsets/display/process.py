from typing import Optional

from django.utils.translation import gettext as _

from wbcore.contrib.workflow.models import Process, ProcessStep
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


class ProcessDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="workflow", label=_("Workflow")),
            dp.Field(key="id", label=_("UUID")),
            dp.Field(key="started", label=_("Started")),
            dp.Field(key="finished", label=_("Finished")),
            dp.Field(key="content_type", label=_("Attached Model")),
        ]

        if "workflow_id" in self.view.kwargs:
            fields.pop(0)

        color_map = Process.ProcessState.get_color_map()

        return dp.ListDisplay(
            fields=fields,
            legends=get_state_legend(color_map),
            formatting=get_state_formatting(color_map),
        )

    def get_instance_display(self) -> Display:
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
        return Display(
            pages=[
                Page(
                    title=_("Process"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["state", "."],
                                ["workflow", "id"],
                                ["started", "finished"],
                                ["content_type", "instance_id"],
                                ["process_steps_section", "process_steps_section"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                            sections=[process_steps_section],
                        ),
                    },
                ),
            ]
        )


def get_state_legend(color_map: list[tuple]) -> list[dp.Legend]:
    """Dynamically creates the process or process step legend based on the state enum using the color mapping"""

    legend_items = []
    for state, color in color_map:
        legend_items.append(dp.LegendItem(icon=color, label=state.label, value=state.value))
    return [dp.Legend(key="state", items=legend_items)]


def get_state_formatting(color_map: list[tuple]) -> list[dp.Formatting]:
    """Dynamically creates the process or process step list formatting based on the state enum using the color mapping"""

    formatting_rules = []
    for state, color in color_map:
        formatting_rules.append(dp.FormattingRule(condition=("==", state.value), style={"backgroundColor": color}))
    return [dp.Formatting(column="state", formatting_rules=formatting_rules)]


class ProcessStepDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="id", label=_("UUID")),
            dp.Field(key="step", label=_("Step")),
            dp.Field(key="process", label=_("Process")),
            dp.Field(key="started", label=_("Started")),
            dp.Field(key="finished", label=_("Finished")),
            dp.Field(key="error_message", label=_("Error Message")),
            dp.Field(key="assignee", label=_("Assignee")),
            dp.Field(key="group", label=_("Group")),
            dp.Field(key="permission", label=_("Permission")),
            dp.Field(key="status", label=_("Status")),
        ]

        if "process_id" in self.view.kwargs:
            fields.pop(2)
        elif "step_id" in self.view.kwargs:
            fields.pop(1)

        color_map = ProcessStep.StepState.get_color_map()

        return dp.ListDisplay(
            fields=fields,
            legends=get_state_legend(color_map),
            formatting=get_state_formatting(color_map),
        )

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["state", ".", "."],
            ["id", "step", "process"],
            ["started", "finished", "status"],
            ["assignee", "group", "permission"],
            ["error_message", "error_message", "."],
        ]
        # if "pk" in self.view.kwargs:
        #     process_step: ProcessStep = self.view.get_object()
        #     if (step := process_step.step).step_type == Step.StepType.USERSTEP and (
        #         display := step.get_casted_step().display
        #     ):
        #         # Display those fields declared in the user step display model
        #         grid_fields = display.grid_template_areas
        #     elif attached_data := process_step.process.workflow.attached_data.all():
        #         # Display the fields from attached data objects
        #         # TODO: Optimize
        #         sublists = split_list_into_grid_template_area_sublists(
        #             [f"data__{str(data.pk)}" for data in attached_data], 3
        #         )
        #         grid_fields = grid_fields + sublists

        return Display(
            pages=[
                Page(
                    title=_("Process Step"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=grid_fields,
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                    },
                ),
            ]
        )


class AssignedProcessStepDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="step", label=_("Step")),
                dp.Field(key="attached_model", label=_("Attached Model")),
                dp.Field(key="workflow_name", label=_("Workflow")),
                dp.Field(key="started", label=_("Started")),
                dp.Field(key="finished", label=_("Finished")),
                dp.Field(key="group", label=_("Group")),
                dp.Field(key="permission", label=_("Permission")),
                dp.Field(key="status", label=_("Status")),
            )
        )
