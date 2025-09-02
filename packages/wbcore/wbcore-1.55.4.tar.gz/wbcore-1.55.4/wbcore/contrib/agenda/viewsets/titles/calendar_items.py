from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class CalendarItemTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Calendar")
