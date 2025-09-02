from django.urls import include, path

from wbcore.routers import WBCoreRouter

from . import viewsets

router = WBCoreRouter()
router.register(r"calendaritem", viewsets.InfiniteCalendarItemViewSet, basename="calendaritem")
router.register(
    r"calendaritemrepresentation", viewsets.CalendarItemRepresentationViewSet, basename="calendaritemrepresentation"
)
router.register(r"owncalendar", viewsets.OwnCalendarItemViewSet, basename="owncalendar")
router.register(
    r"conferenceroomrepresentation",
    viewsets.ConferenceRoomRepresentationViewSet,
    basename="conferenceroomrepresentation",
)
router.register(r"conferenceroom", viewsets.ConferenceRoomModelViewSet, basename="conferenceroom")
router.register(r"buildingrepresentation", viewsets.BuildingRepresentationViewSet, basename="buildingrepresentation")
router.register(r"building", viewsets.BuildingModelViewSet, basename="building")


urlpatterns = [
    path("", include(router.urls)),
    path("ics/", viewsets.get_ics, name="get_ics"),
]
