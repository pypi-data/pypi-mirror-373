from django.http import HttpRequest

from wbcore.contrib.directory.models import Entry


class EntryPermissionMixin:
    queryset = Entry.objects.all()
    request: HttpRequest

    def get_queryset(self):
        # allow the user to see only entries they can see
        return super().get_queryset().filter_for_user(self.request.user)  # type: ignore
