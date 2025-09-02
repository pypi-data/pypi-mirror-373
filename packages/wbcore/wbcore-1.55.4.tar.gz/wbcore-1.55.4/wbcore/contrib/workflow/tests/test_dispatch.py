import pytest
from pytest_mock import MockerFixture

from wbcore.contrib.workflow.dispatch import check_workflow_for_instance
from wbcore.contrib.workflow.models import Process, ProcessStep, Step, Workflow


class TestDispatch:
    @pytest.fixture
    def mocked_instance(self, mocker: MockerFixture):
        return mocker.MagicMock()

    # Fixture that automatically patches ContentType lookup in every test.
    @pytest.fixture(autouse=True)
    def patch_content_type(self, mocker: MockerFixture):
        return mocker.patch(
            "wbcore.contrib.workflow.dispatch.ContentType.objects.get_for_model",
            return_value="dummy_content_type",
        )

    # Fixture for creating a fake process step with a mismatching status.
    @pytest.fixture
    def mocked_process_step(self, mocker: MockerFixture):
        # Create the fake casted step.
        mocked_casted_step = mocker.MagicMock(spec=Step)

        # Create a fake workflow with a status field.
        mocked_workflow = mocker.MagicMock(spec=Workflow)
        mocked_workflow.status_field = "status_a"

        # Create a fake process that uses the workflow.
        mocked_process = mocker.MagicMock(spec=Process)
        mocked_process.workflow = mocked_workflow

        # Create a fake process step with a mismatching status.
        mocked_process_step = mocker.MagicMock(spec=ProcessStep)
        mocked_process_step.process = mocked_process
        mocked_process_step.status = "status_b"
        mocked_process_step.step.get_casted_step.return_value = mocked_casted_step

        return mocked_process_step, mocked_casted_step

    def test_check_workflow_for_instance_fail_process_steps(
        self, mocked_instance, mocked_process_step, mocker: MockerFixture
    ):
        # Arrange
        mocked_process_step, mocked_casted_step = mocked_process_step

        # Patch ProcessStep.objects.filter to return a fake process step.
        mocker.patch(
            "wbcore.contrib.workflow.models.ProcessStep.objects.filter",
            return_value=[mocked_process_step],
        )
        # Patch get_start_steps_for_instance to return an empty list.
        mocker.patch(
            "wbcore.contrib.workflow.models.Workflow.get_start_steps_for_instance",
            return_value=[],
        )

        # Act
        check_workflow_for_instance(sender=None, instance=mocked_instance, created=True)

        # Assert: Ensure set_failed was called with the correct arguments.
        mocked_casted_step.set_failed.assert_called_once_with(mocked_process_step, "Invalid status detected!")

    def test_check_workflow_for_instance_start_workflow(self, mocked_instance, mocker: MockerFixture):
        # Arrange: Create two fake start steps, each with its own workflow.
        fake_start_step1 = mocker.MagicMock()
        fake_workflow1 = mocker.MagicMock(spec=Workflow)
        fake_start_step1.workflow = fake_workflow1

        fake_start_step2 = mocker.MagicMock()
        fake_workflow2 = mocker.MagicMock(spec=Workflow)
        fake_start_step2.workflow = fake_workflow2

        # Patch get_start_steps_for_instance to return our fake start steps.
        get_start_steps_patch = mocker.patch(
            "wbcore.contrib.workflow.models.Workflow.get_start_steps_for_instance",
            return_value=[fake_start_step1, fake_start_step2],
        )
        # Patch ProcessStep.objects.filter to return an empty list.
        mocker.patch(
            "wbcore.contrib.workflow.models.ProcessStep.objects.filter",
            return_value=[],
        )

        # Act
        check_workflow_for_instance(sender=None, instance=mocked_instance, created=True)

        # Assert: Verify that get_start_steps_for_instance was called with our instance.
        get_start_steps_patch.assert_called_once_with(mocked_instance)
        # Verify that each fake workflow's start_workflow was called with its corresponding start step and the instance.
        fake_workflow1.start_workflow.assert_called_once_with(fake_start_step1, mocked_instance)
        fake_workflow2.start_workflow.assert_called_once_with(fake_start_step2, mocked_instance)
