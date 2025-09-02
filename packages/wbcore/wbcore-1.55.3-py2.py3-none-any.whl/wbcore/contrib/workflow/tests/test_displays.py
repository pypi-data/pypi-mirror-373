from rest_framework.test import APIRequestFactory

from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.workflow.models import ProcessStep
from wbcore.contrib.workflow.viewsets.display.process import (
    get_state_formatting,
    get_state_legend,
)


class TestProcessStep:
    api_factory = APIRequestFactory()

    def test_get_state_legend(self):
        color_map = [
            (ProcessStep.StepState.FAILED, WBColor.GREEN_LIGHT.value),
            (ProcessStep.StepState.CANCELED, WBColor.BLUE_LIGHT.value),
        ]
        assert set((y.icon, y.label, y.value) for y in get_state_legend(color_map)[0].items) == {
            (
                WBColor.GREEN_LIGHT.value,
                ProcessStep.StepState.FAILED.label,
                ProcessStep.StepState.FAILED.value,
            ),
            (
                WBColor.BLUE_LIGHT.value,
                ProcessStep.StepState.CANCELED.label,
                ProcessStep.StepState.CANCELED.value,
            ),
        }

    def test_get_state_formatting(self):
        color_map = [
            (ProcessStep.StepState.WAITING, WBColor.GREY.value),
            (ProcessStep.StepState.ACTIVE, WBColor.YELLOW_DARK.value),
        ]
        assert set(
            (y.style["backgroundColor"], y.condition[1]) for y in get_state_formatting(color_map)[0].formatting_rules
        ) == {
            (WBColor.GREY.value, ProcessStep.StepState.WAITING.value),
            (WBColor.YELLOW_DARK.value, ProcessStep.StepState.ACTIVE.value),
        }
