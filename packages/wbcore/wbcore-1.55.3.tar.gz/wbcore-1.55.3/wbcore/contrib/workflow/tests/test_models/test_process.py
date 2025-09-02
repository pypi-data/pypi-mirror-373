from unittest.mock import patch

import pytest
from wbcore.contrib.authentication.factories import GroupFactory, UserFactory
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.contrib.workflow.factories import UserStepFactory
from wbcore.contrib.workflow.models import Process, ProcessStep


@pytest.mark.django_db
class TestProcess:
    @patch("wbcore.contrib.workflow.models.process.ProcessStep.get_all_assignees")
    @patch("wbcore.contrib.workflow.models.step.UserStep.notify_assignees")
    def test_set_failed(
        self,
        mock_notify,
        mock_assignees,
        process_step_factory,
        process_factory,
        random_child_step_factory,
        user_step_factory,
    ):
        step = random_child_step_factory(exclude_factories=[UserStepFactory])
        user_step_no_notify = user_step_factory(notify_user=False)
        user_step_notify = user_step_factory(notify_user=True)
        process = process_factory(state=Process.ProcessState.ACTIVE)
        process_step1 = process_step_factory(
            state=ProcessStep.StepState.ACTIVE, process=process, step=step, error_message=None
        )
        process_step2 = process_step_factory(
            state=ProcessStep.StepState.WAITING, process=process, step=step, error_message=None
        )
        process_step3 = process_step_factory(
            state=ProcessStep.StepState.CANCELED, process=process, step=step, error_message=None
        )
        process_step4 = process_step_factory(
            state=ProcessStep.StepState.FINISHED, process=process, step=step, error_message=None
        )
        process_step5 = process_step_factory(state=ProcessStep.StepState.ACTIVE, step=step, error_message=None)
        process_step6 = process_step_factory(
            state=ProcessStep.StepState.ACTIVE, process=process, step=user_step_no_notify, error_message=None
        )
        process_step7 = process_step_factory(
            state=ProcessStep.StepState.ACTIVE, process=process, step=user_step_notify, error_message=None
        )
        user = UserFactory()
        mock_assignees.return_value = [user]
        process.set_failed()
        assert mock_notify.call_count == 1
        assert mock_notify.call_args.args[0] == [user]
        assert str(mock_notify.call_args.args[1].pk) == process_step7.pk
        assert mock_assignees.call_count == 1
        for process_step in ProcessStep.objects.filter(
            id__in=[process_step1.pk, process_step2.pk, process_step6.pk, process_step7.pk]
        ):
            assert process_step.state == ProcessStep.StepState.FAILED
            assert process_step.error_message
        for process_step in ProcessStep.objects.filter(id__in=[process_step3.pk, process_step4.pk, process_step5.pk]):
            assert process_step.state != ProcessStep.StepState.FAILED
            assert process_step.error_message is None
        assert Process.objects.get(id=process.pk).state == Process.ProcessState.FAILED


@pytest.mark.django_db
class TestProcessStep:
    def test_get_instance(self, process_step_factory):
        attached_instance = PersonFactory()
        process_step = process_step_factory(process__instance=attached_instance)
        assert process_step.get_instance() == attached_instance

    def test_get_instance_no_attached(self, process_step_factory):
        process_step = process_step_factory(process__instance=None, process__instance_id=None)
        assert process_step.get_instance() is None

    def test_get_all_assignees_assignee(self, process_step_factory):
        user = UserFactory()
        group = GroupFactory()
        process_step = process_step_factory(assignee=user, group=group)
        assert process_step.get_all_assignees() == [user]

    def test_get_all_assignees_group(self, process_step_factory):
        group = GroupFactory()
        user1 = UserFactory(groups=[group])
        user2 = UserFactory(groups=[group])
        UserFactory()
        process_step = process_step_factory(group=group, assignee=None)
        assert set(process_step.get_all_assignees()) == {user1, user2}

    def test_get_all_assignees_empty_group(self, process_step_factory):
        group = GroupFactory()
        process_step = process_step_factory(group=group, assignee=None)
        assert process_step.get_all_assignees() == []

    def test_get_all_assignees_none(self, process_step_factory):
        group = GroupFactory()
        UserFactory(groups=[group])
        process_step = process_step_factory(group=None, assignee=None)
        assert process_step.get_all_assignees() == []
