from django.contrib import admin

from ..models import (
    AddressContact,
    BankingContact,
    EmailContact,
    SocialMediaContact,
    TelephoneContact,
    WebsiteContact,
)


@admin.register(TelephoneContact)
class TelephoneContactModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("entry",)
    search_fields = ("entry__computed_str", "number")


@admin.register(WebsiteContact)
class WebsiteContactModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("entry",)
    search_fields = ("entry__computed_str", "url")


@admin.register(EmailContact)
class EmailContactModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("entry",)
    search_fields = ("entry__computed_str", "address")


@admin.register(AddressContact)
class AddressContactModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("entry",)
    search_fields = (
        "entry__computed_str",
        "street",
        "street_additional",
        "zip",
        "geography_city__name",
        "geography_city__parent__name",
        "geography_city__parent__parent__name",
    )
    raw_id_fields = ["geography_city"]


@admin.register(SocialMediaContact)
class SocialMediaContact(admin.ModelAdmin):
    autocomplete_fields = ("entry",)
    search_fields = ("entry__computed_str", "platform")


@admin.register(BankingContact)
class BankingContactModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("entry",)
    search_fields = ("entry__computed_str", "institute", "institute_additional", "iban", "swift_bic")
