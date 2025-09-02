import pytest
from django.forms.models import model_to_dict
from rest_framework.test import APITestCase
from wbcore.contrib.example_app.factories import RoleFactory
from wbcore.contrib.example_app.serializers import RoleModelSerializer


@pytest.mark.django_db
class TestRoleModelSerializer(APITestCase):
    def test_role_serializer(self):
        role_data: dict = model_to_dict(RoleFactory.build())
        role_serializer = RoleModelSerializer(data=role_data)
        self.assertTrue(role_serializer.is_valid())
