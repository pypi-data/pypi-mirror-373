from unittest.mock import patch

import factory
import pytest
from django.contrib.contenttypes.models import ContentType
from wbcore.contrib.authentication.factories import GroupFactory, UserFactory
from wbcore.contrib.authentication.models import Permission
from wbcore.contrib.directory.factories import CompanyFactory, PersonFactory
from wbcore.contrib.directory.models import Person
from wbcore.contrib.workflow.models import (
    Condition,
    DataValue,
    Process,
    ProcessStep,
    Transition,
    Workflow,
)
from wbcore.contrib.workflow.models.workflow import re_render_workflow_graph
from wbcore.contrib.workflow.sites import workflow_site
from wbcore.test.utils import get_or_create_superuser


@pytest.mark.django_db
class TestWorkflow:
    @patch("wbcore.contrib.workflow.models.workflow.transaction.on_commit")
    def test_start_workflow_without_attached_instance(
        self, mock_commit, workflow_factory, data_factory, start_step_factory
    ):
        workflow = workflow_factory(model=None, status_field=None, preserve_instance=False)
        data1 = data_factory(workflow=workflow)
        default_value = "Test"
        data2 = data_factory(workflow=workflow, default=default_value)
        start_step = start_step_factory(workflow=workflow)
        workflow.start_workflow(start_step)
        process_qs = Process.objects.filter(workflow=workflow, instance_id=None, content_type=None)
        assert process_qs.exists()
        assert DataValue.objects.filter(data=data1, process=process_qs.first()).exists()
        assert DataValue.objects.filter(data=data2, process=process_qs.first(), value=default_value).exists()
        assert mock_commit.called

    @patch("wbcore.contrib.workflow.models.workflow.transaction.on_commit")
    def test_start_workflow_with_attached_instance(
        self, mock_commit, workflow_factory, start_step_factory, data_factory
    ):
        attached_person = PersonFactory()
        workflow = workflow_factory(preserve_instance=True)
        data1 = data_factory(workflow=workflow)
        default_value = "Test"
        data2 = data_factory(workflow=workflow, default=default_value)
        start_step = start_step_factory()
        workflow_site.registered_model_classes_serializer_map[Person] = (
            "wbcore.contrib.directory.serializers.PersonModelSerializer"
        )
        workflow.start_workflow(start_step, attached_person)
        process_qs = Process.objects.filter(
            workflow=workflow,
            instance_id=attached_person.pk,
            content_type=ContentType.objects.get_for_model(Person),
            preserved_instance__isnull=False,
        )
        assert process_qs.exists()
        assert DataValue.objects.filter(data=data1, process=process_qs.first()).exists()
        assert DataValue.objects.filter(data=data2, process=process_qs.first(), value=default_value).exists()
        assert mock_commit.called

    def test_get_start_steps_for_workflow(self, workflow_factory, start_step_factory):
        workflow = workflow_factory(model=None, single_instance_execution=False, status_field=None)
        start_step = start_step_factory(workflow=workflow)
        start_step_factory()
        start_transitions = workflow.get_start_steps_for_workflow()
        assert list(start_transitions) == [start_step]

    def test_get_start_steps_for_workflow_single_instance_execution(
        self, workflow_factory, process_factory, start_step_factory
    ):
        workflow = workflow_factory(model=None, single_instance_execution=True, status_field=None)
        start_step_factory(workflow=workflow)
        start_step_factory()
        process_factory(state=Process.ProcessState.ACTIVE, workflow=workflow)
        assert not workflow.get_start_steps_for_workflow().exists()

    def test_get_start_steps_for_workflow_single_instance_execution_no_running_process(
        self, workflow_factory, process_factory, start_step_factory
    ):
        workflow = workflow_factory(model=None, single_instance_execution=True, status_field=None)
        start_step = start_step_factory(workflow=workflow)
        start_step_factory()
        process_factory(state=Process.ProcessState.FINISHED, workflow=workflow)
        start_transitions = workflow.get_start_steps_for_workflow()
        assert list(start_transitions) == [start_step]

    def test_get_start_steps_for_workflow_with_attached_instance(self, workflow_factory, start_step_factory):
        workflow = workflow_factory()
        start_step_factory(workflow=workflow)
        start_step_factory()
        assert not workflow.get_start_steps_for_workflow().exists()

    def test_get_start_steps_for_instance(self, workflow_factory, start_step_factory):
        person = PersonFactory()
        workflow = workflow_factory()
        start_step = start_step_factory(workflow=workflow, status=person.first_name)
        start_step_factory(workflow=workflow)
        assert Workflow.get_start_steps_for_instance(person) == [start_step]

    def test_get_start_steps_for_instance_no_model_attached(self, workflow_factory, start_step_factory):
        person = PersonFactory()
        workflow = workflow_factory(model=None, status_field=None)
        start_step_factory(workflow=workflow, status=person.first_name)
        assert not Workflow.get_start_steps_for_instance(person)

    def test_get_start_steps_for_instance_wrong_instance(self, workflow_factory, start_step_factory):
        company = CompanyFactory()
        workflow = workflow_factory()
        start_step_factory(workflow=workflow)
        assert not Workflow.get_start_steps_for_instance(company)

    def test_get_start_steps_for_instance_single_instance_execution(
        self, workflow_factory, process_factory, start_step_factory
    ):
        person = PersonFactory()
        workflow = workflow_factory(single_instance_execution=True)
        start_step_factory(workflow=workflow, status=person.first_name)
        process_factory(finished=None, workflow=workflow, instance=person)
        assert not Workflow.get_start_steps_for_instance(person)

    def test_get_start_steps_for_instance_single_instance_execution_no_running_process(
        self, workflow_factory, process_factory, start_step_factory
    ):
        attached_instance = PersonFactory()
        workflow = workflow_factory(single_instance_execution=True)
        start_step = start_step_factory(workflow=workflow, status=attached_instance.first_name)
        start_step_factory()
        process_factory(workflow=workflow, instance=attached_instance)
        wrong_instance = CompanyFactory()
        process_factory(workflow=workflow, finished=None, instance=wrong_instance)
        assert Workflow.get_start_steps_for_instance(attached_instance) == [start_step]

    def test_get_start_steps_for_instance_wrong_status_field(self, workflow_factory, start_step_factory):
        person = PersonFactory()
        workflow = workflow_factory(status_field="Test")
        start_step_factory(workflow=workflow, status=person.first_name)
        assert not Workflow.get_start_steps_for_instance(person)

    def test_get_start_steps_for_instance_wrong_status(self, workflow_factory, start_step_factory):
        person = PersonFactory()
        workflow = workflow_factory()
        start_step_factory(workflow=workflow, status="Test")
        assert not Workflow.get_start_steps_for_instance(person)

    def test_get_next_user_step_transitions_for_instance_superuser(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        step = user_step_factory(workflow=workflow, permission=Permission.objects.last())
        transition = transition_factory(from_step=step, to_step__workflow=workflow)
        process_step = process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE)
        attached_instance = process_step.process.instance
        superuser = get_or_create_superuser()
        start_transitions = Workflow.get_next_user_step_transitions_for_instance(attached_instance, superuser)
        assert start_transitions[0][0] == [transition]
        assert str(start_transitions[0][1].pk) == process_step.pk

    def test_get_next_user_step_transitions_for_instance_wrong_instance(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        instance = PersonFactory()
        step = user_step_factory(workflow=workflow, permission=Permission.objects.last())
        transition_factory(from_step=step, to_step__workflow=workflow)
        process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE)
        superuser = get_or_create_superuser()
        assert not Workflow.get_next_user_step_transitions_for_instance(instance, superuser)

    def test_get_next_user_step_transitions_for_instance_user_is_assignee(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        step = user_step_factory(workflow=workflow)
        transition = transition_factory(from_step=step, to_step__workflow=workflow)
        user = UserFactory()
        process_step = process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE, assignee=user)
        attached_instance = process_step.process.instance
        start_transitions = Workflow.get_next_user_step_transitions_for_instance(attached_instance, user)
        assert start_transitions[0][0] == [transition]
        assert str(start_transitions[0][1].pk) == process_step.pk

    def test_get_next_user_step_transitions_for_instance_user_in_assignee_group(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        step = user_step_factory(workflow=workflow, assignee_method=None)
        transition = transition_factory(from_step=step, to_step__workflow=workflow)
        group = GroupFactory()
        user = UserFactory(groups=[group])
        process_step = process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE, group=group)
        attached_instance = process_step.process.instance
        start_transitions = Workflow.get_next_user_step_transitions_for_instance(attached_instance, user)
        assert start_transitions[0][0] == [transition]
        assert str(start_transitions[0][1].pk) == process_step.pk

    def test_get_next_user_step_transitions_for_instance_user_in_assignee_group_but_with_method(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        step = user_step_factory(workflow=workflow, permission=Permission.objects.last())
        transition_factory(from_step=step, to_step__workflow=workflow)
        group = GroupFactory()
        user = UserFactory(groups=[group])
        process_step = process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE, group=group)
        attached_instance = process_step.process.instance
        assert not Workflow.get_next_user_step_transitions_for_instance(attached_instance, user)

    def test_get_next_user_step_transitions_for_instance_user_has_permission(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        step = user_step_factory(workflow=workflow, permission=Permission.objects.last())
        transition = transition_factory(from_step=step, to_step__workflow=workflow)
        user = UserFactory()
        user.user_permissions.add(step.permission)
        process_step = process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE, assignee=user)
        attached_instance = process_step.process.instance
        start_transitions = Workflow.get_next_user_step_transitions_for_instance(attached_instance, user)
        assert start_transitions[0][0] == [transition]
        assert str(start_transitions[0][1].pk) == process_step.pk

    def test_get_next_user_step_transitions_for_instance_user_has_group_permission(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        step = user_step_factory(workflow=workflow, permission=Permission.objects.last())
        transition = transition_factory(from_step=step, to_step__workflow=workflow)
        group = GroupFactory(permissions=[step.permission])
        user = UserFactory(groups=[group])
        process_step = process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE, assignee=user)
        attached_instance = process_step.process.instance
        start_transitions = Workflow.get_next_user_step_transitions_for_instance(attached_instance, user)
        assert start_transitions[0][0] == [transition]
        assert str(start_transitions[0][1].pk) == process_step.pk

    def test_get_next_user_step_transitions_for_instance_user_has_no_permission(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        step = user_step_factory(workflow=workflow, permission=Permission.objects.last())
        transition_factory(from_step=step, to_step__workflow=workflow)
        user = UserFactory()
        process_step = process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE, assignee=user)
        attached_instance = process_step.process.instance
        assert not Workflow.get_next_user_step_transitions_for_instance(attached_instance, user)

    def test_get_next_user_step_transitions_for_instance_user_no_permission_selected(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory
    ):
        workflow = workflow_factory()
        step = user_step_factory(workflow=workflow)
        transition = transition_factory(from_step=step, to_step__workflow=workflow)
        user = UserFactory()
        process_step = process_step_factory(step=step, state=ProcessStep.StepState.ACTIVE, assignee=user)
        attached_instance = process_step.process.instance
        start_transitions = Workflow.get_next_user_step_transitions_for_instance(attached_instance, user)
        assert start_transitions[0][0] == [transition]
        assert str(start_transitions[0][1].pk) == process_step.pk

    def test_get_next_user_step_transitions_for_instance_condition_satisfied(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory, condition_factory
    ):
        workflow = workflow_factory()
        person = PersonFactory()
        step = user_step_factory(workflow=workflow)
        transition = transition_factory(from_step=step, to_step__workflow=workflow)
        condition_factory(
            transition=transition,
            attribute_name="first_name",
            expected_value=person.first_name,
            operator=Condition.Operator.EQ,
            negate_operator=False,
        )
        superuser = get_or_create_superuser()
        process_step = process_step_factory(
            step=step, state=ProcessStep.StepState.ACTIVE, assignee=superuser, process__instance=person
        )
        start_transitions = Workflow.get_next_user_step_transitions_for_instance(person, superuser)
        assert start_transitions[0][0] == [transition]
        assert str(start_transitions[0][1].pk) == process_step.pk

    def test_get_next_user_step_transitions_for_instance_condition_not_satisfied(
        self, workflow_factory, transition_factory, process_step_factory, user_step_factory, condition_factory
    ):
        workflow = workflow_factory()
        person = PersonFactory()
        step = user_step_factory(workflow=workflow)
        transition = transition_factory(from_step=step, to_step__workflow=workflow)
        condition_factory(
            transition=transition,
            attribute_name="first_name",
            expected_value=person.first_name,
            operator=Condition.Operator.EQ,
            negate_operator=True,
        )
        superuser = get_or_create_superuser()
        process_step_factory(
            step=step, state=ProcessStep.StepState.ACTIVE, assignee=superuser, process__instance=person
        )
        assert not Workflow.get_next_user_step_transitions_for_instance(person, superuser)

    @patch("wbcore.contrib.workflow.models.workflow.Workflow.generate_workflow_png")
    def test_re_render_workflow_graph_workflow(self, mock_generate, workflow_factory):
        workflow = workflow_factory()
        old_graph = workflow.graph
        new_graph = factory.django.ImageField()._make_data({"width": 1024, "height": 768})
        mock_generate.return_value = new_graph
        re_render_workflow_graph(sender=Workflow, instance=workflow, raw=False)
        assert mock_generate.call_count == 1
        assert workflow.graph != old_graph

    @patch("wbcore.contrib.workflow.models.workflow.Workflow.generate_workflow_png")
    def test_re_render_workflow_graph_step(self, mock_generate, random_child_step_factory):
        step = random_child_step_factory()
        old_graph = step.workflow.graph
        new_graph = factory.django.ImageField()._make_data({"width": 1024, "height": 768})
        mock_generate.return_value = new_graph
        re_render_workflow_graph(sender=step.__class__, instance=step, raw=False)
        # Not really sure why its called twice but as long as we have no infinite loop I'm fine
        assert mock_generate.call_count == 2
        assert step.workflow.graph != old_graph

    @patch("wbcore.contrib.workflow.models.workflow.Workflow.generate_workflow_png")
    def test_re_render_workflow_graph_transition(self, mock_generate, transition_factory):
        transition = transition_factory()
        old_graph = transition.to_step.workflow.graph
        new_graph = factory.django.ImageField()._make_data({"width": 1024, "height": 768})
        mock_generate.return_value = new_graph
        re_render_workflow_graph(sender=Transition, instance=transition, raw=False)
        # Not really sure why its called twice but as long as we have no infinite loop I'm fine
        assert mock_generate.call_count == 2
        assert transition.to_step.workflow.graph != old_graph

    @patch("wbcore.contrib.workflow.models.workflow.Workflow.generate_workflow_png")
    def test_re_render_workflow_graph_condition(self, mock_generate, condition_factory):
        condition = condition_factory()
        old_graph = condition.transition.to_step.workflow.graph
        new_graph = factory.django.ImageField()._make_data({"width": 1024, "height": 768})
        mock_generate.return_value = new_graph
        re_render_workflow_graph(sender=Condition, instance=condition, raw=False)
        # Not really sure why its called twice but as long as we have no infinite loop I'm fine
        assert mock_generate.call_count == 2
        assert condition.transition.to_step.workflow.graph != old_graph

    @patch("wbcore.contrib.workflow.models.workflow.Workflow.generate_workflow_png")
    def test_re_render_workflow_graph_sender_renamed(self, mock_generate, workflow_factory):
        workflow = workflow_factory()
        old_graph = workflow.graph
        new_graph = factory.django.ImageField()._make_data({"width": 1024, "height": 768})
        mock_generate.return_value = new_graph
        re_render_workflow_graph(sender=ProcessStep, instance=workflow, raw=False)
        assert mock_generate.call_count == 0
        assert workflow.graph == old_graph
