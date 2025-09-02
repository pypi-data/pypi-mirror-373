from rest_framework.reverse import reverse

from wbcore import serializers
from wbcore.contrib.documents.models import DocumentType


class DocumentTypeRepresentationSerializer(serializers.RepresentationSerializer):
    endpoint = "wbcore:documents:documenttyperepresentation-list"
    _detail = serializers.HyperlinkField(reverse_name="wbcore:documents:documenttype-detail")

    class Meta:
        model = DocumentType
        fields = ("id", "_detail", "name", "computed_str")


class DocumentTypeModelSerializer(serializers.ModelSerializer):
    _parent = DocumentTypeRepresentationSerializer(source="parent")
    document_count = serializers.IntegerField(read_only=True)

    @serializers.register_resource()
    def list_of_children(self, instance, request, user):
        base_url = reverse("wbcore:documents:documenttype-list", request=request)
        return {"list_of_children": f"{base_url}?parent={instance.id}"}

    @serializers.register_resource()
    def list_of_documents(self, instance, request, user):
        base_url = reverse("wbcore:documents:document-list", request=request)
        if hasattr(instance, "document_count") and instance.document_count > 0:
            return {"list_of_documents": f"{base_url}?document_type={instance.id}"}
        return {}

    class Meta:
        model = DocumentType
        fields = (
            "id",
            "name",
            "document_count",
            "parent",
            "_parent",
            "_additional_resources",
        )
