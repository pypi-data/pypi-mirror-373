from unittest.mock import patch

import pytest
from pytest import FixtureRequest
from rest_framework import status

from wbcore.contrib.authentication.factories import (
    GroupFactory,
    UserFactory,
)
from wbcore.contrib.workflow.models import (
    Condition,
    Data,
    DecisionStep,
    Process,
    ProcessStep,
    Transition,
    Workflow,
)
from wbcore.contrib.workflow.viewsets import (
    AssignedProcessStepModelViewSet,
    ConditionModelViewSet,
    DataModelViewSet,
    DecisionStepModelViewSet,
    ProcessModelViewSet,
    ProcessStepModelViewSet,
    TransitionModelViewSet,
    WorkflowModelViewSet,
)


@pytest.mark.django_db
class TestViewSets:
    @pytest.mark.parametrize(
        "viewset, entries",
        [
            (AssignedProcessStepModelViewSet, "assigned_process_steps"),
            (ConditionModelViewSet, "conditions"),
            (DataModelViewSet, "data"),
            (DecisionStepModelViewSet, "decision_steps"),
            (ProcessModelViewSet, "processes"),
            (ProcessStepModelViewSet, "process_steps"),
            (TransitionModelViewSet, "transitions"),
            (WorkflowModelViewSet, "workflows"),
        ],
    )
    def test_get(self, request_factory, super_user, viewset, entries, request: FixtureRequest):
        # Arrange
        entries = request.getfixturevalue(entries)
        request = request_factory.get("")
        request.user = super_user
        viewset = viewset.as_view({"get": "list"})
        # Act
        response = viewset(request)
        # Assert
        assert response.data["count"] == 3
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "viewset, model",
        [
            (AssignedProcessStepModelViewSet, "assigned_process_step"),
            (ConditionModelViewSet, "condition"),
            (DataModelViewSet, "singular_data"),
            (DecisionStepModelViewSet, "decision_step"),
            (ProcessModelViewSet, "process"),
            (ProcessStepModelViewSet, "process_step"),
            (TransitionModelViewSet, "transition"),
            (WorkflowModelViewSet, "workflow"),
        ],
    )
    def test_retrieve(self, request_factory, super_user, viewset, model, request: FixtureRequest):
        # Arrange
        entries = request.getfixturevalue(model)
        request = request_factory.get("")
        request.user = super_user
        vs = viewset.as_view({"get": "retrieve"})
        # Act
        response = vs(request, pk=entries.id)
        instance = response.data.get("instance")
        # Assert
        assert instance is not None
        assert instance["id"] == entries.id
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "viewset, build_data, can_create",
        [
            (AssignedProcessStepModelViewSet, "assigned_process_steps_build", False),
            (ConditionModelViewSet, "condition_build", True),
            (DataModelViewSet, "data_build", True),
            (DecisionStepModelViewSet, "decision_step_build", True),
            (ProcessModelViewSet, "process_build", False),
            (ProcessStepModelViewSet, "process_steps_build", False),
            (TransitionModelViewSet, "transition_build", True),
            (WorkflowModelViewSet, "workflow_build", True),
        ],
    )
    def test_create(
        self,
        request_factory,
        super_user,
        viewset,
        build_data,
        can_create,
        request: FixtureRequest,
    ):
        # Arrange
        data = request.getfixturevalue(build_data)
        request = request_factory.post("", data=data, format="json")
        request.user = super_user
        vs = viewset.as_view({"post": "create"})
        # Act
        response = vs(request)
        expected_status_code = status.HTTP_201_CREATED if can_create else status.HTTP_405_METHOD_NOT_ALLOWED
        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "viewset, entries, model",
        [
            (AssignedProcessStepModelViewSet, "assigned_process_steps", ProcessStep),
            (ConditionModelViewSet, "conditions", Condition),
            (DataModelViewSet, "data", Data),
            (DecisionStepModelViewSet, "decision_steps", DecisionStep),
            (ProcessModelViewSet, "processes", Process),
            (ProcessStepModelViewSet, "process_steps", ProcessStep),
            (TransitionModelViewSet, "transitions", Transition),
            (WorkflowModelViewSet, "workflows", Workflow),
        ],
    )
    def test_delete(
        self,
        request_factory,
        super_user,
        viewset,
        entries,
        model,
        request: FixtureRequest,
    ):
        # Arrange
        entries = request.getfixturevalue(entries)
        entry_id = entries[1].id
        request = request_factory.delete("", args=entry_id)
        request.user = super_user
        vs = viewset.as_view({"delete": "destroy"})
        # Act
        response = vs(request, pk=entry_id)
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert model.objects.count() == 2
        assert not model.objects.filter(id=entry_id).exists()

    @pytest.mark.parametrize(
        "viewset, entry, new_entry",
        [
            (
                AssignedProcessStepModelViewSet,
                "assigned_process_step",
                "assigned_process_steps_build",
            ),
            (ConditionModelViewSet, "condition", "condition_build"),
            (DataModelViewSet, "singular_data", "data_build"),
            (DecisionStepModelViewSet, "decision_step", "decision_step_build"),
            (ProcessModelViewSet, "process", "process_build"),
            (ProcessStepModelViewSet, "process_step", "process_steps_build"),
            (TransitionModelViewSet, "transition", "transition_build"),
            (WorkflowModelViewSet, "workflow", "workflow_build"),
        ],
    )
    def test_put(
        self,
        request_factory,
        super_user,
        viewset,
        entry,
        new_entry,
        request: FixtureRequest,
    ):
        # Arrange
        entry = request.getfixturevalue(entry)
        new_data = request.getfixturevalue(new_entry)
        new_data["id"] = entry.id
        request = request_factory.put("", data=new_data, format="json")
        request.user = super_user
        vs = viewset.as_view({"put": "update"})
        # Act
        response = vs(request, pk=entry.id)
        # Assert
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "viewset, entry, field, is_editable",
        [
            (AssignedProcessStepModelViewSet, "assigned_process_step", "status", False),
            (ConditionModelViewSet, "condition", "expected_value", True),
            (DataModelViewSet, "singular_data", "label", True),
            (DecisionStepModelViewSet, "decision_step", "status", True),
            (ProcessModelViewSet, "process", "state", False),
            (ProcessStepModelViewSet, "process_step", "status", False),
            (TransitionModelViewSet, "transition", "name", True),
            (WorkflowModelViewSet, "workflow", "name", True),
        ],
    )
    def test_patch(
        self,
        request_factory,
        super_user,
        viewset,
        entry,
        field,
        is_editable,
        request: FixtureRequest,
    ):
        # Arrange
        entry = request.getfixturevalue(entry)
        old_field_data = getattr(entry, field)
        new_field_data = "Foo Bar"
        request = request_factory.patch("", data={field: new_field_data})
        request.user = super_user
        vs = viewset.as_view({"patch": "partial_update"})
        # Act
        response = vs(request, pk=entry.id)
        field_data = new_field_data if is_editable else old_field_data
        entry.refresh_from_db()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert getattr(entry, field) == field_data

    def test_get_process_step_su(self, request_factory, super_user, permission, process_step_factory):
        # Arrange
        process_step_a = process_step_factory(permission=permission)
        process_step_b = process_step_factory()
        request = request_factory.get("")
        request.user = super_user
        # Act
        vs = ProcessStepModelViewSet(request=request, kwargs={})
        qs = vs.get_queryset()
        id_list = list(map(str, qs.values_list("id", flat=True)))
        # Assert
        assert process_step_a.id in id_list
        assert process_step_b.id in id_list

    def test_get_queryset_user_permission(self, request_factory, user, permission, process_step_factory):
        # Arrange
        user.user_permissions.add(permission)
        process_step_a = process_step_factory(permission=permission)
        process_step_b = process_step_factory()
        request = request_factory.get("")
        request.user = user
        # Act
        vs = ProcessStepModelViewSet(request=request, kwargs={})
        qs = vs.get_queryset()
        id_list = list(map(str, qs.values_list("id", flat=True)))
        # Assert
        assert process_step_a.id in id_list
        assert process_step_b.id in id_list

    def test_get_queryset_user_no_permission(self, request_factory, user, permission, process_step_factory):
        # Arrange
        process_step_a = process_step_factory(permission=permission)
        process_step_b = process_step_factory()
        request = request_factory.get("")
        request.user = user
        # Act
        vs = ProcessStepModelViewSet(request=request, kwargs={})
        qs = vs.get_queryset()
        id_list = list(map(str, qs.values_list("id", flat=True)))
        # Assert
        assert process_step_a.id not in id_list
        assert process_step_b.id in id_list

    def test_get_queryset_group_permission(self, request_factory, permission, process_step_factory):
        # Arrange
        process_step_a = process_step_factory(permission=permission)
        process_step_b = process_step_factory()
        group = GroupFactory(permissions=[permission])
        user = UserFactory(is_superuser=False, groups=[group])
        request = request_factory.get("")
        request.user = user
        # Act
        vs = ProcessStepModelViewSet(request=request, kwargs={})
        qs = vs.get_queryset()
        id_list = list(map(str, qs.values_list("id", flat=True)))
        # Assert
        assert process_step_a.id in id_list
        assert process_step_b.id in id_list

    @patch("wbcore.contrib.workflow.models.step.Step.start_next_step")
    def test_next(self, mock_next, request_factory, super_user, process_step, transition):
        request = request_factory.get("")
        request.user = super_user
        request.GET = request.GET.copy()
        request.GET["transition_id"] = transition.id
        response = ProcessStepModelViewSet().next(request, pk=process_step.pk)
        assert response.status_code == status.HTTP_200_OK
        assert set(str(x.pk) for x in mock_next.call_args.args) == {
            process_step.pk,
            str(transition.pk),
        }
