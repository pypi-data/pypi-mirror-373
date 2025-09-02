import pytest
from django.apps import apps
from django.db.backends.base.base import BaseDatabaseWrapper
from pytest_mock import MockerFixture
from rest_framework.test import APIRequestFactory, APIClient
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbcore.contrib.workflow.factories import (
    ConditionFactory,
    DataFactory,
    DataValueFactory,
    DecisionStepFactory,
    EmailStepFactory,
    FinishStepFactory,
    JoinStepFactory,
    ProcessFactory,
    ProcessStepFactory,
    RandomChildStepFactory,
    ScriptStepFactory,
    SplitStepFactory,
    StartStepFactory,
    StepFactory,
    TransitionFactory,
    UserStepFactory,
    WorkflowFactory,
)
from wbcore.contrib.authentication.factories import PermissionFactory

from wbcore.contrib.workflow.models import (
    ProcessStep,
    Step,
)

from wbcore.contrib.workflow.serializers import (
    AssignedProcessStepSerializer,
    ConditionModelSerializer,
    DataModelSerializer,
    DecisionStepModelSerializer,
    ProcessModelSerializer,
    ProcessStepModelSerializer,
    TransitionModelSerializer,
    WorkflowModelSerializer,
)

from wbcore.tests.conftest import *

register(WorkflowFactory)
register(EmailStepFactory)
register(TransitionFactory)
register(DataFactory)
register(ProcessStepFactory)
register(UserStepFactory)
register(ConditionFactory)
register(RandomChildStepFactory)
register(FinishStepFactory)
register(ProcessFactory)
register(DecisionStepFactory)
register(SplitStepFactory)
register(JoinStepFactory)
register(ScriptStepFactory)
register(StepFactory)
register(DataValueFactory)
register(StartStepFactory)


# ============================== General Fixtures ==============================


@pytest.fixture
def api_client(super_user):
    client = APIClient()
    client.force_authenticate(user=super_user)
    return client


@pytest.fixture
def request_factory():
    return APIRequestFactory()


@pytest.fixture
def super_user(django_db_setup, django_db_blocker):
    return UserFactory(is_superuser=True)


@pytest.fixture
def user(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        return UserFactory(is_superuser=False)


@pytest.fixture()
def user_step():
    return UserStepFactory(step_type=Step.StepType.USERSTEP)


@pytest.fixture
def permission(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        return PermissionFactory()


# ============================== Condition Fixtures ==============================


@pytest.fixture
def condition(conditions):
    return conditions[0]


@pytest.fixture
def condition_build():
    transition = TransitionFactory()
    instance = ConditionFactory.build(transition=transition)
    return ConditionModelSerializer(instance).data


@pytest.fixture
def conditions():
    return ConditionFactory.create_batch(3)


# ============================== Data Fixtures ==============================


@pytest.fixture
def data():
    return DataFactory.create_batch(3)


@pytest.fixture
def data_build(workflow):
    instance = DataFactory.build(workflow=workflow)
    return DataModelSerializer(instance).data


@pytest.fixture
def singular_data(data):
    return data[0]


# ============================== Decision Step Fixtures ==============================


@pytest.fixture
def decision_step(decision_steps):
    return decision_steps[0]


@pytest.fixture
def decision_step_build(workflow):
    instance = DecisionStepFactory.build(workflow=workflow)
    return DecisionStepModelSerializer(instance).data


@pytest.fixture
def decision_steps():
    return DecisionStepFactory.create_batch(3)


# ============================== Process Fixtures ==============================


@pytest.fixture
def process(processes):
    return processes[0]


@pytest.fixture
def process_build():
    instance = ProcessFactory.build()
    return ProcessModelSerializer(instance).data


@pytest.fixture
def processes():
    return ProcessFactory.create_batch(3)


# ============================== Process Step Fixtures ==============================


@pytest.fixture
def process_step(process_steps):
    return process_steps[0]


@pytest.fixture
def process_steps():
    return ProcessStepFactory.create_batch(3)


@pytest.fixture
def process_steps_build():
    instance = ProcessStepFactory.build()
    return ProcessStepModelSerializer(instance).data


@pytest.fixture
def mocked_process_step(mocker: MockerFixture):
    return mocker.MagicMock(spec=ProcessStep)


# ============================== Assigned Process Step Fixtures ==============================


@pytest.fixture
def assigned_process_step(assigned_process_steps):
    return assigned_process_steps[0]


@pytest.fixture
def assigned_process_steps(super_user, user_step):
    return ProcessStepFactory.create_batch(
        3,
        step=user_step,
        state=ProcessStep.StepState.ACTIVE,
        assignee=super_user,
    )


@pytest.fixture
def assigned_process_steps_build(super_user, user_step):
    instance = ProcessStepFactory.build(
        step=user_step, state=ProcessStep.StepState.ACTIVE, assignee=super_user
    )
    return AssignedProcessStepSerializer(instance).data


# ============================== Transition Fixtures ==============================


@pytest.fixture
def transition(transitions):
    return transitions[0]


@pytest.fixture
def transition_build():
    to_step = FinishStepFactory()
    from_step = StartStepFactory(workflow=to_step.workflow)
    instance = TransitionFactory.build(to_step=to_step, from_step=from_step)
    return TransitionModelSerializer(instance).data


@pytest.fixture
def transitions():
    return TransitionFactory.create_batch(3)


# ============================== Workflow Fixtures ==============================


@pytest.fixture
def workflow(workflows):
    return workflows[0]


@pytest.fixture
def workflow_build():
    instance = WorkflowFactory.build()
    return WorkflowModelSerializer(instance).data


@pytest.fixture
def workflows():
    return WorkflowFactory.create_batch(3)


@pytest.fixture(autouse=True, scope="session")
def django_test_environment(django_test_environment):
    from django.apps import apps

    get_models = apps.get_models

    for m in [m for m in get_models() if not m._meta.managed]:
        m._meta.managed = True


pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("geography"))
