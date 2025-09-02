import pytest
from django.contrib.auth.models import Permission


@pytest.mark.django_db
class TestCalendarItemTest:
    def test_to_ics(self, calendar_item_factory):
        calendar_item1 = calendar_item_factory()
        assert calendar_item1.to_ics(calendar_item1.period.upper, calendar_item1.period.lower) is None
        calendar_item2 = calendar_item_factory()
        assert calendar_item2.to_ics(calendar_item1.period.lower, calendar_item1.period.upper)

    def test_get_item_type(self, calendar_item_factory):
        calendar_item = calendar_item_factory()
        assert calendar_item.get_item_type() == "agenda.CalendarItem"

    @pytest.mark.parametrize("calendar_item__is_deletable", [True, False])
    def test_cannot_delete_calendar_item(self, calendar_item, user):
        assert not calendar_item.can_delete(
            user
        )  # as user is not a manger nor among the entities, he cannot delete the event

    @pytest.mark.parametrize("calendar_item__is_deletable", [True, False])
    def test_can_manager_delete_event(self, calendar_item, user):
        permission = Permission.objects.get(
            content_type__app_label="agenda", codename="administrate_confidential_items"
        )
        user.user_permissions.add(permission)
        assert calendar_item.can_delete(user) == calendar_item.is_deletable

    @pytest.mark.parametrize("calendar_item__is_deletable", [True, False])
    def test_can_participants_delete_event(self, calendar_item, user):
        calendar_item.entities.add(user.profile.id)
        assert calendar_item.can_delete(user) == calendar_item.is_deletable
