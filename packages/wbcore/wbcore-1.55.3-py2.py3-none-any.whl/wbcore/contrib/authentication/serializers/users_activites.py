from wbcore import serializers as wb_serializers

from ..models import User, UserActivity
from .users import UserRepresentationSerializer


class UserActivitySerializer(wb_serializers.ModelSerializer):
    IP = wb_serializers.CharField(read_only=True)
    _user = UserRepresentationSerializer(source="user")
    user = wb_serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=False)
    time_online_minute = wb_serializers.CharField(read_only=True)

    class Meta:
        model = UserActivity
        fields = (
            "id",
            "IP",
            "date",
            "user",
            "_user",
            "status",
            "type",
            "user_agent_info",
            "latest_refresh",
            "time_online_minute",
        )


class UserActivityTableSerializer(UserActivitySerializer):
    today_activity = wb_serializers.CharField(read_only=True)
    beforeyesterday_activity = wb_serializers.CharField(read_only=True)
    yesterday_activity = wb_serializers.CharField(read_only=True)
    user_repr = wb_serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "user_repr", "today_activity", "yesterday_activity", "beforeyesterday_activity")
