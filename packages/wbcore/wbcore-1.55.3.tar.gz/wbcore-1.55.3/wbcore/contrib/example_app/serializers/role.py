from wbcore import serializers
from wbcore.contrib.example_app.models import Role


class RoleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class RoleRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:role-detail")

    class Meta:
        model = Role
        fields = ("id", "title", "_detail")
