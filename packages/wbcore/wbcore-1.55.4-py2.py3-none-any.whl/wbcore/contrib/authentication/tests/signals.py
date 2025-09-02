from django.dispatch import receiver

from wbcore.test.signals import custom_update_kwargs, get_custom_factory

from ..factories import UserFactory
from ..viewsets import UserActivityTable, UserActivityUserChart


@receiver(get_custom_factory, sender=UserActivityTable)
def receive_factory_user_activity(sender, *args, **kwargs):
    return UserFactory


@receiver(custom_update_kwargs, sender=UserActivityUserChart)
def receive_kwargs_user_activity(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        return {"user_id": obj.user.id}
    return {}
