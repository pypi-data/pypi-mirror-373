from typing import Optional

from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.directory.models import BankingContact, Entry
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

CONTACT_PERSON_LEGEND = [
    dp.Legend(
        key="primary",
        items=[dp.LegendItem(icon=WBColor.GREEN_LIGHT.value, label=gettext_lazy("Primary Contact"), value=True)],
    ),
    dp.Legend(
        key="company_contact",
        items=[dp.LegendItem(icon=WBColor.YELLOW_LIGHT.value, label=gettext_lazy("Company Contact"), value=True)],
    ),
]
CONTACT_PERSON_FORMATTING = [
    dp.Formatting(
        column="primary",
        formatting_rules=[
            dp.FormattingRule(
                style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                condition=("==", True),
            )
        ],
    ),
    dp.Formatting(
        column="company_contact",
        formatting_rules=[
            dp.FormattingRule(
                style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                condition=("==", True),
            )
        ],
    ),
]

CONTACT_COMPANY_LEGEND = [
    dp.Legend(
        key="primary",
        items=[dp.LegendItem(icon=WBColor.GREEN_LIGHT.value, label=gettext_lazy("Primary Contact"), value=True)],
    ),
]
CONTACT_COMPANY_FORMATTING = [
    dp.Formatting(
        column="primary",
        formatting_rules=[
            dp.FormattingRule(
                style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                condition=("==", True),
            )
        ],
    )
]


def get_legend_formatting(self):
    entry = Entry.all_objects.get(id=self.view.kwargs["entry_id"])
    if entry.is_company:
        legend = CONTACT_COMPANY_LEGEND
        format = CONTACT_COMPANY_FORMATTING
        return legend, format
    else:
        legend = CONTACT_PERSON_LEGEND
        format = CONTACT_PERSON_FORMATTING
        return legend, format


class EmailContactDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="address", label=_("Email Address")),
                dp.Field(key="entry", label=_("Entry")),
            ],
            legends=CONTACT_PERSON_LEGEND,
            formatting=CONTACT_PERSON_FORMATTING,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["primary", "location"],
                ["entry", "address"],
            ]
        )


class TelephoneContactDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="telephone_type", label=_("Type")),
                dp.Field(key="number", label=_("Number")),
                dp.Field(key="entry", label=_("Entry")),
            ],
            legends=CONTACT_PERSON_LEGEND,
            formatting=CONTACT_PERSON_FORMATTING,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["primary", "location", "entry"], ["telephone_type", repeat_field(2, "number")]])


class AddressContactDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="street", label=_("Street")),
                dp.Field(key="street_additional", label=_("Street Additional")),
                dp.Field(key="zip", label=_("Zip")),
                dp.Field(key="geography_city", label=_("City")),
            ],
            legends=CONTACT_PERSON_LEGEND,
            formatting=CONTACT_PERSON_FORMATTING,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["primary", "location", "entry"],
                [repeat_field(2, "street"), "street_additional"],
                [repeat_field(2, "geography_city"), "zip"],
            ]
        )


class BankingContactDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="institute", label=_("Institute")),
                dp.Field(key="institute_additional", label=_("Institute additional")),
                dp.Field(key="iban", label=_("IBAN")),
                dp.Field(key="swift_bic", label=_("SWIFT")),
                dp.Field(key="currency", label=_("Currency")),
                dp.Field(key="entry", label=_("Entry")),
                dp.Field(key="edited", label=_("Edited")),
                dp.Field(key="additional_information", label=_("Information")),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=BankingContact.Status.APPROVED.label,
                            value=BankingContact.Status.APPROVED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=BankingContact.Status.PENDING.label,
                            value=BankingContact.Status.PENDING.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=BankingContact.Status.DRAFT.label,
                            value=BankingContact.Status.DRAFT.value,
                        ),
                    ],
                ),
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", BankingContact.Status.APPROVED.value),
                        ),
                    ],
                ),
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", BankingContact.Status.PENDING.value),
                        )
                    ],
                ),
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", BankingContact.Status.DRAFT.value),
                        )
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        if "pk" not in self.view.kwargs:
            fields = []
        else:
            fields = [[repeat_field(2, "status")]]
        fields.extend(
            [
                [repeat_field(2, "location")],
                ["primary", "."],
                ["institute", "institute_additional"],
                ["iban", "swift_bic"],
                ["currency", "entry"],
                [repeat_field(2, "additional_information")],
                [repeat_field(2, "edited")],
            ]
        )
        return create_simple_display(fields)


class EmailContactEntryDisplay(EmailContactDisplay):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        legend, format = get_legend_formatting(self)
        return dp.ListDisplay(
            fields=[
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="address", label=_("Email Address")),
            ],
            legends=legend,
            formatting=format,
            editable=True,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["primary", "location"], [repeat_field(2, "address")]])


class AddressContactEntryDisplay(AddressContactDisplay):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        legend, format = get_legend_formatting(self)
        return dp.ListDisplay(
            fields=[
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="street", label=_("Street")),
                dp.Field(key="street_additional", label=_("Street Additional")),
                dp.Field(key="zip", label=_("Zip")),
                dp.Field(key="geography_city", label=_("City")),
                dp.Field(key="geography_state", label=_("State")),
                dp.Field(key="geography_country", label=_("Country")),
                dp.Field(key="geography_continent", label=_("Continent")),
            ],
            legends=legend,
            formatting=format,
            editable=True,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["primary", "location"],
                ["street", "street_additional"],
                ["zip", "geography_city"],
            ]
        )


class TelephoneContactEntryDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        legend, format = get_legend_formatting(self)
        return dp.ListDisplay(
            fields=[
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="telephone_type", label=_("Type")),
                dp.Field(key="number", label=_("Number")),
            ],
            legends=legend,
            formatting=format,
            editable=True,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["primary", "location"], ["telephone_type", "number"], [repeat_field(2, "activities_section")]],
            [
                create_simple_section(
                    "activities_section", "Activities", [["list_of_activities"]], "list_of_activities", collapsed=True
                )
            ],
        )


class WebsiteContactEntryDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        legend, format = get_legend_formatting(self)
        return dp.ListDisplay(
            fields=[
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="url", label=_("URL")),
            ],
            legends=legend,
            formatting=format,
            editable=True,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["primary", "location"], [repeat_field(2, "url")]])


class BankingContactEntryDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        legend, format = get_legend_formatting(self)
        return dp.ListDisplay(
            fields=[
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="institute", label=_("Institute")),
                dp.Field(key="institute_additional", label=_("Institute additional")),
                dp.Field(key="iban", label=_("IBAN")),
                dp.Field(key="swift_bic", label=_("SWIFT")),
                dp.Field(key="currency", label=_("Currency")),
                dp.Field(key="edited", label=_("Edited")),
                dp.Field(key="additional_information", label=_("Information")),
            ],
            legends=legend,
            formatting=format,
            editable=True,
        )

    def get_instance_display(self) -> Display:
        if "pk" not in self.view.kwargs:
            fields = []
        else:
            fields = [[repeat_field(2, "status")]]
        fields.extend(
            [
                ["primary", "location"],
                ["institute", "institute_additional"],
                ["iban", "swift_bic"],
                [repeat_field(2, "currency")],
                [repeat_field(2, "additional_information")],
            ]
        )

        return create_simple_display(fields)


class SocialMediaContactEntryDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        legend, format = get_legend_formatting(self)
        return dp.ListDisplay(
            fields=[
                dp.Field(key="platform", label=_("Platform")),
                dp.Field(key="location", label=_("Location")),
                dp.Field(key="url", label=_("URL")),
            ],
            legends=legend,
            formatting=format,
            editable=True,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["platform", "primary"], ["url", "location"]])
