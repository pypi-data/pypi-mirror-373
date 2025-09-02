from configurations import values
from rest_framework.reverse import reverse


class AgendaConfigurationMixin:
    FRONTEND_MENU_CALENDAR = "wbcore.contrib.agenda.configurations.frontend_menu_calendar"
    DEFAULT_CREATE_ENDPOINT_BASENAME = values.Value("wbcore:agenda:calendaritem-list", environ_prefix=None)


def frontend_menu_calendar(request):
    return reverse("wbcore:agenda:owncalendar-list", request=request)
