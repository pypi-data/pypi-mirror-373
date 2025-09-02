from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse

from wbcore import serializers
from wbcore.contrib.documents.models import Document, ShareableLink, ShareableLinkAccess
from wbcore.contrib.documents.serializers import DocumentRepresentationSerializer
from wbcore.utils.strings import snake_case_to_human


class ShareableLinkModelSerializer(serializers.ModelSerializer):
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(), label="Document", default=serializers.DefaultFromGET("document")
    )
    _document = DocumentRepresentationSerializer(source="document")
    valid = serializers.BooleanField(label=_("Valid"), default=True, read_only=True)

    @serializers.register_resource()
    def hits(self, instance, request, user):
        base_url = reverse("wbcore:documents:linkaccess-list", request=request)
        return {"hits": f"{base_url}?shareable_link={instance.id}"}

    @serializers.register_resource()
    def manually_invalidate(self, instance, request, user):
        if "view" in request.parser_context and hasattr(instance, "is_valid") and instance.is_valid():
            return {
                "manually_invalidate": reverse(
                    "wbcore:documents:link-invalidate",
                    args=[instance.id],
                    request=request,
                )
            }
        return {}

    class Meta:
        model = ShareableLink
        fields = (
            "id",
            "link",
            "document",
            "_document",
            "valid_until",
            "one_time_link",
            "manual_invalid",
            "uuid",
            "_additional_resources",
            "valid",
        )


class ShareableLinkRepresentationSerializer(serializers.RepresentationSerializer):
    endpoint = "wbcore:documents:linkrepresentation-list"
    _detail = serializers.HyperlinkField(reverse_name="wbcore:documents:link-detail")
    _detail_preview = serializers.HyperlinkField(reverse_name="wbcore:documents:link-detail")

    class Meta:
        model = ShareableLink
        fields = ("id", "uuid", "_detail", "_detail_preview")


class ShareableLinkAccessModelSerializer(serializers.ModelSerializer):
    _shareable_link = ShareableLinkRepresentationSerializer(source="shareable_link")

    metadata_repr = serializers.SerializerMethodField(read_only=True)

    def get_metadata_repr(self, obj):
        return f"""
        <ul>
        {"".join([f"<li>{snake_case_to_human(key)}: {value}</li>" for key, value in obj.metadata.items()])}
        </ul>
        """

    class Meta:
        model = ShareableLinkAccess
        fields = (
            "id",
            "shareable_link",
            "_shareable_link",
            "metadata",
            "metadata_repr",
            "accessed",
        )


class ShareableLinkAccessRepresentationSerializer(serializers.RepresentationSerializer):
    endpoint = "wbcore:documents:linkaccessrepresentation-list"
    _detail = serializers.HyperlinkField(reverse_name="wbcore:documents:linkaccess-detail")
    _detail_preview = serializers.HyperlinkField(reverse_name="wbcore:documents:linkaccess-detail")

    class Meta:
        model = ShareableLinkAccess
        fields = ("id", "metadata", "_detail", "_detail_preview")
