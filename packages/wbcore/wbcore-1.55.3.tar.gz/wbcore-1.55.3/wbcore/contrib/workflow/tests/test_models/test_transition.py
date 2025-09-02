from unittest.mock import patch

import pytest
from wbcore.contrib.workflow.factories import UserStepFactory
from wbcore.contrib.workflow.models import Condition


@pytest.mark.django_db
class TestTransition:
    def test_all_conditions_satisfied_no_conditions(self, transition_factory, process_step_factory):
        transition = transition_factory()
        process_step = process_step_factory()
        assert transition.all_conditions_satisfied(process_step)

    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    @patch("wbcore.contrib.workflow.models.process.ProcessStep.get_instance")
    def test_all_conditions_satisfied_no_instance(
        self,
        mock_get_instance,
        mock_failed,
        random_child_step_factory,
        transition_factory,
        condition_factory,
        process_step_factory,
    ):
        transition = transition_factory()
        condition_factory(transition=transition)
        step = random_child_step_factory(exclude_factories=[UserStepFactory])
        process_step = process_step_factory(step=step)
        mock_get_instance.return_value = None
        assert not transition.all_conditions_satisfied(process_step)
        assert mock_failed.call_args.args[0] == process_step

    @patch("wbcore.contrib.workflow.models.process.ProcessStep.get_instance")
    @patch("wbcore.contrib.workflow.models.condition.Condition.satisfied")
    def test_all_conditions_satisfied(
        self, mock_satisfied, mock_get_instance, transition_factory, condition_factory, process_step_factory
    ):
        transition = transition_factory()
        process_step = process_step_factory()
        attached_instance = process_step.process.instance
        condition_factory()
        condition_factory(transition=transition)
        condition_factory(transition=transition)
        mock_get_instance.return_value = attached_instance
        mock_satisfied.return_value = True
        assert transition.all_conditions_satisfied(process_step)
        assert mock_satisfied.call_args.args == (attached_instance,)
        assert mock_satisfied.call_count == 2

    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    @patch("wbcore.contrib.workflow.models.process.ProcessStep.get_instance")
    def test_all_conditions_satisfied_errors(
        self,
        mock_get_instance,
        mock_failed,
        random_child_step_factory,
        transition_factory,
        condition_factory,
        process_step_factory,
    ):
        transition = transition_factory()
        step = random_child_step_factory(exclude_factories=[UserStepFactory])
        process_step = process_step_factory(step=step)
        attached_instance = process_step.process.instance
        condition_factory()
        condition_factory(
            transition=transition,
            operator=Condition.Operator.EQ,
            expected_value=attached_instance.first_name,
            negate_operator=False,
        )
        condition_factory(
            transition=transition,
            attribute_name="last_name",
            operator=Condition.Operator.EQ,
            expected_value=attached_instance.last_name,
            negate_operator=False,
        )
        condition_factory(
            transition=transition,
            attribute_name="Test",
            operator=Condition.Operator.EQ,
            expected_value=attached_instance.first_name,
            negate_operator=True,
        )
        mock_get_instance.return_value = attached_instance
        assert not transition.all_conditions_satisfied(process_step)
        assert mock_failed.call_args.args[0] == process_step

    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    @patch("wbcore.contrib.workflow.models.process.ProcessStep.get_instance")
    def test_all_conditions_satisfied_false(
        self,
        mock_get_instance,
        mock_failed,
        random_child_step_factory,
        transition_factory,
        condition_factory,
        process_step_factory,
    ):
        transition = transition_factory()
        step = random_child_step_factory(exclude_factories=[UserStepFactory])
        process_step = process_step_factory(step=step)
        attached_instance = process_step.process.instance
        condition_factory()
        condition_factory(
            transition=transition,
            operator=Condition.Operator.EQ,
            expected_value=attached_instance.first_name,
            negate_operator=False,
        )
        condition_factory(
            transition=transition,
            operator=Condition.Operator.EQ,
            expected_value=attached_instance.first_name,
            negate_operator=True,
        )
        condition_factory(
            transition=transition,
            attribute_name="last_name",
            operator=Condition.Operator.EQ,
            expected_value=attached_instance.last_name,
            negate_operator=False,
        )
        mock_get_instance.return_value = attached_instance
        assert not transition.all_conditions_satisfied(process_step)
        assert not mock_failed.called
