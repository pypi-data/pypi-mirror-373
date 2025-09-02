from unittest.mock import patch

import pytest


@pytest.mark.django_db
class TestScriptStep:
    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    @patch("wbcore.contrib.workflow.models.step.Step.execute_single_next_step")
    def test_run(self, mock_execute, mock_failed, script_step_factory, process_step_factory):
        step = script_step_factory()
        process_step = process_step_factory(step=step)
        step.run(process_step)
        assert not mock_failed.called
        assert mock_execute.call_args.args == (process_step,)

    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    @patch("wbcore.contrib.workflow.models.step.Step.execute_single_next_step")
    def test_run_failed(self, mock_execute, mock_failed, script_step_factory, process_step_factory):
        step = script_step_factory(script="Test")
        process_step = process_step_factory(step=step)
        step.run(process_step)
        assert mock_failed.call_args.args[0] == process_step
        assert not mock_execute.called
