import pytest
from django.forms.models import model_to_dict
from rest_framework.test import APITestCase
from wbcore.contrib.example_app.factories import StadiumFactory
from wbcore.contrib.example_app.serializers import StadiumModelSerializer


@pytest.mark.django_db
class TestStadiumModelSerializer(APITestCase):
    def test_stadium_serializer(self):
        stadium_data: dict = model_to_dict(StadiumFactory.build())
        stadium_serializer = StadiumModelSerializer(data=stadium_data)

        self.assertTrue(stadium_serializer.is_valid())
