from rest_framework.reverse import reverse

from wbcore.contrib.directory.models import BankingContact
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class EmailContactEntryEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcore:directory:entry-emailcontact-list", args=[self.view.kwargs["entry_id"]], request=self.request
        )


class AddressContactEntryEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcore:directory:entry-addresscontact-list", args=[self.view.kwargs["entry_id"]], request=self.request
        )


class SocialMediaContactEntryEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcore:directory:entry-socialmediacontact-list", args=[self.view.kwargs["entry_id"]], request=self.request
        )


class TelephoneContactEntryEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcore:directory:entry-telephonecontact-list", args=[self.view.kwargs["entry_id"]], request=self.request
        )


class WebsiteContactEntryEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcore:directory:entry-websitecontact-list", args=[self.view.kwargs["entry_id"]], request=self.request
        )


class BankingContactEndpointConfig(EndpointViewConfig):
    def get_delete_endpoint(self, **kwargs):
        if self.instance:
            _object = self.view.get_object()
            if _object.status != BankingContact.Status.DRAFT or _object.primary is True:
                return None
        return super().get_delete_endpoint(**kwargs)


class BankingContactEntryEndpointConfig(BankingContactEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcore:directory:entry-bankingcontact-list", args=[self.view.kwargs["entry_id"]], request=self.request
        )
