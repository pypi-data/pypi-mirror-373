from rest_framework.reverse import reverse
from reversion.models import Revision, Version

from wbcore import serializers
from wbcore import serializers as wb_serializers


class RevisionRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="wbcore:revision-detail")

    endpoint = "wbcore:revisionrepresentation-list"
    value_key = "id"
    label_key = "{{date_created}}"

    class Meta:
        model = Revision
        fields = ("id", "date_created", "_detail")


class VersionRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="wbcore:version-detail")
    user_repr = serializers.StringRelatedField(source="revision.user")
    revision_date_created = serializers.StringRelatedField(source="revision.date_created")

    endpoint = "wbcore:versionrepresentation-list"
    value_key = "id"
    label_key = "{{id}} - {{user_repr}} - {{revision_date_created}}"

    class Meta:
        model = Version
        fields = ("id", "user_repr", "revision_date_created", "_detail")


class RevisionModelSerializer(serializers.ModelSerializer):
    user_repr = serializers.StringRelatedField(read_only=True, source="user")
    user = serializers.IntegerField(read_only=True, source="user.id")
    # @wb_serializers.register_resource()
    # def versions(self, instance, request, user):
    #     return {"versions": reverse("wbcore:revision-version-list", args=[instance.id], request=request)}

    class Meta:
        model = Revision
        fields = read_only_fields = (
            "id",
            "date_created",
            "user_repr",
            "user",
            "comment",
            "_additional_resources",
        )


class VersionModelSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(read_only=True, source="revision.date_created")
    _revision = RevisionRepresentationSerializer(source="revision")
    profile_repr = serializers.CharField(read_only=True)

    object_repr = serializers.CharField()

    @wb_serializers.register_resource()
    def resources(self, instance, request, user):
        res = {"compare_with": reverse("wbcore:version-comparewith", args=[instance.id], request=request)}
        if user.has_perm("reversion.change_version") or user.is_superuser:
            res["revert"] = reverse("wbcore:version-revert", args=[instance.id], request=request)
        return res

    class Meta:
        model = Version
        fields = read_only_fields = (
            "id",
            "profile_repr",
            "revision",
            "_revision",
            "content_type",
            "object_id",
            "object_repr",
            "serialized_data",
            "date_created",
            "_additional_resources",
            # "field_dict"
        )
