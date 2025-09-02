from django.db.models import Exists, OuterRef, Q
from django.utils.translation import gettext_lazy as _
from django_filters.widgets import CSVWidget

from wbcore import filters as wb_filters
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.geography.models import Geography

from ..models import (
    Company,
    CompanyType,
    CustomerStatus,
    EmployerEmployeeRelationship,
    Entry,
    Person,
    Position,
)


class EntryFilter(wb_filters.FilterSet):
    tier = wb_filters.MultipleChoiceFilter(
        label=_("Tier"),
        help_text=_("Filter by tiering (1-5, with 1 being the best)"),
        choices=Company.Tiering.choices,
        widget=CSVWidget,
    )

    last_event_tmp = wb_filters.DateTimeRangeFilter(
        label=_("Has Event between.."),
        help_text=_("Filter by activities in a date range"),
        method="filter_last_event",
    )
    last_event_period_endswith = wb_filters.DateTimeFilter(
        label=_("Last Event Period End date"), field_name="last_event_period_endswith", lookup_expr="exact"
    )
    last_event_period_endswith__gte = wb_filters.DateTimeFilter(
        label=_("Last Event Period End date"), field_name="last_event_period_endswith", lookup_expr="gte"
    )
    last_event_period_endswith__lte = wb_filters.DateTimeFilter(
        label=_("Last Event Period End date"), field_name="last_event_period_endswith", lookup_expr="lte"
    )

    activity_heat = wb_filters.MultipleLookupFilter(
        field_class=wb_filters.RangeSelectFilter,
        lookup_expr=["gte", "lte"],
        label=_("Activity Heat"),
        help_text=_("Filter by the recent activity level"),
        precision=2,
        field_name="activity_heat",
    )

    # activity_heat__gte = wb_filters.NumberFilter(
    #     label=_("Activity Heat"),
    #     help_text=_("Filter by the recent activity level"),
    #     lookup_expr="gte",
    #     precision=2,
    #     field_name="activity_heat",
    # )
    # activity_heat__lte = wb_filters.NumberFilter(
    #     label=_("Activity Heat"),
    #     help_text=_("Filter by the recent activity level"),
    #     lookup_expr="lte",
    #     precision=2,
    #     field_name="activity_heat",
    # )

    cities = wb_filters.ModelChoiceFilter(
        method="filter_city",
        label=_("City"),
        help_text=_("Filter by related city"),
        queryset=Geography.objects.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
        filter_params={"notnull_related_name": "contact_city"},
    )

    full_addresses = wb_filters.ModelChoiceFilter(
        method="filter_full_address",
        label=_("Full Address"),
        help_text=_("Filter by an address or geography (e.g. Geneva/Switzerland/Europe)"),
        queryset=Geography.objects.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
    )

    def filter_last_event(self, queryset, label, value):
        if value:
            return queryset.annotate(
                has_events=Exists(CalendarItem.objects.filter(entities=OuterRef("pk"), period__overlap=value))
            ).filter(has_events=True)
        return queryset

    def filter_city(self, queryset, name, value):
        if value:
            return queryset.filter(addresses__geography_city=value).distinct()
        return queryset

    def filter_full_address(self, queryset, name, value):
        if value:
            city_level: int = 3
            return queryset.filter(
                **{f'addresses__geography_city{"__parent" * (city_level - value.level)}': value}
            ).distinct()
        return queryset

    class Meta:
        model = Entry
        fields = {}


class PersonFilter(EntryFilter):
    name = wb_filters.CharFilter(label=_("Name"), lookup_expr="icontains")

    position_in_company = wb_filters.ModelMultipleChoiceFilter(
        label=_("Positions"),
        queryset=Position.objects.all(),
        endpoint=Position.get_representation_endpoint(),
        value_key=Position.get_representation_value_key(),
        label_key=Position.get_representation_label_key(),
    )
    customer_status = wb_filters.ModelMultipleChoiceFilter(
        label=_("Customer Statuses"),
        queryset=CustomerStatus.objects.all(),
        endpoint=CustomerStatus.get_representation_endpoint(),
        value_key=CustomerStatus.get_representation_value_key(),
        label_key=CustomerStatus.get_representation_label_key(),
        method="filter_status",
    )
    primary_telephone = wb_filters.CharFilter(label=_("Telephone"), method="filter_primary_telephone")
    email = wb_filters.CharFilter(label=_("Email"), method="filter_email")

    only_internal_users = wb_filters.BooleanFilter(label=_("Only Internal Users"), method="filter_only_internal_users")
    with_active_user_account = wb_filters.BooleanFilter(
        label=_("With Active User Account"), method="filter_with_active_user_account"
    )

    def filter_only_internal_users(self, queryset, name, value):
        if value:
            return queryset.filter_only_internal()
        return queryset

    def filter_with_active_user_account(self, queryset, name, value):
        if value:
            return queryset.filter(user_account__isnull=False, user_account__is_active=True)
        return queryset

    def filter_address(self, queryset, name, value):
        if value:
            city_level: int = 3
            filter_key = f'addresses__geography_city{"__parent" * (city_level - value.level)}'
            return queryset.filter(
                Q(**{filter_key: value})
                | Q(
                    Exists(
                        EmployerEmployeeRelationship.objects.filter(
                            employee=OuterRef("pk"), **{"employer__" + filter_key: value}
                        )
                    )
                )
            ).distinct()
        return queryset

    def filter_status(self, queryset, name, value):
        if value:
            status_title_list = [x.title for x in value]
            return queryset.filter(customer_status__in=status_title_list)
        return queryset

    def filter_email(self, queryset, name, value):
        if value:
            return queryset.filter(emails__address__icontains=value).distinct()
        return queryset

    def filter_primary_telephone(self, queryset, name, value):
        if value:
            return queryset.filter(primary_telephone__icontains=value).distinct()
        return queryset

    def get_union_employee(self, queryset, name, value):
        if (profile := getattr(self.request.user, "profile", None)) and profile.employers.exists():
            return queryset.filter(
                Q(employers__in=[value]) | Q(employers__in=profile.employers.values("id"))
            ).distinct()
        return queryset.filter(employers__in=[value])

    class Meta:
        model = Person
        fields = {
            "employers": ["exact"],
            "relationship_managers": ["exact"],
            "specializations": ["exact"],
        }


class CompanyFilter(EntryFilter):
    type = wb_filters.ModelMultipleChoiceFilter(
        label=_("Type"),
        help_text=_("Filter by the type of company"),
        queryset=CompanyType.objects.all(),
        endpoint=CompanyType.get_representation_endpoint(),
        value_key=CompanyType.get_representation_value_key(),
        label_key=CompanyType.get_representation_label_key(),
    )

    customer_status = wb_filters.ModelMultipleChoiceFilter(
        label=_("Status"),
        help_text=_("Filter by the status of a company"),
        queryset=CustomerStatus.objects.all(),
        endpoint=CustomerStatus.get_representation_endpoint(),
        value_key=CustomerStatus.get_representation_value_key(),
        label_key=CustomerStatus.get_representation_label_key(),
    )

    employees = wb_filters.ModelChoiceFilter(
        label=_("Employees"),
        help_text=_("Filter by some person who is an employee of the company"),
        queryset=lambda request: Person.objects.exclude(
            id__in=Person.objects.filter_only_internal()
        ),  # we need to lazy load queryset so that it is not evaluated at runtime
        endpoint=Person.get_representation_endpoint(),
        value_key=Person.get_representation_value_key(),
        label_key=Person.get_representation_label_key(),
    )
    help_texts = {
        "name": "Filter by the name of the company",
        "relationship_managers": "Filter by a person who is the relationship manager of a company",
    }

    class Meta:
        model = Company
        fields = {
            "name": ["exact", "icontains"],
            "relationship_managers": ["exact"],
            "tier": ["exact", "lt", "lte", "gt", "gte"],
        }


class UserIsManagerFilter(wb_filters.FilterSet):
    computed_str = wb_filters.CharFilter(label=_("Name"), lookup_expr="icontains")
    primary_email = wb_filters.CharFilter(label=_("Email"), method="filter_primary_email")
    primary_telephone = wb_filters.CharFilter(label=_("Telephone"), method="filter_primary_telephone")

    primary_address = wb_filters.ModelChoiceFilter(
        method="filter_address",
        label=_("Address"),
        queryset=Geography.objects.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
    )

    def filter_address(self, queryset, name, value):
        if value:
            return queryset.filter(
                addresses__geography_city__in=value.get_descendants(include_self=True), addresses__primary=True
            )
        return queryset

    def filter_primary_email(self, queryset, name, value):
        if value:
            return queryset.filter(primary_email__icontains=value)
        return queryset

    def filter_primary_telephone(self, queryset, name, value):
        if value:
            return queryset.filter(primary_telephone__icontains=value)
        return queryset

    class Meta:
        model = Entry
        fields = {}
