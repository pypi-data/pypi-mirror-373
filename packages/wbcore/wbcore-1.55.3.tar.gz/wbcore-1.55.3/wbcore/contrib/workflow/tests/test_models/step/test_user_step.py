from unittest.mock import patch

import pytest
from rest_framework.reverse import reverse
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.directory.factories import BankingContactFactory, PersonFactory
from wbcore.contrib.workflow.models import ProcessStep


@pytest.mark.django_db
class TestUserStep:
    def test_get_assigned_group(self, user_step_factory):
        user_step = user_step_factory()
        assert user_step.get_assigned_group() == user_step.group

    def test_get_assigned_user(self, user_step_factory):
        user = UserFactory()
        user_step = user_step_factory(assignee=user, group=None)
        assert user_step.get_assigned_user() == user

    def test_execute_assignee_method(self, process_step_factory, user_step_factory):
        step = user_step_factory()
        manager = PersonFactory()
        manager_account = UserFactory(profile=manager)
        assignee = PersonFactory(relationship_managers=[manager])
        instance = BankingContactFactory(entry=assignee)
        process_step = process_step_factory(step=step, process__instance=instance)
        process_step.step.execute_assignee_method(
            process_step, "manager_of_instance_assignee", assignee_field="entry", assignee_type="entry"
        )
        assert process_step.assignee == manager_account

    @patch("wbcore.contrib.workflow.models.step.UserStep.execute_assignee_method")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_run(self, mock_notify, mock_execute, process_step_factory, transition_factory, user_step_factory):
        kwargs = {"test": "Test"}
        step = user_step_factory(notify_user=True, kwargs=kwargs)
        user = UserFactory(groups=[step.group])
        process_step = process_step_factory(state=ProcessStep.StepState.ACTIVE, step=step)
        transition_factory(from_step=step)
        step.run(process_step)
        assert mock_notify.call_args.args == ([user], process_step)
        assert mock_execute.call_args.args == (process_step, step.assignee_method)
        assert mock_execute.call_args.kwargs == kwargs

    @patch("wbcore.contrib.workflow.models.step.UserStep.execute_assignee_method")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_run_no_kwargs(
        self, mock_notify, mock_execute, process_step_factory, transition_factory, user_step_factory
    ):
        step = user_step_factory(notify_user=True)
        user = UserFactory(groups=[step.group])
        process_step = process_step_factory(state=ProcessStep.StepState.ACTIVE, step=step)
        transition_factory(from_step=step)
        step.run(process_step)
        assert mock_notify.call_args.args == ([user], process_step)
        assert mock_execute.call_args.args == (process_step, step.assignee_method)
        assert mock_execute.call_args.kwargs == {}

    @patch("wbcore.contrib.workflow.models.step.UserStep.execute_assignee_method")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_run_no_notification(
        self, mock_notify, mock_execute, process_step_factory, transition_factory, user_step_factory
    ):
        kwargs = {"test": "Test"}
        step = user_step_factory(notify_user=False, kwargs=kwargs)
        UserFactory(groups=[step.group])
        process_step = process_step_factory(state=ProcessStep.StepState.ACTIVE, step=step)
        transition_factory(from_step=step)
        step.run(process_step)
        assert not mock_notify.called
        assert mock_execute.call_args.args == (process_step, step.assignee_method)
        assert mock_execute.call_args.kwargs == kwargs

    @patch("wbcore.contrib.workflow.models.step.UserStep.execute_assignee_method")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_run_assignee_method_failed(
        self, mock_notify, mock_execute, process_step_factory, transition_factory, user_step_factory
    ):
        kwargs = {"test": "Test"}
        step = user_step_factory(notify_user=True, kwargs=kwargs)
        UserFactory(groups=[step.group])
        process_step = process_step_factory(state=ProcessStep.StepState.FAILED, step=step)
        transition_factory(from_step=step)
        step.run(process_step)
        assert not mock_notify.called
        assert mock_execute.call_args.args == (process_step, step.assignee_method)
        assert mock_execute.call_args.kwargs == kwargs

    @patch("wbcore.contrib.workflow.models.step.UserStep.set_failed")
    @patch("wbcore.contrib.workflow.models.step.UserStep.execute_assignee_method")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_run_no_assignee(
        self, mock_notify, mock_execute, mock_failed, process_step_factory, transition_factory, user_step_factory
    ):
        kwargs = {"test": "Test"}
        step = user_step_factory(notify_user=True, kwargs=kwargs)
        process_step = process_step_factory(state=ProcessStep.StepState.ACTIVE, step=step)
        transition_factory(from_step=step)
        step.run(process_step)
        assert not mock_notify.called
        assert mock_execute.call_args.args == (process_step, step.assignee_method)
        assert mock_execute.call_args.kwargs == kwargs
        assert mock_failed.call_args.args[0] == process_step

    @patch("wbcore.contrib.workflow.models.step.UserStep.set_failed")
    @patch("wbcore.contrib.workflow.models.step.UserStep.execute_assignee_method")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_run_no_transition(
        self, mock_notify, mock_execute, mock_failed, process_step_factory, transition_factory, user_step_factory
    ):
        kwargs = {"test": "Test"}
        step = user_step_factory(notify_user=True, kwargs=kwargs)
        UserFactory(groups=[step.group])
        process_step = process_step_factory(state=ProcessStep.StepState.ACTIVE, step=step)
        step.run(process_step)
        assert not mock_notify.called
        assert mock_execute.call_args.args == (process_step, step.assignee_method)
        assert mock_execute.call_args.kwargs == kwargs
        assert mock_failed.call_args.args[0] == process_step

    @patch("wbcore.contrib.workflow.models.step.process_can_finish.delay")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_set_failed_user_step_notify_user(
        self, mock_notify, mock_can_finish, process_step_factory, user_step_factory
    ):
        step = user_step_factory(notify_user=True)
        UserFactory(groups=[step.group])
        process_step = process_step_factory(step=step, error_message=None)
        error_message = "Error message"
        step.set_failed(process_step, error_message)
        assert process_step.state == ProcessStep.StepState.FAILED
        assert process_step.error_message == error_message
        assert mock_notify.call_args.args == (process_step.get_all_assignees(), process_step, error_message)
        assert mock_can_finish.call_args.args == (process_step.process.pk,)

    @patch("wbcore.contrib.workflow.models.step.process_can_finish.delay")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_set_failed_user_step_not_notify(
        self, mock_notify, mock_can_finish, process_step_factory, user_step_factory
    ):
        step = user_step_factory(notify_user=False)
        UserFactory(groups=[step.group])
        process_step = process_step_factory(step=step, error_message=None)
        error_message = "Error message"
        step.set_failed(process_step, error_message)
        assert process_step.state == ProcessStep.StepState.FAILED
        assert process_step.error_message == error_message
        assert not mock_notify.called
        assert mock_can_finish.call_args.args == (process_step.process.pk,)

    @patch("wbcore.contrib.workflow.models.step.process_can_finish.delay")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_set_failed_user_step_no_assignees(
        self, mock_notify, mock_can_finish, process_step_factory, user_step_factory
    ):
        step = user_step_factory(notify_user=True)
        process_step = process_step_factory(step=step, error_message=None)
        error_message = "Error message"
        step.set_failed(process_step, error_message)
        assert process_step.state == ProcessStep.StepState.FAILED
        assert process_step.error_message == error_message
        assert not mock_notify.called
        assert mock_can_finish.call_args.args == (process_step.process.pk,)

    @patch("wbcore.contrib.workflow.models.step.send_notification")
    def test_notify_single_assignee(self, mock_notification, process_step_factory, user_step_factory):
        step = user_step_factory()
        process_step = process_step_factory(step=step)
        assignee_list = [UserFactory()]
        step.notify_assignees(assignee_list, process_step)
        assert mock_notification.call_args.kwargs == {
            "code": "workflow.userstep.notify_next_step",
            "title": "Workflow Step Awaiting Your Decision",
            "body": "You were assigned to a workflow step. Please select the next step.",
            "user": assignee_list[0],
            "endpoint": reverse(f"{process_step.get_endpoint_basename()}-detail", args=[process_step.id]),
        }

    @patch("wbcore.contrib.workflow.models.step.send_notification")
    def test_notify_assignee_error(self, mock_notification, process_step_factory, user_step_factory):
        step = user_step_factory()
        process_step = process_step_factory(step=step)
        assignee_list = [UserFactory()]
        error_message = "Test error"
        step.notify_assignees(assignee_list, process_step, error_message)
        assert mock_notification.call_args.kwargs == {
            "code": "workflow.userstep.notify_failed_step",
            "title": "Assigned Workflow Step Failed",
            "body": f"A workflow step you were assigned to just failed with the error message '{error_message}'. Please take appropriate action.",
            "user": assignee_list[0],
            "endpoint": reverse(f"{process_step.get_endpoint_basename()}-detail", args=[process_step.id]),
        }

    @patch("wbcore.contrib.workflow.models.step.send_notification")
    def test_notify_assignee_list(self, mock_notification, process_step_factory, user_step_factory):
        step = user_step_factory()
        process_step = process_step_factory(step=step)
        assignee_list = UserFactory.create_batch(3)
        step.notify_assignees(assignee_list, process_step)
        assert mock_notification.call_count == 3

    @patch("wbcore.contrib.workflow.models.step.send_notification")
    def test_notify_assignee_inactive_user(self, mock_notification, process_step_factory, user_step_factory):
        step = user_step_factory()
        process_step = process_step_factory(step=step)
        assignee_list = UserFactory.create_batch(3)
        inactive_user = UserFactory(is_active=False)
        assignee_list.append(inactive_user)
        step.notify_assignees(assignee_list, process_step)
        assert mock_notification.call_count == 3
        for call in mock_notification.call_args_list:
            assert call[1]["user"] != inactive_user

    @patch("wbcore.contrib.workflow.models.step.send_notification")
    @patch("wbcore.contrib.workflow.models.step.Step.user_can_see_step")
    def test_notify_assignee_user_cant_see(
        self, mock_can_see, mock_notification, process_step_factory, user_step_factory
    ):
        step = user_step_factory()
        process_step = process_step_factory(step=step)
        assignee_list = [UserFactory()]
        mock_can_see.return_value = False
        step.notify_assignees(assignee_list, process_step)
        assert not mock_notification.called
