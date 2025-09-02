from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from wbcore.contrib.workflow.models import Process, ProcessStep, Workflow


def check_workflow_for_instance(sender, instance, created, *args, **kwargs):
    # Fail all active process steps with statuses that don't match the instance's status
    active_process_steps = ProcessStep.objects.filter(
        state__in=[ProcessStep.StepState.ACTIVE, ProcessStep.StepState.WAITING],
        process__instance_id=instance.pk,
        process__content_type=ContentType.objects.get_for_model(instance),
        process__state=Process.ProcessState.ACTIVE,
    )
    for process_step in active_process_steps:
        if hasattr(instance, process_step.process.workflow.status_field) and not process_step.status == getattr(
            instance, process_step.process.workflow.status_field
        ):
            process_step.step.get_casted_step().set_failed(process_step, _("Invalid status detected!"))

    # Start workflow if instance's status matches the status of a start step
    start_steps = Workflow.get_start_steps_for_instance(instance)
    for start_step in start_steps:
        start_step.workflow.start_workflow(start_step, instance)
