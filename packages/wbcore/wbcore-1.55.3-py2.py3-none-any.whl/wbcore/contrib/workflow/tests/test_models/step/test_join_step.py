import pytest
from django.db import models
from pytest_mock import MockerFixture
from wbcore.contrib.workflow.models import (
    JoinStep,
    ProcessStep,
    Step,
    Transition,
)


class TestJoinStep:
    @pytest.fixture
    def join_step(self):
        return JoinStep()

    @pytest.fixture
    def mocked_step(self, mocker: MockerFixture):
        return mocker.MagicMock(spec=Step, set_canceled=mocker.MagicMock())

    @pytest.fixture
    def mocked_process_step(self, mocker: MockerFixture, mocked_step):
        return mocker.MagicMock(spec=ProcessStep, step=mocked_step)

    @pytest.fixture
    def mocked_transition(self, mocker: MockerFixture):
        return mocker.MagicMock(spec=Transition)

    @pytest.fixture
    def mocked_execute_single_next_step(self, mocker: MockerFixture, join_step):
        return mocker.patch.object(join_step, "execute_single_next_step")

    def test_cancel_if_leading_to_self_transition_found(
        self,
        mocker: MockerFixture,
        join_step,
        mocked_step,
        mocked_process_step,
        mocked_transition,
    ):
        # Arrange
        mocker.patch.object(join_step, "id", 1)
        mocked_transition.to_step = join_step
        mocked_step.outgoing_transitions.all.return_value = [mocked_transition]
        # Act
        join_step.cancel_if_leading_to_self(mocked_step, mocked_process_step)
        # Assert
        mocked_step.set_canceled.assert_called_once_with(mocked_process_step)

    def test_cancel_if_leading_to_self_no_transition_found(
        self,
        mocker: MockerFixture,
        join_step,
        mocked_step,
        mocked_process_step,
        mocked_transition,
    ):
        # Arrange
        mocked_step.outgoing_transitions.all.return_value = [mocked_transition]
        # Act
        join_step.cancel_if_leading_to_self(mocked_step, mocked_process_step)
        # Assert
        mocked_step.set_canceled.assert_not_called()

    @pytest.mark.parametrize("with_transition_qs", [True, False])
    def test_run_with_wait_for_all(
        self,
        mocker: MockerFixture,
        join_step,
        mocked_process_step,
        with_transition_qs,
        mocked_execute_single_next_step,
    ):
        # Arrange
        mocker.patch.object(join_step, "wait_for_all", True)
        mocked_process_step.save = mocker.MagicMock()
        mocked_object_manager = mocker.patch("wbcore.contrib.workflow.models.transition.Transition.objects")
        mocked_qs = mocker.MagicMock(spec=models.QuerySet)
        mocked_qs.exists.return_value = with_transition_qs
        mocked_object_manager.filter.return_value = mocked_qs
        # Act
        join_step.run(mocked_process_step)
        # Assert
        assert mocked_process_step.state == ProcessStep.StepState.WAITING
        mocked_process_step.save.assert_called_once()
        if with_transition_qs:
            mocked_execute_single_next_step.assert_not_called()
        else:
            mocked_execute_single_next_step.assert_called_once_with(mocked_process_step)

    def test_run_without_wait_for_all(
        self,
        mocker: MockerFixture,
        join_step,
        mocked_process_step,
        mocked_execute_single_next_step,
    ):
        # Arrange
        mocker.patch.object(join_step, "wait_for_all", False)

        mocked_cancel_if_leading = mocker.patch.object(join_step, "cancel_if_leading_to_self")
        mocked_process_step.save = mocker.MagicMock()
        mocked_object_manager = mocker.patch("wbcore.contrib.workflow.models.step.ProcessStep.objects")
        unfinished_step_a = mocker.MagicMock(spec=ProcessStep, pk=123, step=mocker.MagicMock(spec=Step))

        unfinished_step_b = mocker.MagicMock(spec=ProcessStep, pk=456, step=mocker.MagicMock(spec=Step))

        mocked_qs = mocker.MagicMock(spec=models.QuerySet)
        mocked_qs.exclude.return_value = [unfinished_step_a, unfinished_step_b]
        mocked_object_manager.filter.return_value = mocked_qs
        # Act
        join_step.run(mocked_process_step)
        # Assert
        assert mocked_process_step.state == ProcessStep.StepState.WAITING
        assert mocked_cancel_if_leading.call_count == len(mocked_qs.exclude.return_value)
        mocked_process_step.save.assert_called_once()
        mocked_execute_single_next_step.assert_called_once()
