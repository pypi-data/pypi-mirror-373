from wbcore import serializers as wb_serializers
from wbcore.contrib.workflow.models import Display


class DisplayModelSerializer(wb_serializers.ModelSerializer):
    class Meta:
        model = Display
        fields = (
            "id",
            "name",
            "grid_template_areas",
            "_additional_resources",
        )


class DisplayRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:display-detail")

    class Meta:
        model = Display
        fields = (
            "id",
            "name",
            "_detail",
        )
