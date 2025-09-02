from unittest.mock import patch

import pytest
from wbcore.contrib.authentication.factories import GroupFactory, UserFactory
from wbcore.contrib.authentication.models import Permission
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.contrib.directory.models import Person
from wbcore.contrib.workflow.factories import (
    FinishStepFactory,
    JoinStepFactory,
    UserStepFactory,
)
from wbcore.contrib.workflow.models import Condition, ProcessStep, Step
from wbcore.contrib.workflow.models.step import activate_step, process_can_finish
from wbcore.test.utils import get_or_create_superuser


@pytest.mark.django_db
class TestStep:
    @patch("wbcore.contrib.workflow.models.step.Step.run")
    def test_activate_step_no_status(self, mock_run, step_factory, process_factory):
        step = step_factory(status=None)
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.Step.run")
    def test_activate_step_no_instance(self, mock_run, step_factory, process_factory):
        step = step_factory()
        process = process_factory(workflow=step.workflow, instance=None, instance_id=None)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.Step.run")
    def test_activate_step_wrong_status_field(self, mock_run, step_factory, process_factory):
        step = step_factory(workflow__status_field="test")
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.Step.run")
    def test_activate_step_wrong_status_field_type(self, mock_run, step_factory, process_factory):
        step = step_factory(workflow__status_field="birthday")
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).birthday == process.instance.birthday
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.UserStep.run")
    def test_activate_user_step(self, mock_run, user_step_factory, process_factory):
        step = user_step_factory(permission=Permission.objects.last())
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            permission=step.permission,
            status=step.status,
            group=step.group,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.DecisionStep.run")
    def test_activate_decision_step(self, mock_run, decision_step_factory, process_factory):
        step = decision_step_factory()
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.SplitStep.run")
    def test_activate_split_step(self, mock_run, split_step_factory, process_factory):
        step = split_step_factory()
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.ScriptStep.run")
    def test_activate_script_step(self, mock_run, script_step_factory, process_factory):
        step = script_step_factory()
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.EmailStep.run")
    def test_activate_email_step(self, mock_run, email_step_factory, process_factory):
        step = email_step_factory()
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.FinishStep.run")
    def test_activate_finish_step(self, mock_run, finish_step_factory, process_factory):
        step = finish_step_factory()
        process = process_factory(workflow=step.workflow)
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.JoinStep.run")
    def test_activate_join_step(self, mock_run, process_step_factory, join_step_factory, process_factory):
        step = join_step_factory()
        process = process_factory(workflow=step.workflow)
        process_step_factory(
            state=ProcessStep.StepState.WAITING,
            step=step,
            status=step.status,
            process=process,
        )
        process_step_factory(
            state=ProcessStep.StepState.WAITING,
            step=step,
            status=step.status,
            finished=None,
        )
        process_step_factory()
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.JoinStep.run")
    def test_activate_step_too_many_waiting_steps(
        self, mock_run, process_step_factory, join_step_factory, process_factory
    ):
        step = join_step_factory()
        process = process_factory(workflow=step.workflow)
        process_step_factory(
            state=ProcessStep.StepState.WAITING,
            step=step,
            status=step.status,
            process=process,
            finished=None,
        )
        process_step_factory(
            state=ProcessStep.StepState.WAITING,
            step=step,
            status=step.status,
            process=process,
            finished=None,
        )
        process_step_factory()
        activate_step(step.pk, process.pk)
        process_step_qs = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        )
        assert process_step_qs.count() == 1
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert mock_run.call_args.args == (process_step_qs.first(),)

    @patch("wbcore.contrib.workflow.models.step.JoinStep.run")
    def test_activate_waiting_join_step(self, mock_run, process_step_factory, join_step_factory, process_factory):
        step = join_step_factory()
        process = process_factory(workflow=step.workflow)
        process_step_factory(
            state=ProcessStep.StepState.WAITING,
            step=step,
            status=step.status,
            process=process,
        )
        waiting_process_step = process_step_factory(
            state=ProcessStep.StepState.WAITING,
            step=step,
            status=step.status,
            process=process,
            finished=None,
        )
        process_step_factory()
        activate_step(step.pk, process.pk)
        assert not ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process=process,
            step=step,
            status=step.status,
        ).exists()
        assert Person.objects.get(id=process.instance.pk).first_name == step.status
        assert str(mock_run.call_args.args[0].pk) == waiting_process_step.pk

    def test_get_outgoing_transitions(self, random_child_step_factory, transition_factory):
        step = random_child_step_factory()
        transition = transition_factory(from_step=step)
        transition_factory()
        transition_factory(to_step=step)
        assert list(step.get_outgoing_transitions()) == [transition]

    def test_get_incoming_transitions(self, random_child_step_factory, transition_factory):
        step = random_child_step_factory()
        transition_factory(from_step=step)
        transition_factory()
        transition = transition_factory(to_step=step)
        assert list(step.get_incoming_transitions()) == [transition]

    def test_get_previous_steps(
        self,
        join_step_factory,
        split_step_factory,
        finish_step_factory,
        transition_factory,
    ):
        to_step = join_step_factory()
        from_step = split_step_factory()
        transition1 = transition_factory(to_step=to_step, from_step=from_step)
        transition2 = transition_factory(to_step=to_step, from_step=from_step)
        transition_factory(to_step=finish_step_factory(), from_step=to_step)
        transition_factory()
        previous_steps = to_step.get_previous_steps()
        previous_steps = [step.id for step in previous_steps]
        assert set(previous_steps) == {
            transition1.from_step.id,
            transition2.from_step.id,
        }

    def test_get_all_valid_outgoing_transitions(
        self,
        random_child_step_factory,
        transition_factory,
        condition_factory,
        process_step_factory,
    ):
        person = PersonFactory()
        step = random_child_step_factory()
        invalid_transition = transition_factory(from_step=step, to_step__workflow=step.workflow)
        condition_factory(
            transition=invalid_transition,
            attribute_name="first_name",
            expected_value=person.first_name,
            operator=Condition.Operator.EQ,
            negate_operator=True,
        )
        condition_factory(
            transition=invalid_transition,
            attribute_name="last_name",
            expected_value=person.last_name,
            operator=Condition.Operator.EQ,
            negate_operator=False,
        )
        valid_transition = transition_factory(from_step=step, to_step__workflow=step.workflow)
        condition_factory(
            transition=valid_transition,
            attribute_name="first_name",
            expected_value=person.first_name,
            operator=Condition.Operator.EQ,
            negate_operator=False,
        )
        valid_transition_without_condition = transition_factory(from_step=step, to_step__workflow=step.workflow)
        process_step = process_step_factory(step=step, process__instance=person)
        transitions = step.get_all_valid_outgoing_transitions(process_step)
        assert set(transitions) == {
            valid_transition,
            valid_transition_without_condition,
        }

    def test_get_assigned_group(self, random_child_step_factory):
        random_step = random_child_step_factory(exclude_factories=[UserStepFactory])
        assert random_step.get_assigned_group() is None

    def test_get_assigned_user(self, random_child_step_factory):
        random_step = random_child_step_factory(exclude_factories=[UserStepFactory])
        assert random_step.get_assigned_user() is None

    def test_get_casted_step(self, random_child_step_factory):
        random_step_child = random_child_step_factory()
        parent_step = random_step_child.step_ptr
        assert parent_step.get_casted_step().__class__ == random_step_child.__class__

    def test_user_can_see_step_user_permission(self, random_child_step_factory):
        step = random_child_step_factory(permission=Permission.objects.last())
        user = UserFactory()
        user.user_permissions.add(step.permission)
        assert step.user_can_see_step(user)

    def test_user_can_see_step_no_permission(self, random_child_step_factory):
        step = random_child_step_factory()
        user = UserFactory()
        assert step.user_can_see_step(user)

    def test_user_can_see_step_superuser(self, random_child_step_factory):
        step = random_child_step_factory(permission=Permission.objects.last())
        user = get_or_create_superuser()
        assert step.user_can_see_step(user)

    def test_user_can_see_step_group_permission(self, random_child_step_factory):
        step = random_child_step_factory(permission=Permission.objects.last())
        group = GroupFactory(permissions=[step.permission])
        user = UserFactory(groups=[group])
        assert step.user_can_see_step(user)

    def test_user_can_see_step_user_no_permission(self, random_child_step_factory):
        step = random_child_step_factory(permission=Permission.objects.last())
        user = UserFactory()
        assert not step.user_can_see_step(user)

    @patch("wbcore.contrib.workflow.models.step.Step.finish")
    def test_set_finished(self, mock_finish, process_step_factory, random_child_step_factory):
        step = random_child_step_factory(exclude_factories=[FinishStepFactory])
        process_step = process_step_factory(step=step)
        step.set_finished(process_step)
        assert process_step.state == ProcessStep.StepState.FINISHED
        assert mock_finish.call_args.args == (process_step,)

    @patch("wbcore.contrib.workflow.models.step.FinishStep.finish")
    def test_set_finished_finish_step(self, mock_finish, process_step_factory, finish_step_factory):
        step = finish_step_factory()
        process_step = process_step_factory(step=step)
        step.set_finished(process_step)
        assert process_step.state == ProcessStep.StepState.FINISHED
        assert mock_finish.call_args.args == (process_step,)

    @patch("wbcore.contrib.workflow.models.step.process_can_finish.delay")
    def test_set_failed(self, mock_can_finish, process_step_factory, random_child_step_factory):
        step = random_child_step_factory()
        process_step = process_step_factory(step=step, error_message=None)
        error_message = "Error message"
        step.set_failed(process_step, error_message)
        assert process_step.state == ProcessStep.StepState.FAILED
        assert process_step.error_message == error_message
        assert mock_can_finish.call_args.args == (process_step.process.pk,)

    @patch("wbcore.contrib.workflow.models.step.process_can_finish.delay")
    def test_set_failed_has_error_message(self, mock_can_finish, process_step_factory, random_child_step_factory):
        step = random_child_step_factory()
        error_message = "Error message"
        process_step = process_step_factory(step=step, error_message=error_message)
        step.set_failed(process_step, "Test")
        assert process_step.state == ProcessStep.StepState.FAILED
        assert process_step.error_message == error_message
        assert mock_can_finish.call_args.args == (process_step.process.pk,)

    @patch("wbcore.contrib.workflow.models.step.Step.finish")
    def test_set_canceled(self, mock_finish, process_step_factory, random_child_step_factory):
        step = random_child_step_factory(exclude_factories=[FinishStepFactory])
        process_step = process_step_factory(step=step)
        step.set_canceled(process_step)
        assert process_step.state == ProcessStep.StepState.CANCELED
        assert mock_finish.call_args.args == (process_step,)

    @patch("wbcore.contrib.workflow.models.step.FinishStep.finish")
    def test_set_canceled_finish_step(self, mock_finish, process_step_factory, finish_step_factory):
        step = finish_step_factory()
        process_step = process_step_factory(step=step)
        step.set_canceled(process_step)
        assert process_step.state == ProcessStep.StepState.CANCELED
        assert mock_finish.call_args.args == (process_step,)

    @patch("wbcore.contrib.workflow.models.step.Step.start_next_step")
    def test_execute_single_next_step(
        self,
        mock_next,
        process_step_factory,
        transition_factory,
        random_child_step_factory,
    ):
        step = random_child_step_factory()
        process_step = process_step_factory(step=step)
        transition = transition_factory(from_step=step)
        transition_factory()
        step.execute_single_next_step(process_step)
        assert mock_next.call_args.args == (process_step, transition)

    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    def test_execute_single_next_step_no_transitions(
        self,
        mock_failed,
        process_step_factory,
        transition_factory,
        random_child_step_factory,
    ):
        step = random_child_step_factory(exclude_factories=[UserStepFactory])
        process_step = process_step_factory(step=step)
        transition_factory()
        step.execute_single_next_step(process_step)
        assert mock_failed.call_args.args[0] == process_step

    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    def test_execute_single_next_step_multiple_transitions(
        self,
        mock_failed,
        process_step_factory,
        transition_factory,
        random_child_step_factory,
    ):
        step = random_child_step_factory(exclude_factories=[UserStepFactory])
        process_step = process_step_factory(step=step)
        transition_factory(from_step=step)
        transition_factory(from_step=step)
        step.execute_single_next_step(process_step)
        assert mock_failed.call_args.args[0] == process_step

    @patch("wbcore.contrib.workflow.models.step.Step.set_finished")
    def test_run(self, mock_finished, process_step_factory):
        process_step = process_step_factory()
        step = process_step.step
        step.run(process_step)
        assert mock_finished.call_args.args == (process_step,)

    @pytest.mark.parametrize(
        "state, expected",
        [
            ("Finished", True),
            ("Canceled", True),
            ("Active", False),
            ("Waiting", False),
            ("Failed", False),
        ],
    )
    def test_finish(self, state, expected, process_step_factory, random_child_step_factory):
        step = random_child_step_factory(exclude_factories=[FinishStepFactory])
        process_step = process_step_factory(step=step, state=state, finished=None)
        step.finish(process_step)
        assert bool(process_step.finished) is expected

    @patch("wbcore.contrib.workflow.models.step.activate_step.delay")
    @patch("wbcore.contrib.workflow.models.step.Step.set_finished")
    def test_start_next_step(self, mock_finish, mock_activate, transition_factory, process_step_factory):
        transition = transition_factory()
        process_step = process_step_factory()
        Step.start_next_step(process_step, transition)
        assert mock_finish.call_args.args == (process_step,)
        assert mock_activate.call_args.args == (
            transition.to_step.pk,
            process_step.process.pk,
        )

    @patch("wbcore.contrib.workflow.models.process.Process.set_failed")
    def test_process_can_finish_no_active(self, mock_failed, process_step_factory):
        process_step = process_step_factory(state=ProcessStep.StepState.CANCELED)
        process = process_step.process
        process_step_factory(state=ProcessStep.StepState.FINISHED, process=process)
        process_step_factory(state=ProcessStep.StepState.FAILED, process=process)
        process_step_factory(state=ProcessStep.StepState.ACTIVE)
        process_can_finish(process.pk)
        assert mock_failed.call_count == 1

    @patch("wbcore.contrib.workflow.models.process.Process.set_failed")
    def test_process_can_finish_no_join_steps(
        self,
        mock_failed,
        process_step_factory,
        random_child_step_factory,
        process_factory,
    ):
        step = random_child_step_factory(exclude_factories=[JoinStepFactory])
        process = process_factory(workflow=step.workflow)
        process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE, process=process)
        process_can_finish(process.pk)
        assert not mock_failed.called

    # """
    # Test Workflow:
    #                          8
    #                        /   \                    # noqa: W605
    #              4 - 6 - 7       14
    #            /           \   /    \               # noqa: W605
    #           /              9        \             # noqa: W605
    # 1 - 2 - 3                            16 - 17
    #           \               12       /            # noqa: W605
    #            \             /  \    /              # noqa: W605
    #              5 - 10 - 11      15
    #                          \  /                   # noqa: W605
    #                           13
    # """

    @patch("wbcore.contrib.workflow.models.process.Process.set_failed")
    def test_process_can_finish_join_steps_can_be_reached(
        self,
        mock_failed,
        workflow_factory,
        split_step_factory,
        process_factory,
        process_step_factory,
        random_child_step_factory,
        start_step_factory,
        transition_factory,
        join_step_factory,
        finish_step_factory,
    ):
        workflow = workflow_factory()
        step1 = start_step_factory(workflow=workflow)
        step2 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step1, to_step=step2)
        step3 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step2, to_step=step3)
        step4 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step5 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step3, to_step=step4)
        transition_factory(from_step=step3, to_step=step5)
        step6 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step4, to_step=step6)
        step7 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step6, to_step=step7)
        step8 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step9 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step7, to_step=step8)
        transition_factory(from_step=step7, to_step=step9)
        step10 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step5, to_step=step10)
        step11 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step10, to_step=step11)
        step12 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step13 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step11, to_step=step12)
        transition_factory(from_step=step11, to_step=step13)
        step14 = join_step_factory(wait_for_all=True, workflow=workflow)
        transition_factory(from_step=step8, to_step=step14)
        transition_factory(from_step=step9, to_step=step14)
        step15 = join_step_factory(wait_for_all=False, workflow=workflow)
        transition_factory(from_step=step12, to_step=step15)
        transition_factory(from_step=step13, to_step=step15)
        step16 = join_step_factory(wait_for_all=True, workflow=workflow)
        transition_factory(from_step=step14, to_step=step16)
        transition_factory(from_step=step15, to_step=step16)
        step17 = finish_step_factory(workflow=workflow)
        transition_factory(from_step=step16, to_step=step17)

        process = process_factory(workflow=workflow)
        process_step_factory(step=step12, state=ProcessStep.StepState.FAILED, process=process)
        process_step_factory(step=step11, state=ProcessStep.StepState.ACTIVE, process=process)
        for step in [
            step1,
            step2,
            step3,
            step4,
            step5,
            step6,
            step7,
            step8,
            step9,
            step10,
            step14,
        ]:
            process_step_factory(step=step, state=ProcessStep.StepState.FINISHED, process=process)
        process_can_finish(process.pk)
        assert not mock_failed.called

    @patch("wbcore.contrib.workflow.models.process.Process.set_failed")
    def test_process_can_finish_waiting_join_step_one_failed(
        self,
        mock_failed,
        workflow_factory,
        split_step_factory,
        process_factory,
        process_step_factory,
        random_child_step_factory,
        start_step_factory,
        transition_factory,
        join_step_factory,
        finish_step_factory,
    ):
        workflow = workflow_factory()
        step1 = start_step_factory(workflow=workflow)
        step2 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step1, to_step=step2)
        step3 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step2, to_step=step3)
        step4 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step5 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step3, to_step=step4)
        transition_factory(from_step=step3, to_step=step5)
        step6 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step4, to_step=step6)
        step7 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step6, to_step=step7)
        step8 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step9 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step7, to_step=step8)
        transition_factory(from_step=step7, to_step=step9)
        step10 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step5, to_step=step10)
        step11 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step10, to_step=step11)
        step12 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step13 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step11, to_step=step12)
        transition_factory(from_step=step11, to_step=step13)
        step14 = join_step_factory(wait_for_all=True, workflow=workflow)
        transition_factory(from_step=step8, to_step=step14)
        transition_factory(from_step=step9, to_step=step14)
        step15 = join_step_factory(wait_for_all=False, workflow=workflow)
        transition_factory(from_step=step12, to_step=step15)
        transition_factory(from_step=step13, to_step=step15)
        step16 = join_step_factory(wait_for_all=True, workflow=workflow)
        transition_factory(from_step=step14, to_step=step16)
        transition_factory(from_step=step15, to_step=step16)
        step17 = finish_step_factory(workflow=workflow)
        transition_factory(from_step=step16, to_step=step17)

        process = process_factory(workflow=workflow)
        process_step_factory(step=step8, state=ProcessStep.StepState.FAILED, process=process)
        process_step_factory(step=step14, state=ProcessStep.StepState.WAITING, process=process)
        for step in [
            step1,
            step2,
            step3,
            step4,
            step5,
            step6,
            step7,
            step9,
            step10,
            step11,
            step12,
            step13,
            step15,
        ]:
            process_step_factory(step=step, state=ProcessStep.StepState.FINISHED, process=process)
        process_can_finish(process.pk)
        assert mock_failed.called

    @patch("wbcore.contrib.workflow.models.process.Process.set_failed")
    def test_process_can_finish_failed_at_beginning(
        self,
        mock_failed,
        workflow_factory,
        split_step_factory,
        process_factory,
        process_step_factory,
        random_child_step_factory,
        start_step_factory,
        transition_factory,
        join_step_factory,
        finish_step_factory,
    ):
        workflow = workflow_factory()
        step1 = start_step_factory(workflow=workflow)
        step2 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step1, to_step=step2)
        step3 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step2, to_step=step3)
        step4 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step5 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step3, to_step=step4)
        transition_factory(from_step=step3, to_step=step5)
        step6 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step4, to_step=step6)
        step7 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step6, to_step=step7)
        step8 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step9 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step7, to_step=step8)
        transition_factory(from_step=step7, to_step=step9)
        step10 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step5, to_step=step10)
        step11 = split_step_factory(workflow=workflow)
        transition_factory(from_step=step10, to_step=step11)
        step12 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        step13 = random_child_step_factory(exclude_factories=[JoinStepFactory], workflow=workflow)
        transition_factory(from_step=step11, to_step=step12)
        transition_factory(from_step=step11, to_step=step13)
        step14 = join_step_factory(wait_for_all=True, workflow=workflow)
        transition_factory(from_step=step8, to_step=step14)
        transition_factory(from_step=step9, to_step=step14)
        step15 = join_step_factory(wait_for_all=False, workflow=workflow)
        transition_factory(from_step=step12, to_step=step15)
        transition_factory(from_step=step13, to_step=step15)
        step16 = join_step_factory(wait_for_all=True, workflow=workflow)
        transition_factory(from_step=step14, to_step=step16)
        transition_factory(from_step=step15, to_step=step16)
        step17 = finish_step_factory(workflow=workflow)
        transition_factory(from_step=step16, to_step=step17)

        process = process_factory(workflow=workflow)
        process_step_factory(step=step6, state=ProcessStep.StepState.FAILED, process=process)
        process_step_factory(step=step15, state=ProcessStep.StepState.ACTIVE, process=process)
        for step in [
            step1,
            step2,
            step3,
            step4,
            step5,
            step10,
            step11,
            step12,
            step13,
            step15,
        ]:
            process_step_factory(step=step, state=ProcessStep.StepState.FINISHED, process=process)
        process_can_finish(process.pk)
        assert mock_failed.called
