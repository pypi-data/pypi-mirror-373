from unittest.mock import patch

import pytest


@pytest.mark.django_db
class TestSplitStep:
    @patch("wbcore.contrib.workflow.models.step.activate_step.delay")
    @patch("wbcore.contrib.workflow.models.step.Step.get_all_valid_outgoing_transitions")
    @patch("wbcore.contrib.workflow.models.step.Step.set_finished")
    def test_run(
        self,
        mock_finished,
        mock_transitions,
        mock_activate,
        process_step_factory,
        transition_factory,
        split_step_factory,
    ):
        transition1 = transition_factory()
        transition2 = transition_factory()
        transition_factory()
        mock_transitions.return_value = [transition1, transition2]
        step = split_step_factory()
        process_step = process_step_factory(step=step)
        step.run(process_step)
        assert mock_finished.call_args.args == (process_step,)
        assert mock_activate.call_args_list == [
            ((transition1.to_step.pk, process_step.process.pk),),
            ((transition2.to_step.pk, process_step.process.pk),),
        ]

    @patch("wbcore.contrib.workflow.models.step.activate_step.delay")
    @patch("wbcore.contrib.workflow.models.step.Step.get_all_valid_outgoing_transitions")
    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    def test_run_failed(
        self,
        mock_failed,
        mock_transitions,
        mock_activate,
        process_step_factory,
        split_step_factory,
    ):
        mock_transitions.return_value = []
        step = split_step_factory()
        process_step = process_step_factory(step=step)
        step.run(process_step)
        assert mock_failed.call_args.args[0] == process_step
        assert not mock_activate.called
