import pytest
from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.test import APIRequestFactory

from wbcore.contrib.authentication.factories import SuperUserFactory
from wbcore.contrib.tags.factories import (
    TagFactory,
    TagGroupFactory,
)
from wbcore.contrib.tags.viewsets import (
    TagGroupModelViewSet,
    TagGroupRepresentationViewSet,
    TagModelViewSet,
    TagRepresentationViewSet,
)


@pytest.mark.viewset_tests
@pytest.mark.with_db
@pytest.mark.django_db
class TestTagViewSets:
    @pytest.fixture()
    def api_rf(self):
        factory = APIRequestFactory()
        return factory

    @pytest.fixture()
    def super_user(self):
        super_user = SuperUserFactory()
        return super_user

    @pytest.mark.parametrize(
        "viewset, factory",
        [
            (TagGroupModelViewSet, TagGroupFactory),
            (TagModelViewSet, TagFactory),
            (TagGroupRepresentationViewSet, TagGroupFactory),
            (TagRepresentationViewSet, TagFactory),
        ],
    )
    def test_get_list(self, viewset, factory, api_rf, super_user):
        # Arrange
        request = api_rf.get("")
        request.user = super_user
        factory.create_batch(3)
        vs = viewset.as_view({"get": "list"})
        # Act
        response = vs(request)
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3
        assert not response.data.get("instance")

    @pytest.mark.parametrize(
        "viewset, factory",
        [
            (TagGroupModelViewSet, TagGroupFactory),
            (TagModelViewSet, TagFactory),
            (TagGroupRepresentationViewSet, TagGroupFactory),
            (TagRepresentationViewSet, TagFactory),
        ],
    )
    def test_get_instance(self, viewset, factory, api_rf, super_user):
        # Arrange
        request = api_rf.get("")
        request.user = super_user
        instance = factory()
        vs = viewset.as_view({"get": "retrieve"})
        # Act
        response = vs(request, pk=instance.pk)
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["instance"]["id"] == instance.id
        assert not response.data.get("results")

    @pytest.mark.parametrize(
        "viewset, factory",
        [
            (TagGroupModelViewSet, TagGroupFactory),
            (TagModelViewSet, TagFactory),
        ],
    )
    def test_delete_instance(self, viewset, factory, api_rf, super_user):
        # Arrange
        request = api_rf.delete("")
        request.user = super_user
        instance = factory()
        vs = viewset.as_view({"delete": "destroy"})
        model = viewset.get_model()
        # Act
        response = vs(request, pk=instance.pk)
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not model.objects.filter(id=instance.id).exists()

    @pytest.mark.parametrize(
        "viewset, factory",
        [
            (TagGroupModelViewSet, TagGroupFactory),
            (TagModelViewSet, TagFactory),
        ],
    )
    def test_update_instance(self, viewset, factory, api_rf, super_user):
        # Arrange
        instance = factory()
        new_data = model_to_dict(factory.build())
        new_title = instance.title + "Foo Bar"
        new_data["id"] = instance.id
        new_data["title"] = new_title
        request = api_rf.put("", data=new_data, format="json")
        request.user = super_user
        vs = viewset.as_view({"put": "update"})
        # Act
        response = vs(request, pk=instance.pk)
        updated_instance = response.data.get("instance")
        print("RESPONSE:----------------->\n", response.data)  # noqa
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert updated_instance["id"] == instance.id
        assert updated_instance["title"] == new_title
        assert updated_instance["title"] != instance.title

    @pytest.mark.parametrize(
        "viewset, factory",
        [
            (TagGroupModelViewSet, TagGroupFactory),
            (TagModelViewSet, TagFactory),
        ],
    )
    def test_patch_instance(self, viewset, factory, api_rf, super_user):
        # Arrange
        instance = factory()
        new_title = instance.title + "Foo Bar"
        request = api_rf.patch("", data={"title": new_title})
        request.user = super_user
        vs = viewset.as_view({"patch": "partial_update"})
        # Act
        response = vs(request, pk=instance.pk)
        updated_instance = response.data.get("instance")
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert updated_instance["title"] == new_title
        assert updated_instance["title"] != instance.title
