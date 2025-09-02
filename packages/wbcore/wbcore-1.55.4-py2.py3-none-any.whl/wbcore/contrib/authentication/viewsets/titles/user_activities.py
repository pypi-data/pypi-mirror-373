from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig

from ...models import User


class UserActivityModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("User Activity")


class UserActivityUserModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        user = User.objects.get(id=self.view.kwargs["user_id"])
        return _("User Activity of {user}").format(user=user.profile.computed_str)


class UserActivityTableTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("User Activity Table")


class UserActivityChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("User Activity Chart")


class UserActivityUserChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        user = User.objects.get(id=self.view.kwargs["user_id"])
        return _("User Activity of {user}").format(user=user.profile.computed_str)
