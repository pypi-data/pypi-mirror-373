from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.example_app.models import Role, SportPerson


class RoleFilter(filters.FilterSet):
    sport_persons = filters.ModelChoiceFilter(
        label=_("Associated Person"),
        queryset=SportPerson.objects.all(),
        endpoint=SportPerson.get_representation_endpoint(),
        value_key=SportPerson.get_representation_value_key(),
        label_key=SportPerson.get_representation_label_key(),
    )

    class Meta:
        model = Role
        fields = {"title": ("exact",)}
