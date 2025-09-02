from django.db.models import Case, Exists, OuterRef, Q, Value, When
from rest_framework.decorators import action
from rest_framework.response import Response

from wbcore import viewsets

from ..contrib.icons import WBIcon
from .buttons import ReleaseNotesButtonConfig
from .display import ReleaseNoteDisplayConfig
from .filters import ReleaseNoteFilterSet
from .models import ReleaseNote
from .serializers import ReleaseNoteModelSerializer


class ReleaseNoteReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    display_config_class = ReleaseNoteDisplayConfig
    button_config_class = ReleaseNotesButtonConfig

    queryset = ReleaseNote.objects.all()
    serializer_class = ReleaseNoteModelSerializer
    filterset_class = ReleaseNoteFilterSet
    search_fields = ("module", "version", "summary")
    ordering_fields = ("module", "version", "release_date")
    ordering = ("-release_date", "-version")

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                user_read=Exists(ReleaseNote.objects.filter(id=OuterRef("id"), read_by=self.request.user)),
                user_read_icon=Case(
                    When(user_read=True, then=Value(WBIcon.VIEW.icon)), default=Value(WBIcon.IGNORE.icon)
                ),
            )
        )

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.read_by.filter(id=self.request.user.id).exists():
            obj.read_by.add(self.request.user)
        return super().retrieve(request, *args, **kwargs)

    @action(methods=["GET"], detail=False)
    def unread_count(self, request, pk=None):
        return Response({"count": ReleaseNote.objects.filter(~Q(read_by=self.request.user)).count()})

    @action(methods=["PATCH"], detail=False)
    def mark_all_as_read(self, request, pk=None):
        for rl in ReleaseNote.objects.filter(~Q(read_by=self.request.user)):
            rl.read_by.add(self.request.user)
        return Response({})
