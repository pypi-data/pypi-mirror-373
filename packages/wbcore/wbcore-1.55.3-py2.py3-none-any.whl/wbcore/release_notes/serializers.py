from wbcore import serializers

from .models import ReleaseNote


class ReleaseNoteModelSerializer(serializers.ModelSerializer):
    user_read = serializers.BooleanField()
    user_read_icon = serializers.IconSelectField()

    class Meta:
        model = ReleaseNote
        fields = ("id", "version", "release_date", "module", "summary", "notes", "user_read", "user_read_icon")
