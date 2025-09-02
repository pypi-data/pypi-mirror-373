from django_celery_beat.models import CrontabSchedule

from wbcore import serializers


class CrontabScheduleRepresentationSerializer(serializers.RepresentationSerializer):
    endpoint = "wbcore:crontabschedulerepresentation-list"
    value_key = "id"

    human_readable = serializers.SerializerMethodField()
    obj_str = serializers.SerializerMethodField()

    def get_obj_str(self, obj):
        return str(obj)

    def get_human_readable(self, obj):
        return obj.human_readable

    def __init__(self, *args, label_key="{{human_readable}} [ {{obj_str}} ]", **kwargs):
        super().__init__(*args, label_key=label_key, **kwargs)

    class Meta:
        model = CrontabSchedule
        fields = ("id", "month_of_year", "day_of_month", "day_of_week", "hour", "minute", "human_readable", "obj_str")
