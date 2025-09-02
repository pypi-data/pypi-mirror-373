from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.test import APIRequestFactory

from wbcore.pagination import LimitOffsetPagination

factory = APIRequestFactory()


class TestEndlessPaginationMixin:
    def setup_method(self):
        class PassThroughSerializer(serializers.Serializer):
            def to_representation(self, instance):
                return instance

        self.view = ListAPIView.as_view(
            serializer_class=PassThroughSerializer,
            queryset=range(1, 101),
            pagination_class=LimitOffsetPagination,
            authentication_classes=[],
            permission_classes=[],
        )

    def test_paginate_queryset_with_pagination(self):
        request = factory.get("/")
        response = self.view(request)
        assert len(response.data["results"]) == 25

    def test_paginate_queryset_without_pagination(self):
        request = factory.get("/", {"disable_pagination": "true"})
        response = self.view(request)
        assert len(response.data) == 100
