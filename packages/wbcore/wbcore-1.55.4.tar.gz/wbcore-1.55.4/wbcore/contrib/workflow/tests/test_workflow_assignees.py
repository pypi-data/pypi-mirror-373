import pytest
from pytest_mock import MockerFixture

from wbcore.contrib.authentication.models import Group, User
from wbcore.contrib.directory.models import Entry
from wbcore.contrib.workflow.models import Process, ProcessStep, Step
from wbcore.contrib.workflow.workflows import (
    manager_of_instance_assignee,
    random_group_member,
    weighted_random,
)


class TestWorkflowAssignees:
    @pytest.fixture
    def mocked_active_user(self, mocker: MockerFixture):
        return mocker.MagicMock(spec=User, is_active=True)

    @pytest.fixture
    def mocked_group(self, mocker: MockerFixture):
        return mocker.MagicMock(spec=Group)

    def test_manager_of_instance_assignee_person(self, mocker: MockerFixture, mocked_process_step, mocked_active_user):
        # Arrange
        kwargs = {"assignee_field": "profile", "assignee_type": "entry"}

        user_a = mocker.MagicMock(spec=User, is_active=False)
        manager_a = mocker.MagicMock(spec=Entry, user_account=user_a)
        manager_b = mocker.MagicMock(spec=Entry, user_account=mocked_active_user)

        assignee_mock = mocker.MagicMock()

        mocked_process_step.process.instance = mocker.MagicMock(spec=User)
        mocked_process_step.process.instance.profile = assignee_mock

        assignee_mock.relationship_managers.all.return_value = [manager_a, manager_b]
        # Act
        result = manager_of_instance_assignee(mocked_process_step, **kwargs)
        # Assert
        assert result == manager_b.user_account

    def test_manager_of_instance_assignee_no_kwargs(self, mocked_process_step, mocker: MockerFixture):
        mocked_process_step.step.get_casted_step.return_value = mocker.MagicMock(spec=Step)
        result = manager_of_instance_assignee(mocked_process_step)
        assert result is None
        mocked_process_step.step.get_casted_step().set_failed.assert_called_once_with(
            mocked_process_step,
            "Error in assignee method: Incorrect input in kwargs field!",
        )

    def test_manager_of_instance_assignee_no_assignee_field(self, mocked_process_step):
        kwargs = {"test": "profile", "assignee_type": "entry"}
        result = manager_of_instance_assignee(mocked_process_step, **kwargs)
        assert result is None
        mocked_process_step.step.get_casted_step().set_failed.assert_called_once_with(
            mocked_process_step,
            "Error in assignee method: Incorrect input in kwargs field!",
        )

    def test_manager_of_instance_assignee_no_assignee_type(self, mocked_process_step):
        kwargs = {"assignee_field": "profile", "test": "entry"}
        result = manager_of_instance_assignee(mocked_process_step, **kwargs)
        assert result is None
        mocked_process_step.step.get_casted_step().set_failed.assert_called_once_with(
            mocked_process_step,
            "Error in assignee method: Incorrect input in kwargs field!",
        )

    def test_manager_of_instance_assignee_wrong_assignee_field(self, mocked_process_step):
        kwargs = {"assignee_field": "profile", "assignee_type": "entry"}
        result = manager_of_instance_assignee(mocked_process_step, **kwargs)
        assert result is None
        mocked_process_step.step.get_casted_step().set_failed.assert_called_once_with(
            mocked_process_step,
            "Error in assignee method: Incorrect input in kwargs field!",
        )

    def test_manager_of_instance_assignee_wrong_assignee_type(self, mocked_process_step, mocked_active_user):
        kwargs = {"assignee_field": "profile", "assignee_type": "test"}
        mocked_process_step.process.instance = mocked_active_user
        result = manager_of_instance_assignee(mocked_process_step, **kwargs)
        assert result is None
        mocked_process_step.step.get_casted_step().set_failed.assert_called_once_with(
            mocked_process_step,
            "Error in assignee method: Incorrect input in kwargs field!",
        )

    def test_weighted_random_with_prior_assignments(self, mocker: MockerFixture, mocked_process_step, mocked_group):
        # Arrange
        user_a = mocker.MagicMock(spec=User, pk=1)
        user_b = mocker.MagicMock(spec=User, pk=2)
        mock_group_users = [user_a, user_b]

        mocked_group.user_set.all.return_value = mock_group_users
        mocked_group.user_set.count.return_value = len(mock_group_users)

        mocked_process_step.group = mocked_group
        mocked_process_step.process = mocker.MagicMock(spec=Process)

        mocked_choices = mocker.patch("wbcore.contrib.workflow.workflows.assignees.choices", return_value=[user_a])
        mocked_qs = mocker.patch("wbcore.contrib.workflow.workflows.assignees.ProcessStep.objects.filter")

        mocked_query = mocked_qs.return_value
        mocked_query.exclude.return_value.values_list.return_value = [1, 2, 2]
        # Act
        result = weighted_random(mocked_process_step)

        mocked_choices.assert_called_once_with(mock_group_users, weights=mocker.ANY)
        assignees, weights = (
            mocked_choices.call_args.args[0],
            mocked_choices.call_args.kwargs["weights"],
        )
        # Assert
        assert assignees == mock_group_users
        assert weights == pytest.approx([2 / 3, 1 / 3], rel=1e-2)
        assert result in mock_group_users

    def test_weighted_random_no_group(self, mocker: MockerFixture, mocked_process_step):
        # Arrange
        mocked_process_step.group = None
        mocked_failed_method = mocker.patch.object(mocked_process_step.step.get_casted_step(), "set_failed")
        # Act
        result = weighted_random(mocked_process_step)
        # Assert
        mocked_failed_method.assert_called_once()
        assert result is None

    def test_weighted_random_empty_group(self, mocker: MockerFixture, mocked_process_step, mocked_group):
        # Arrange
        mocked_group.user_set.count.return_value = 0
        mocked_process_step.group = mocked_group
        mocked_fail_method = mocker.patch.object(mocked_process_step.step.get_casted_step(), "set_failed")
        # Act
        result = weighted_random(mocked_process_step)
        # Assert
        mocked_fail_method.assert_called_once()
        assert result is None

    def test_weighted_random_no_prior_assignments(self, mocker: MockerFixture, mocked_process_step, mocked_group):
        # Arrange
        user_a = mocker.MagicMock(spec=User, pk=1)
        user_b = mocker.MagicMock(spec=User, pk=2)

        mock_group_users = [user_a, user_b]
        mocked_group.user_set.all.return_value = mock_group_users = [user_a, user_b]
        mocked_group.user_set.count.return_value = 2
        mocked_process_step.group = mocked_group

        mocked_choices = mocker.patch(
            "wbcore.contrib.workflow.workflows.assignees.choices",
            return_value=[user_b],
        )
        mocked_qs = mocker.patch("wbcore.contrib.workflow.workflows.assignees.ProcessStep.objects.filter")
        mocked_query = mocked_qs.return_value
        mocked_query.exclude.return_value.values_list.return_value = []
        # Act
        result = weighted_random(mocked_process_step)
        # Assert
        mocked_choices.assert_called_once_with(mock_group_users)
        assert result == user_b

    def test_weighted_random_single_user(self, mocker: MockerFixture, mocked_process_step, mocked_group):
        # Arrange
        user_a = mocker.MagicMock(spec=User, pk=1)
        mocked_group.user_set.all.return_value = [user_a]
        mocked_group.user_set.count.return_value = 1
        mocked_process_step.group = mocked_group
        mocked_process_step.process = mocker.MagicMock(spec=Process)

        mocked_qs = mocker.patch("wbcore.contrib.workflow.workflows.assignees.ProcessStep.objects.filter")

        mocked_query = mocked_qs.return_value
        mocked_query.exclude.return_value.values_list.return_value = []
        # Act
        result = weighted_random(mocked_process_step)
        # Assert
        assert result == user_a

    def test_random_group_member_multiple_users(self, mocker: MockerFixture, mocked_process_step, mocked_group):
        # Arrange
        mocked_process_step = mocker.MagicMock(spec=ProcessStep)

        user_a = mocker.MagicMock(spec=User)
        user_b = mocker.MagicMock(spec=User)
        user_c = mocker.MagicMock(spec=User)
        users = [user_a, user_b, user_c]

        mocked_group.user_set.exists.return_value = True
        mocked_group.user_set.count.return_value = 3
        mocked_group.user_set.all.return_value = users

        mocked_process_step.group = mocked_group

        mock_randint = mocker.patch("wbcore.contrib.workflow.workflows.assignees.randint", return_value=1)
        # Act
        result = random_group_member(mocked_process_step)
        # Assert
        mock_randint.assert_called_once_with(0, 2)
        assert result == user_b  # index 1

    def test_random_group_member_single_user(self, mocker: MockerFixture, mocked_process_step, mocked_group):
        # Arrange
        mocked_process_step = mocker.MagicMock(spec=ProcessStep)

        user_a = mocker.MagicMock(spec=User)
        mocked_group.user_set.exists.return_value = True
        mocked_group.user_set.count.return_value = 1
        mocked_group.user_set.all.return_value = [user_a]

        mocked_process_step.group = mocked_group
        # Act
        result = random_group_member(mocked_process_step)
        # Assert
        assert result == user_a

    def test_random_group_member_empty_group(self, mocker, mocked_process_step, mocked_group):
        # Arrange
        mocked_process_step.group = mocked_group
        mocked_process_step.group.user_set.exists.return_value = False

        mocked_set_failed = mocker.patch.object(mocked_process_step.step.get_casted_step(), "set_failed")
        # Act
        result = random_group_member(mocked_process_step)
        # Assert
        mocked_set_failed.assert_called_once()
        assert result is None

    def test_random_group_member_no_group(self, mocker, mocked_process_step):
        # Arrange
        mocked_process_step.group = None
        mocked_set_failed = mocker.patch.object(mocked_process_step.step.get_casted_step(), "set_failed")
        # Act
        result = random_group_member(mocked_process_step)
        # Assert
        mocked_set_failed.assert_called_once()
        assert result is None
