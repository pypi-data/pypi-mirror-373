from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from psycopg.types.range import DateRange, TimestamptzRange

from wbcore import filters
from wbcore.contrib.example_app.models import (
    Event,
    EventType,
    Match,
    Sport,
    SportPerson,
)
from wbcore.filters.defaults import current_year_date_range


class EventMatchFilter(filters.FilterSet):
    person = filters.ModelMultipleChoiceFilter(
        label=_("Persons"),
        queryset=SportPerson.objects.all(),
        endpoint=SportPerson.get_representation_endpoint(),
        value_key=SportPerson.get_representation_value_key(),
        label_key=SportPerson.get_representation_label_key(),
    )
    minute__gte = filters.NumberFilter(label=_("Minute"), lookup_expr="gte", field_name="minute")
    minute__lte = filters.NumberFilter(label=_("Minute"), lookup_expr="lte", field_name="minute")
    event_type = filters.ModelMultipleChoiceFilter(
        label=_("Event Types"),
        queryset=SportPerson.objects.all(),
        endpoint=SportPerson.get_representation_endpoint(),
        value_key=SportPerson.get_representation_value_key(),
        label_key=SportPerson.get_representation_label_key(),
    )

    class Meta:
        model = Event
        fields = {}


class EventFilter(EventMatchFilter):
    match = filters.ModelChoiceFilter(
        label=_("Match"),
        queryset=Match.objects.all(),
        endpoint=Match.get_representation_endpoint(),
        value_key=Match.get_representation_value_key(),
        label_key=Match.get_representation_label_key(),
    )


class EventTypeSportFilter(filters.FilterSet):
    points__gte = filters.NumberFilter(label=_("Points"), lookup_expr="gte", field_name="points")
    points__lte = filters.NumberFilter(label=_("Points"), lookup_expr="lte", field_name="points")

    class Meta:
        model = EventType
        fields = {
            "name": ["exact", "icontains"],
            "icon": ["exact", "icontains"],
        }


class EventTypeFilter(EventTypeSportFilter):
    sport = filters.ModelMultipleChoiceFilter(
        label=_("Sports"),
        queryset=Sport.objects.all(),
        endpoint=Sport.get_representation_endpoint(),
        value_key=Sport.get_representation_value_key(),
        label_key=Sport.get_representation_label_key(),
    )


class PlayerStatisticsChartFilter(filters.FilterSet):
    minute__gte = filters.NumberFilter(label=_("Minute"), lookup_expr="gte", field_name="minute")
    minute__lte = filters.NumberFilter(label=_("Minute"), lookup_expr="lte", field_name="minute")
    period = filters.DateRangeFilter(
        label=_("Period"), method="filter_by_period", initial=current_year_date_range, required=True
    )

    def filter_by_period(self, queryset: QuerySet[Event], name, value: DateRange) -> QuerySet[Event]:
        return queryset.filter(match__date_time__contained_by=TimestamptzRange(value.lower, value.upper))

    class Meta:
        model = Event
        fields = {}
