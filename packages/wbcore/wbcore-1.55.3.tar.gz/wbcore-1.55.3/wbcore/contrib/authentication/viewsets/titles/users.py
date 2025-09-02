from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig

from ...models import User


class UserPermissionsModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        user = User.objects.get(id=self.view.kwargs["user_id"])
        return _("Permissions for {email}").format(email=user.email)


class UserProfileModelTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Your Profile")


class UserModelTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("User: {{email}}")

    def get_list_title(self):
        return _("Users")

    def get_create_title(self):
        return _("New User")
