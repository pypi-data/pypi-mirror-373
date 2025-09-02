import pytest
from pytest_mock import MockerFixture
from rest_framework.test import APIRequestFactory

from wbcore.contrib.authentication.models import Group, User
from wbcore.contrib.workflow.models import ProcessStep, Step, Transition, UserStep
from wbcore.contrib.workflow.serializers import (
    AssignedProcessStepSerializer,
    ProcessStepModelSerializer,
)
from wbcore.test.utils import get_or_create_superuser


@pytest.fixture
def process_step(mocker: MockerFixture):
    mocked_process_step = mocker.MagicMock(spec=ProcessStep)
    mocked_process_step.pk = 1
    mocked_process_step.state = ProcessStep.StepState.ACTIVE
    return mocked_process_step


class TestProcessStep:
    @pytest.fixture
    def transitions(self, mocker: MockerFixture):
        transition_1 = mocker.MagicMock(spec=Transition)
        transition_1.pk = 101
        transition_1.name = "Transition One"
        transition_1.icon = "icon_1"

        transition_2 = mocker.MagicMock(spec=Transition)
        transition_2.pk = 102
        transition_2.name = "Transition Two"
        transition_2.icon = "icon_2"

        return (transition_1, transition_2)

    @pytest.fixture
    def casted_step(self, mocker: MockerFixture):
        mocked_casted_step = mocker.MagicMock(spec=Step, assignee_method=False)
        return mocked_casted_step

    @pytest.fixture
    def user_step(self, mocker: MockerFixture, casted_step, transitions):
        mocked_user_step = mocker.MagicMock(spec=UserStep)
        mocked_user_step.step_type = Step.StepType.USERSTEP
        mocked_user_step.get_casted_step.return_value = casted_step
        mocked_user_step.get_all_valid_outgoing_transitions.return_value = [*transitions]
        return mocked_user_step

    @pytest.fixture(autouse=True)
    def mocked_patch_path(self, mocker: MockerFixture):
        mocker.patch(
            "wbcore.contrib.workflow.models.workflow",
            return_value="/dummy-url/",
        )
        mocker.patch(
            "wbcore.contrib.workflow.dispatch.ContentType.objects.get_for_model",
            return_value="content_type",
        )

    @pytest.mark.parametrize("user", ["super_user", "user", "group"])
    def test_next_process_step_buttons(self, mocker: MockerFixture, user, process_step, user_step):
        """
        This test verifies that the method next_process_step_buttons returns buttons when:
        - "super_user": The user is a superuser.
        - "user": The user is the assignee of the process step.
        - "group": The user belongs to the group assigned to the process step.
        """
        # Arrange
        mocked_process_step = process_step
        mocked_process_step.step = user_step

        request_user = mocker.MagicMock(spec=User, is_superuser=(user == "super_user"))
        if user == "user":
            mocked_process_step.assignee = request_user
        elif user == "group":
            mocked_group = mocker.MagicMock(spec=Group)
            mocked_group.user_set.all.return_value = [request_user]
            mocked_process_step.group = mocked_group
        request = mocker.MagicMock(user=request_user)

        # Act
        serializer = ProcessStepModelSerializer(mocked_process_step, context={"request": request})
        data = serializer.data
        button_labels = {button["label"] for button in data["_buttons"]}

        # Assert
        assert len(data["_buttons"]) == 2
        assert button_labels == {"Transition One", "Transition Two"}

    @pytest.mark.parametrize("reason", ["finished_state", "not_user_step"])
    def test_no_transition_buttons_when_step_is_not_eligible(
        self, mocker: MockerFixture, reason, process_step, user_step
    ):
        """
        Test that no transition buttons appear if:
        - The process step is in a non-active state, OR
        - The step is not a UserStep type.
        """
        # Arrange
        mocked_process_step = process_step
        if reason == "inactive_state":
            mocked_process_step.state = ProcessStep.StepState.FINISHED
        else:
            user_step.step_type = Step.StepType.SPLITSTEP

        super_user = mocker.MagicMock(spec=User, is_superuser=True)
        request = mocker.MagicMock(user=super_user)
        # Act
        serializer = ProcessStepModelSerializer(mocked_process_step, context={"request": request})
        data = serializer.data

        # Assert
        assert len(data["_buttons"]) == 0

    def test_next_process_step_buttons_not_assigned(self, mocker: MockerFixture, process_step, user_step, casted_step):
        """
        No buttons when there is a assignee_method
        """
        # Arrange
        request_user = mocker.MagicMock(spec=User, is_superuser=False)
        request = mocker.MagicMock(user=request_user)

        mocked_group = mocker.MagicMock(spec=Group)
        mocked_group.user_set.all.return_value = [request_user]

        mocked_casted_step = casted_step
        mocked_casted_step.assignee_method = True

        mocked_user_step = user_step
        mocked_user_step.get_casted_step.return_value = casted_step

        mocked_process_step = process_step
        mocked_process_step.step = mocked_user_step
        mocked_process_step.group = mocked_group

        # Act
        serializer = ProcessStepModelSerializer(mocked_process_step, context={"request": request})
        data = serializer.data
        # Assert
        assert len(data["_buttons"]) == 0

    def test_next_process_step_buttons_no_transitions(
        self, mocker: MockerFixture, process_step, user_step, casted_step
    ):
        """
        No transitions no buttons
        """
        # Arrange
        request_user = mocker.MagicMock(spec=User, is_superuser=True)
        request = mocker.MagicMock(user=request_user)

        mocked_user_step = user_step
        mocked_user_step.get_all_valid_outgoing_transitions.return_value = []

        mocked_process_step = process_step
        mocked_process_step.step = user_step

        # Act
        serializer = ProcessStepModelSerializer(mocked_process_step, context={"request": request})
        data = serializer.data
        # Assert
        assert len(data["_buttons"]) == 0


class TestAssignedProcessStep:
    @pytest.fixture
    def process_step_with_assignee(self, mocker: MockerFixture, process_step):
        mocked_step = mocker.MagicMock(spec=Step)
        mocked_step.id = 42
        mocked_user = mocker.MagicMock(spec=User)
        mocked_user.id = 3
        process_step.step = mocked_step
        process_step.assignee = mocked_user
        return process_step

    def test_get_instance_endpoint_no_request(self, mocker: MockerFixture, process_step_with_assignee):
        serializer = AssignedProcessStepSerializer(process_step_with_assignee)
        assert serializer.data
        assert serializer.data["instance_endpoint"] == ""

    @pytest.mark.django_db
    @pytest.mark.with_db
    @pytest.mark.parametrize("with_instance", [True, False])
    def test_get_instance_endpoint_no_attached_instance(self, process_step_factory, with_instance):
        api_factory = APIRequestFactory()
        process_step = (
            process_step_factory()
            if with_instance
            else process_step_factory(process__instance=None, process__instance_id=None)
        )
        request = api_factory.get("")
        request.user = get_or_create_superuser()
        serializer = AssignedProcessStepSerializer(process_step, context={"request": request})
        assert serializer.data
        if with_instance:
            assert "processstep" not in serializer.data["instance_endpoint"]
            assert "person" in serializer.data["instance_endpoint"]
        else:
            assert "processstep" in serializer.data["instance_endpoint"]
