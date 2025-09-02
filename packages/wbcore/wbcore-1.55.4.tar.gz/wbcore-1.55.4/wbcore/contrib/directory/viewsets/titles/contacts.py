from django.utils.translation import gettext as _

from wbcore.contrib.directory.models import Entry, SocialMediaContact
from wbcore.metadata.configs.titles import TitleViewConfig


class EmailContactTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Email Contact: {{address}}")

    def get_list_title(self):
        return _("Email Contacts")

    def get_create_title(self):
        return _("New Email Contact")


class AddressContactTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Address Contact")

    def get_list_title(self):
        return _("Address Contacts")

    def get_create_title(self):
        return _("New Address Contact")


class BankingContactTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Banking Contact: {{institute}}")

    def get_list_title(self):
        return _("Banking Contacts")

    def get_create_title(self):
        return _("New Banking Contact")


class EmailContactEntryTitleConfig(TitleViewConfig):
    def get_create_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("New Email Contact for {entry}").format(entry=entry.computed_str)

    def get_list_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("Email Contacts for {entry}").format(entry=entry.computed_str)


class AddressContactEntryTitleConfig(TitleViewConfig):
    def get_create_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("New Address Contact for {entry}").format(entry=entry.computed_str)

    def get_list_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("Address Contacts for {entry}").format(entry=entry.computed_str)


class TelephoneContactTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Telephone Contact: {{number}}")

    def get_list_title(self):
        return _("Telephone Contacts")

    def get_create_title(self):
        return _("New Telephone Contact")


class TelephoneContactEntryTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Telephone Contact: {{number}}")

    def get_list_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("Telephone Contacts for {entry}").format(entry=entry.computed_str)

    def get_create_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("New Telephone Contact for {entry}").format(entry=entry.computed_str)


class WebsiteContactEntryTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Website Contact: {{url}}")

    def get_list_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("Websites for {entry}").format(entry=entry.computed_str)

    def get_create_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("New Website Contact for {entry}").format(entry=entry.computed_str)


class BankingContactEntryTitleConfig(TitleViewConfig):
    def get_list_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("Banking Contacts for {entry}").format(entry=entry.computed_str)

    def get_create_title(self):
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("New Banking Contact for {entry}").format(entry=entry.computed_str)


class SocialMediaContactEntryTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("Social Media Accounts of {entry}").format(entry=entry.computed_str)

    def get_instance_title(self):
        try:
            contact_instance = self.view.get_object()
        except AssertionError:
            return _("Social Media Account")
        return _("{platform} Account of {entry}").format(
            platform=SocialMediaContact.Platforms[contact_instance.platform].value, entry=contact_instance.entry
        )

    def get_create_title(self) -> str:
        entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
        return _("New Social Media Contact for {entry}").format(entry=entry.computed_str)
