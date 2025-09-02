import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIRequestFactory

from wbcore.contrib.workflow.models import Step
from wbcore.contrib.workflow.viewsets import (
    EmailStepModelViewSet,
    StepModelViewSet,
    TransitionModelViewSet,
    WorkflowModelViewSet,
)
from wbcore.test.utils import get_or_create_superuser


@pytest.fixture()
def super_user_get_request():
    request = APIRequestFactory().get("")
    request.user = get_or_create_superuser()


@pytest.mark.django_db
class TestWorkflow:
    @pytest.fixture()
    def workflow_viewset(self):
        return WorkflowModelViewSet()

    def test_filter_attached_model(self, super_user_get_request, workflow_viewset, workflow_factory):
        workflow_factory()
        workflow_factory(model=ContentType.objects.first())
        qs = workflow_viewset.get_queryset()
        assert (
            workflow_viewset.filterset_class(request=super_user_get_request).filter_attached_model(qs, "", None) == qs
        )
        assert (
            workflow_viewset.filterset_class(request=super_user_get_request)
            .filter_attached_model(qs, "", "person")
            .count()
            == 1
        )
        assert (
            not workflow_viewset.filterset_class(request=super_user_get_request)
            .filter_attached_model(qs, "", "company")
            .exists()
        )

    def test_filter_by_data(self, super_user_get_request, workflow_viewset, workflow_factory, data_factory):
        workflow_factory()
        data = data_factory()
        qs = workflow_viewset.get_queryset()
        assert workflow_viewset.filterset_class(request=super_user_get_request).filter_by_data(qs, "", None) == qs
        assert (
            workflow_viewset.filterset_class(request=super_user_get_request).filter_by_data(qs, "", data).count() == 1
        )
        assert (
            workflow_viewset.filterset_class(request=super_user_get_request).filter_by_data(qs, "", data).first()
            == data.workflow
        )


@pytest.mark.django_db
class TestStep:
    def test_filter_by_transition(self, super_user_get_request, transition_factory, random_child_step_factory):
        transition = transition_factory()
        random_child_step_factory()
        mvs = StepModelViewSet(kwargs={})
        qs = mvs.get_queryset()
        assert mvs.get_filterset_class(request=super_user_get_request)().filter_by_transition(qs, "", None) == qs
        assert set(
            mvs.get_filterset_class(request=super_user_get_request)().filter_by_transition(qs, "", transition)
        ) == set(Step.objects.filter(id__in=[transition.from_step.pk, transition.to_step.pk]))

    def test_email_filter_template_name(self, super_user_get_request, email_step_factory):
        step = email_step_factory()
        email_step_factory()
        mvs = EmailStepModelViewSet(kwargs={})
        qs = mvs.get_queryset()
        assert mvs.get_filterset_class(request=super_user_get_request)().filter_template_name(qs, "", None) == qs
        assert (
            mvs.get_filterset_class(request=super_user_get_request)()
            .filter_template_name(qs, "", step.template.name)
            .count()
            == 1
        )
        assert (
            mvs.get_filterset_class(request=super_user_get_request)()
            .filter_template_name(qs, "", step.template.name)
            .first()
            == step
        )


@pytest.mark.django_db
class TestTransition:
    def test_filter_by_condition(self, super_user_get_request, condition_factory, transition_factory):
        transition_factory()
        condition = condition_factory()
        mvs = TransitionModelViewSet(kwargs={})
        qs = mvs.get_queryset()
        assert mvs.filterset_class(request=super_user_get_request).filter_by_condition(qs, "", None) == qs
        assert mvs.filterset_class(request=super_user_get_request).filter_by_condition(qs, "", condition).count() == 1
        assert (
            mvs.filterset_class(request=super_user_get_request).filter_by_condition(qs, "", condition).first()
            == condition.transition
        )
