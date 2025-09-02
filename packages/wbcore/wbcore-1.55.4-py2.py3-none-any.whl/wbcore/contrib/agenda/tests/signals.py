from django.dispatch import receiver

from wbcore.test.signals import get_custom_factory

from ..factories import CalendarItemFactory
from ..viewsets import (
    CalendarItemViewSet,
    InfiniteCalendarItemViewSet,
    OwnCalendarItemViewSet,
)


@receiver(get_custom_factory, sender=CalendarItemViewSet)
@receiver(get_custom_factory, sender=InfiniteCalendarItemViewSet)
@receiver(get_custom_factory, sender=OwnCalendarItemViewSet)
def receive_factory_employee(sender, *args, **kwargs):
    return CalendarItemFactory
