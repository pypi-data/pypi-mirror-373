from django.utils.translation import gettext_lazy as _

from wbcore import filters

from .models import ReleaseNote


def get_choices(*args):
    choices = [(rl, rl) for rl in ReleaseNote.objects.all().distinct("module").values_list("module", flat=True)]
    return choices


class ReleaseNoteFilterSet(filters.FilterSet):
    module = filters.ChoiceFilter(label=_("Module"), choices=get_choices)

    read_unread = filters.ChoiceFilter(
        label=_("Read / Unread"),
        choices=(("read", "Read"), ("unread", "Unread")),
        method="get_read_unread",
    )

    def get_read_unread(self, queryset, name, value):
        if value == "read":
            return queryset.filter(user_read=True)
        elif value == "unread":
            return queryset.filter(user_read=False)
        return queryset

    class Meta:
        model = ReleaseNote
        fields = {
            "version": ["icontains"],
            "module": ["exact"],
            "release_date": ["exact", "lte", "gte"],
            "summary": ["icontains"],
        }
