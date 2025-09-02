import pytest
from pytest_mock import MockerFixture
from wbcore.contrib.workflow.models import DecisionStep, Transition


class TestDecisionStep:
    @pytest.fixture
    def mocked_instances(self, mocker: MockerFixture):
        return mocker.MagicMock(first_name="John")

    @pytest.fixture
    def mocked_decision_step(self, mocker: MockerFixture):
        return mocker.MagicMock(spec=DecisionStep)

    def test_get_first_valid_transition(
        self,
        mocker: MockerFixture,
        mocked_process_step,
        mocked_instances,
        mocked_decision_step,
    ):
        # Arrange
        mocked_process_step.get_instance.return_value = mocked_instances
        mocked_process_step.step = mocked_decision_step
        valid_transition1 = mocker.MagicMock(spec=Transition)
        valid_transition2 = mocker.MagicMock(spec=Transition)
        invalid_transition = mocker.MagicMock(spec=Transition)
        mocked_decision_step.get_outgoing_transitions.return_value = [
            invalid_transition,
            valid_transition1,
            valid_transition2,
        ]
        invalid_transition.all_conditions_satisfied.return_value = False
        valid_transition1.all_conditions_satisfied.return_value = True
        valid_transition2.all_conditions_satisfied.return_value = True
        # Act
        result = DecisionStep.get_first_valid_transition(mocked_decision_step, mocked_process_step)
        # Assert
        assert result in [valid_transition1, valid_transition2]
        invalid_transition.all_conditions_satisfied.assert_called_once_with(mocked_process_step)
        valid_transition1.all_conditions_satisfied.assert_called_once_with(mocked_process_step)
        valid_transition2.all_conditions_satisfied.assert_not_called()

    def test_get_first_valid_transition_no_transitions(
        self, mocker, mocked_process_step, mocked_instances, mocked_decision_step
    ):
        # Arrange
        mocked_process_step.get_instance.return_value = mocked_instances
        mocked_process_step.step = mocked_decision_step
        invalid_transition = mocker.MagicMock(spec=Transition)
        mocked_decision_step.get_outgoing_transitions.return_value = [invalid_transition]
        invalid_transition.all_conditions_satisfied.return_value = False
        # Act
        result = DecisionStep.get_first_valid_transition(mocked_decision_step, mocked_process_step)
        # Assert
        assert result is None
        invalid_transition.all_conditions_satisfied.assert_called_once_with(mocked_process_step)

    def test_run(self, mocker: MockerFixture, mocked_process_step, mocked_decision_step):
        # Arrange
        mocked_start_next_step = mocker.patch("wbcore.contrib.workflow.models.step.Step.start_next_step")
        mocked_transition = mocker.MagicMock(spec=Transition)
        mocked_decision_step.get_first_valid_transition.return_value = mocked_transition
        # Act
        DecisionStep.run(mocked_decision_step, mocked_process_step)
        # Assert
        mocked_decision_step.get_first_valid_transition.assert_called_once_with(mocked_process_step)
        mocked_start_next_step.assert_called_once_with(mocked_process_step, mocked_transition)

    def test_run_failed(self, mocker: MockerFixture, mocked_process_step, mocked_decision_step):
        # Arrange
        mocked_activate_step = mocker.patch("wbcore.contrib.workflow.models.step.activate_step.delay")
        mocked_decision_step.get_first_valid_transition.return_value = None
        mocked_set_failed = mocker.patch.object(mocked_decision_step, "set_failed")
        # Act
        DecisionStep.run(mocked_decision_step, mocked_process_step)
        # Assert
        mocked_decision_step.get_first_valid_transition.assert_called_once_with(mocked_process_step)
        mocked_set_failed.assert_called_once_with(
            mocked_process_step, "No valid outgoing transition found for this step!"
        )
        mocked_activate_step.assert_not_called()
