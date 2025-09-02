from wbcore import serializers as wb_serializers

from .models import Geography


class GeographyRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = Geography
        fields = ["id", "representation"]


class CountryRepresentationSerializer(GeographyRepresentationSerializer):
    filter_params = {"level": Geography.Level.COUNTRY.value}


class GeographyModelSerializer(wb_serializers.ModelSerializer):
    _parent = GeographyRepresentationSerializer(source="parent")

    class Meta:
        model = Geography
        fields = [
            "id",
            "name",
            "representation",
            "parent",
            "_parent",
            "code_2",
            "code_3",
        ]
