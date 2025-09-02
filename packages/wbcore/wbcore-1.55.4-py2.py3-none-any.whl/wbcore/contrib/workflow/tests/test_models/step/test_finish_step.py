import pytest
from django.utils.translation import gettext
from pytest_mock import MockerFixture
from wbcore.contrib.workflow.models import FinishStep, Process, ProcessStep, Step


class TestFinishStep:
    @pytest.fixture(autouse=True)
    def patch_super_finish(self, mocker: MockerFixture):
        mocker.patch("wbcore.contrib.workflow.models.step.Step.finish", autospec=True)

    @pytest.fixture
    def mocked_finish_step(self, mocker: MockerFixture):
        return mocker.MagicMock(spec=FinishStep)

    @pytest.fixture
    def mocked_instance(self, mocker: MockerFixture):
        return mocker.MagicMock(first_name="Original")

    @pytest.fixture
    def mocked_process(self, mocker: MockerFixture, mocked_instance):
        mocked_process = mocker.MagicMock(
            finished=None,
            instance=mocked_instance,
            save=mocker.MagicMock(),
            spec=Process,
            state=Process.ProcessState.ACTIVE,
        )
        return mocked_process

    @pytest.fixture
    def mocked_process_step(self, mocker: MockerFixture, mocked_process):
        return mocker.MagicMock(spec=ProcessStep, process=mocked_process)

    def test_run(self, mocker: MockerFixture, mocked_process_step, mocked_finish_step):
        # Arrange
        mocked_qs = mocker.patch("wbcore.contrib.workflow.models.step.ProcessStep.objects.filter")
        mocked_qs.return_value.exclude.return_value.exists.return_value = False
        mocked_set_finished = mocker.patch.object(mocked_finish_step, "set_finished")
        # Act
        FinishStep.run(mocked_finish_step, mocked_process_step)
        # Assert
        mocked_set_finished.assert_called_once_with(mocked_process_step)

    def test_run_failed(self, mocker: MockerFixture, mocked_process_step, mocked_finish_step):
        # Arrange
        mocked_qs = mocker.patch("wbcore.contrib.workflow.models.step.ProcessStep.objects.filter")
        mocked_qs.return_value.exclude.return_value.exists.return_value = True
        mocked_set_failed = mocker.patch.object(mocked_finish_step, "set_failed")
        # Act
        FinishStep.run(mocked_finish_step, mocked_process_step)
        # Assert
        mocked_set_failed.assert_called_once_with(
            mocked_process_step,
            gettext("There are process steps still running for this workflow!"),
        )

    @pytest.mark.parametrize(
        "unfinished_state",
        [
            ProcessStep.StepState.ACTIVE,
            ProcessStep.StepState.WAITING,
            ProcessStep.StepState.CANCELED,
            ProcessStep.StepState.FAILED,
        ],
    )
    def test_finish_not_finished(
        self,
        mocker: MockerFixture,
        mocked_process,
        mocked_process_step,
        unfinished_state,
    ):
        # Arrange
        mocked_process.preserved_instance = {"first_name": "Test"}
        mocked_process_step.state = unfinished_state

        finish_step = FinishStep()
        mock_serializer = mocker.patch("wbcore.contrib.workflow.models.step.get_model_serializer_class_for_instance")
        # Act
        finish_step.finish(mocked_process_step)
        # Assert
        mock_serializer.assert_not_called()
        mocked_process_step.process.save.assert_not_called()
        assert mocked_process.finished is None
        assert mocked_process.state == Process.ProcessState.ACTIVE

    def test_finish_write_preserved_instance(
        self,
        mocker: MockerFixture,
        mocked_process,
        mocked_process_step,
    ):
        # Arrange
        preserved_data = {"first_name": "Updated"}

        mocked_serializer = mocker.MagicMock()
        mocked_serializer.validated_data = preserved_data
        mocked_serializer_class = mocker.MagicMock()
        mocked_serializer_class.return_value = mocked_serializer
        mocker.patch(
            "wbcore.contrib.workflow.models.step.get_model_serializer_class_for_instance",
            return_value=mocked_serializer_class,
        )
        mocked_serializer.is_valid.return_value = True
        mocked_serializer.update = mocker.MagicMock()

        mocked_process.preserved_instance = preserved_data

        mocked_step = mocker.MagicMock(spec=Step, write_preserved_instance=True)
        mocked_step.workflow.preserve_instance = True

        mocked_process_step.state = ProcessStep.StepState.FINISHED
        mocked_process_step.step = mocked_step

        finish_step = FinishStep()
        mocker.patch.object(finish_step, "write_preserved_instance", True)
        # Act
        finish_step.finish(mocked_process_step)
        # Assert
        mocked_serializer.is_valid.assert_called_once()
        mocked_serializer.update.assert_called_once_with(mocked_process.instance, preserved_data)
        mocked_process.save.assert_called_once()
        assert mocked_process.finished is not None
        assert mocked_process.state == Process.ProcessState.FINISHED

    def test_finish_do_not_write_mocker(self, mocker: MockerFixture, mocked_process, mocked_process_step):
        # Arrange
        mocked_process.preserved_instance = {"first_name": "Updated"}
        mocked_process.state = Process.ProcessState.ACTIVE

        mocked_process_step.state = ProcessStep.StepState.FINISHED

        finish_step = FinishStep()
        mocker.patch.object(finish_step, "write_preserved_instance", False)

        mock_serializer = mocker.patch("wbcore.contrib.workflow.models.step.get_model_serializer_class_for_instance")

        # Act
        finish_step.finish(mocked_process_step)

        # Assert
        mock_serializer.assert_not_called()
        mocked_process.save.assert_called_once()
        assert mocked_process.finished is not None
        assert mocked_process.state == Process.ProcessState.FINISHED

    def test_finish_no_preserved_instance_mocker(self, mocker: MockerFixture, mocked_process, mocked_process_step):
        # Arrange
        mocked_process.preserved_instance = None
        mocked_process.state = Process.ProcessState.ACTIVE

        mocked_process_step.state = ProcessStep.StepState.FINISHED

        finish_step = FinishStep()
        mocker.patch.object(finish_step, "write_preserved_instance", True)

        mock_serializer = mocker.patch("wbcore.contrib.workflow.models.step.get_model_serializer_class_for_instance")

        # Act
        finish_step.finish(mocked_process_step)

        # Assert
        mock_serializer.assert_not_called()
        mocked_process.save.assert_called_once()
        assert mocked_process.finished is not None
        assert mocked_process.state == Process.ProcessState.FINISHED
