import pytest
from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory

from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.agenda.viewsets import CalendarItemViewSet
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.test.utils import get_kwargs, get_or_create_superuser

from ..factories import CalendarItemFactory


@pytest.mark.django_db
class TestCalendarItemViewSet:
    api_factory = APIRequestFactory()

    def test_activity_is_draggable(self, calendar_item_factory, user_factory):
        calendar_item = calendar_item_factory()
        request = self.api_factory.get("")
        request.user = user_factory(is_active=True, is_superuser=True)
        view = CalendarItemViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=calendar_item.id).render()
        assert response.data["instance"]["is_draggable"] is False

    # =================================================================================================================
    #                                            TESTING PRIVATE CALENDAR ITEMS
    # =================================================================================================================

    def test_entity_can_see_private_item(self, calendar_item_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = calendar_item_factory(entities=[user.profile], visibility=CalendarItem.Visibility.PRIVATE)
        request = self.api_factory.get("")
        request.user = user
        view = CalendarItemViewSet.as_view({"get": "list"})
        response = view(request).render()

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == activity.id
        assert response.data["results"][0]["is_private"] is False
        assert response.data["results"][0]["title"] == activity.title

    @pytest.mark.parametrize("mvs", [CalendarItemViewSet])
    def test_random_cannot_see_private_item(self, mvs, calendar_item_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        item = calendar_item_factory(visibility=CalendarItem.Visibility.PRIVATE)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == item.id
        assert response.data["results"][0]["is_private"] is True
        assert response.data["results"][0]["title"] == "Private CalendarItem"

    # =================================================================================================================
    #                                            TESTING CONFIDENTIAL CALENDAR ITEMS
    # =================================================================================================================

    @pytest.mark.parametrize("mvs", [CalendarItemViewSet])
    def test_manager_can_see_confidential_item(self, mvs, calendar_item_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        permission = Permission.objects.get(
            content_type__app_label="agenda", codename="administrate_confidential_items"
        )
        user.user_permissions.add(permission)
        item = calendar_item_factory(visibility=CalendarItem.Visibility.CONFIDENTIAL)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == item.id
        assert response.data["results"][0]["is_confidential"] is False
        assert response.data["results"][0]["title"] == item.title

    @pytest.mark.parametrize("mvs", [CalendarItemViewSet])
    def test_random_cannot_see_confidential_item(self, mvs, calendar_item_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        item = calendar_item_factory(visibility=CalendarItem.Visibility.CONFIDENTIAL)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == item.id
        assert response.data["results"][0]["is_confidential"] is True
        assert response.data["results"][0]["title"] == "Confidential CalendarItem"


@pytest.mark.django_db
class TestSpecificsInfiniteViewsets:
    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (CalendarItemViewSet, CalendarItemFactory),
        ],
    )
    def test_option_request(self, mvs, factory, entry):
        request = APIRequestFactory().options("")
        request.user = get_or_create_superuser()
        obj = factory(entities=(entry,))
        request.GET = request.GET.copy()
        request.GET["date_gte"] = str(obj.period.lower.date())
        kwargs = {}
        mvs.request = request
        vs = mvs.as_view({"options": "options"})
        kwargs = get_kwargs(obj, mvs, request=request)
        response = vs(request, **kwargs).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (CalendarItemViewSet, CalendarItemFactory),
        ],
    )
    def test_viewsets(self, mvs, factory, entry):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        obj = factory(entities=(entry,))
        request.GET = request.GET.copy()
        request.GET["date_gte"] = str(obj.period.lower.date())
        kwargs = {}
        mvs.request = request
        vs = mvs.as_view({"get": "list"})
        response = vs(request, **kwargs).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (CalendarItemViewSet, CalendarItemFactory),
        ],
    )
    def test_viewsets_without_date_gte(self, mvs, factory, entry):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        factory(entities=(entry,))
        request.GET = request.GET.copy()
        request.GET["date_gte"] = None
        kwargs = {}
        mvs.request = request
        vs = mvs.as_view({"get": "list"})
        response = vs(request, **kwargs).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_get_ics(self, calendar_item_factory):
        client = APIClient()
        user = UserFactory(is_active=True, is_superuser=True)
        calendar_item_factory(
            entities=(user.profile,),
        )

        client.force_authenticate(user)
        response = client.get(reverse("wbcore:agenda:get_ics", args=[]))
        assert response.status_code == status.HTTP_200_OK
