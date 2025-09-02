from django_celery_beat.models import CrontabSchedule

from wbcore import viewsets

from .serializers import CrontabScheduleRepresentationSerializer


class CrontabScheduleRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = CrontabSchedule.objects.all()
    serializer_class = CrontabScheduleRepresentationSerializer
