import pytest
from django.forms.models import model_to_dict
from rest_framework.test import APITestCase
from wbcore.contrib.example_app.factories import SportFactory
from wbcore.contrib.example_app.serializers import SportModelSerializer


@pytest.mark.django_db
class TestSportModelSerializer(APITestCase):
    def test_sport_serializer(self):
        sport_data: dict = model_to_dict(SportFactory.build())
        sport_serializer = SportModelSerializer(data=sport_data)

        self.assertTrue(sport_serializer.is_valid())
