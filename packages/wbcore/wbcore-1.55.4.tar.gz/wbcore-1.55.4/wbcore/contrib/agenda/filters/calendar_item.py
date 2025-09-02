from datetime import timedelta

from django.utils.translation import gettext_lazy as _
from psycopg.types.range import DateRange

from wbcore import filters as wb_filters
from wbcore.contrib.agenda.models import CalendarItem, ConferenceRoom
from wbcore.contrib.directory.models import Entry
from wbcore.utils.date import current_month_date_end, current_month_date_start


class CalendarItemPeriodBaseFilterSet(wb_filters.FilterSet):
    period = wb_filters.DateTimeRangeFilter(label="Period")

    conference_room = wb_filters.ModelMultipleChoiceFilter(
        label=_("Conference Rooms"),
        queryset=ConferenceRoom.objects.all(),
        endpoint=ConferenceRoom.get_representation_endpoint(),
        value_key=ConferenceRoom.get_representation_value_key(),
        label_key=ConferenceRoom.get_representation_label_key(),
    )
    boolean_conference_room = wb_filters.BooleanFilter(
        label=_("Inside Conference Room"), method="boolean_is_in_conference_room"
    )

    def boolean_is_in_conference_room(self, queryset, name, value):
        if value:
            return queryset.filter(conference_room__isnull=False)
        elif value is False:
            return queryset.filter(conference_room__isnull=True)
        return queryset

    class Meta:
        model = CalendarItem
        fields = {}


def get_calendar_period_default(*args, **kwargs):
    month_start = current_month_date_start(*args, **kwargs)
    last_monday_from_month_start = month_start - timedelta(days=month_start.weekday())

    week_after_month = current_month_date_end(*args, **kwargs) + timedelta(weeks=1)
    next_week_sunday_after_month = week_after_month + timedelta(
        days=6 - week_after_month.weekday()
    )  # weekday will return value between 0 and 6 so in order to get the next Sunday we need to subtract from 6
    return DateRange(last_monday_from_month_start, next_week_sunday_after_month)


class CalendarItemFilter(CalendarItemPeriodBaseFilterSet):
    period = wb_filters.DateTimeRangeFilter(label="Period", required=True, initial=get_calendar_period_default)
    item_type = wb_filters.MultipleChoiceFilter(
        label=_("Type"), choices=CalendarItem.get_item_types_choices(), field_name="item_type"
    )
    entities = wb_filters.ModelMultipleChoiceFilter(
        label=_("Calendar Regarding"),
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
        field_name="entities",
        initial=lambda field, request, view: request.user.profile.id,
    )

    class Meta:
        model = CalendarItem
        fields = {}
