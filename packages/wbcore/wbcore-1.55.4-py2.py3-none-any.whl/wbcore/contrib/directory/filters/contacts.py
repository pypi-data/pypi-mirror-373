import django_filters
from django.utils.translation import gettext_lazy as _

from wbcore import filters as wb_filters
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.geography.models import Geography

from ..models import (
    AddressContact,
    BankingContact,
    ContactLocationChoices,
    ContactTelephoneChoices,
    EmailContact,
    Entry,
    SocialMediaContact,
    TelephoneContact,
    WebsiteContact,
)


class ContactPersonFilter(wb_filters.FilterSet):
    company_contact = wb_filters.BooleanFilter(
        label=_("Company Contact"),
        method="boolean_is_company_contact",
    )

    def boolean_is_company_contact(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.filter(company_contact=value)


class EmailContactCompanyFilter(wb_filters.FilterSet):
    location = wb_filters.MultipleChoiceFilter(
        label=_("Locations"), choices=ContactLocationChoices.choices, widget=django_filters.widgets.CSVWidget
    )

    class Meta:
        model = EmailContact
        fields = {
            "primary": ["exact"],
            "address": ["exact", "icontains"],
        }


class EmailContactPersonFilter(EmailContactCompanyFilter, ContactPersonFilter):
    pass


class AddressContactCompanyFilter(wb_filters.FilterSet):
    geography_city = wb_filters.ModelChoiceFilter(
        label=_("City"),
        queryset=Geography.cities.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
        method="filter_city",
        filter_params={"level": 3},
    )

    geography_country = wb_filters.ModelChoiceFilter(
        label=_("Country"),
        queryset=Geography.countries.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
        method="filter_country",
        filter_params={"level": 1},
    )

    geography_state = wb_filters.ModelChoiceFilter(
        label=_("State"),
        queryset=Geography.states.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
        method="filter_state",
        filter_params={"level": 2},
    )

    geography_continent = wb_filters.ModelChoiceFilter(
        label=_("Continent"),
        queryset=Geography.continents.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
        method="filter_continent",
        filter_params={"level": 0},
    )

    location = wb_filters.MultipleChoiceFilter(
        label=_("Locations"), choices=ContactLocationChoices.choices, widget=django_filters.widgets.CSVWidget
    )

    def filter_city(self, queryset, name, value):
        if value:
            return queryset.filter(geography_city=value)
        return queryset

    def filter_country(self, queryset, name, value):
        if value:
            return queryset.filter(geography_city__parent__parent=value)
        return queryset

    def filter_state(self, queryset, name, value):
        if value:
            return queryset.filter(geography_city__parent=value)
        return queryset

    def filter_continent(self, queryset, name, value):
        if value:
            return queryset.filter(geography_city__parent__parent__parent=value)
        return queryset

    class Meta:
        model = AddressContact
        fields = {
            "street": ["exact", "icontains"],
            "street_additional": ["exact", "icontains"],
            "zip": ["exact", "icontains"],
            "primary": ["exact"],
        }


class AddressContactPersonFilter(AddressContactCompanyFilter, ContactPersonFilter):
    pass


class TelephoneContactCompanyFilter(wb_filters.FilterSet):
    location = wb_filters.MultipleChoiceFilter(
        label=_("Locations"), choices=ContactLocationChoices.choices, widget=django_filters.widgets.CSVWidget
    )
    telephone_type = wb_filters.MultipleChoiceFilter(
        label=_("Types"), choices=ContactTelephoneChoices.choices, widget=django_filters.widgets.CSVWidget
    )

    class Meta:
        model = TelephoneContact
        fields = {
            "number": ["exact", "icontains"],
            "primary": ["exact"],
        }


class TelephoneContactPersonFilter(TelephoneContactCompanyFilter, ContactPersonFilter):
    pass


class WebsiteContactCompanyFilter(wb_filters.FilterSet):
    location = wb_filters.MultipleChoiceFilter(
        label=_("Locations"), choices=ContactLocationChoices.choices, widget=django_filters.widgets.CSVWidget
    )

    class Meta:
        model = WebsiteContact
        fields = {
            "url": ["exact", "icontains"],
            "primary": ["exact"],
        }


class WebsiteContactPersonFilter(WebsiteContactCompanyFilter, ContactPersonFilter):
    pass


class BankingContactCompanyFilter(wb_filters.FilterSet):
    currency = wb_filters.ModelMultipleChoiceFilter(
        label=_("Currencies"),
        queryset=Currency.objects.all(),
        endpoint=Currency.get_representation_endpoint(),
        value_key=Currency.get_representation_value_key(),
        label_key=Currency.get_representation_label_key(),
    )
    location = wb_filters.MultipleChoiceFilter(
        label=_("Locations"), choices=ContactLocationChoices.choices, widget=django_filters.widgets.CSVWidget
    )
    edited__lte = wb_filters.DateTimeFilter(
        label=_("Edited"),
        lookup_expr="lte",
        field_name="edited",
    )

    edited__gte = wb_filters.DateTimeFilter(
        label=_("Edited"),
        lookup_expr="gte",
        field_name="edited",
    )

    class Meta:
        model = BankingContact
        fields = {
            "status": ["exact"],
            "institute": ["exact", "icontains"],
            "institute_additional": ["exact", "icontains"],
            "iban": ["exact", "icontains"],
            "swift_bic": ["exact", "icontains"],
            "primary": ["exact"],
            "additional_information": ["exact", "icontains"],
        }


class BankingContactPersonFilter(BankingContactCompanyFilter, ContactPersonFilter):
    pass


class BankingContactFilter(BankingContactCompanyFilter):
    entry = wb_filters.ModelMultipleChoiceFilter(
        label=_("Entries"),
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
    )


class SocialMediaContactCompanyFilter(wb_filters.FilterSet):
    location = wb_filters.MultipleChoiceFilter(
        label=_("Locations"),
        choices=ContactLocationChoices.choices,
        widget=django_filters.widgets.CSVWidget,
    )
    platform = wb_filters.MultipleChoiceFilter(
        label=_("Social Media Platform"),
        choices=SocialMediaContact.Platforms.choices,
        widget=django_filters.widgets.CSVWidget,
    )

    class Meta:
        model = SocialMediaContact
        fields = {"url": ["exact", "icontains"], "primary": ["exact"]}


class SocialMediaContactPersonFilter(SocialMediaContactCompanyFilter, ContactPersonFilter):
    pass
