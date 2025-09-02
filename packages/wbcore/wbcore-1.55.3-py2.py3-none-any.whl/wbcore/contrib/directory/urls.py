from django.urls import include, path

from wbcore.routers import WBCoreRouter

from . import viewsets

router = WBCoreRouter()

# Representations
router.register(r"entryrepresentation", viewsets.EntryRepresentationViewSet, basename="entryrepresentation")
router.register(r"personrepresentation", viewsets.PersonRepresentationViewSet, basename="personrepresentation")
router.register(
    r"personinchargerepresentation",
    viewsets.PersonInChargeRepresentationViewSet,
    basename="personinchargerepresentation",
)
router.register(
    r"emailcontactrepresentation", viewsets.EmailContactRepresentationViewSet, basename="emailcontactrepresentation"
)
router.register(
    r"addresscontactrepresentation", viewsets.AddressContactViewSet, basename="addresscontactrepresentation"
)
router.register(
    r"socialmediacontactrepresentation",
    viewsets.SocialMediaContactRepresentationViewSet,
    basename="socialmediacontactrepresentation",
)
router.register(
    r"telephonecontactrepresentation",
    viewsets.TelephoneContactRepresentationViewSet,
    basename="telephonecontactrepresentation",
)
router.register(
    r"bankingcontactrepresentation",
    viewsets.BankingContactRepresentationViewSet,
    basename="bankingcontactrepresentation",
)
router.register(
    r"websitecontactrepresentation",
    viewsets.WebsiteContactRepresentationViewSet,
    basename="websitecontactrepresentation",
)

# Relationships
router.register(r"relationship", viewsets.RelationshipModelViewSet, basename="relationship")
router.register(r"relationship-type", viewsets.RelationshipTypeModelViewSet, basename="relationship-type")
router.register(
    r"relationshiprepresentation", viewsets.RelationshipRepresentationViewSet, basename="relationshiprepresentation"
)
router.register(
    r"relationshiptyperepresentation",
    viewsets.RelationshipTypeRepresentationViewSet,
    basename="relationshiptyperepresentation",
)
router.register(
    r"employeremployeerelationship",
    viewsets.EmployerEmployeeRelationshipModelViewSet,
    basename="employeremployeerelationship",
)
router.register(r"clientmanagerrelationship", viewsets.ClientManagerViewSet, basename="clientmanagerrelationship")
router.register(
    r"clientmanagerrelationshiprepresentation",
    viewsets.ClientManagerRelationshipRepresentationViewSet,
    basename="clientmanagerrelationshiprepresentation",
)
router.register(
    r"clientmanagerrelationship-usermanager",
    viewsets.UserIsManagerViewSet,
    basename="clientmanagerrelationship-usermanager",
)
router.register(
    r"clientmanagerrelationship-userclient",
    viewsets.UserIsClientViewSet,
    basename="clientmanagerrelationship-userclient",
)

# Entry
router.register(r"entry", viewsets.EntryModelViewSet, basename="entry")
router.register(r"person", viewsets.PersonModelViewSet, basename="person")
router.register(r"bank", viewsets.BankModelViewSet, basename="bank")
router.register(r"systememployee", viewsets.SystemEmployeeModelViewSet, basename="systememployee")
router.register(r"company", viewsets.CompanyModelViewSet, basename="company")
router.register(r"companyrepresentation", viewsets.CompanyRepresentationViewSet, basename="companyrepresentation")
# Contacts
router.register(r"addresscontact", viewsets.AddressContactViewSet, basename="addresscontact")
router.register(r"bankingcontact", viewsets.BankingContactViewSet, basename="bankingcontact")
router.register(r"emailcontact", viewsets.EmailContactViewSet, basename="emailcontact")
router.register(r"socialmediacontact", viewsets.SocialMediaContactViewSet, basename="socialmediacontact")
router.register(r"telephonecontact", viewsets.TelephoneContactViewSet, basename="telephonecontact")
router.register(r"websitecontact", viewsets.WebsiteContactViewSet, basename="websitecontact")


# Utils
router.register(r"customerstatus", viewsets.CustomerStatusModelViewSet, basename="customerstatus")
router.register(
    r"customerstatusrepresentation",
    viewsets.CustomerStatusRepresentationViewSet,
    basename="customerstatusrepresentation",
)
router.register(r"position", viewsets.PositionModelViewSet, basename="position")
router.register(r"positionrepresentation", viewsets.PositionRepresentationViewSet, basename="positionrepresentation")
router.register(r"companytype", viewsets.CompanyTypeModelViewSet, basename="companytype")
router.register(
    r"companytyperepresentation", viewsets.CompanyTypeRepresentationViewSet, basename="companytyperepresentation"
)
router.register(r"specialization", viewsets.SpecializationModelViewSet, basename="specialization")
router.register(
    r"specializationrepresentation",
    viewsets.SpecializationRepresentationViewSet,
    basename="specializationrepresentation",
)

employer_router = WBCoreRouter()
employer_router.register(r"employee", viewsets.EmployeeEmployerModelViewSet, basename="employer-employee")

employee_router = WBCoreRouter()
employee_router.register(r"employer", viewsets.EmployerEmployeeModelViewSet, basename="employee-employer")

entry_router = WBCoreRouter()
entry_router.register(r"emailcontact", viewsets.EmailContactEntryViewSet, basename="entry-emailcontact")
entry_router.register(r"addresscontact", viewsets.AddressContactEntryViewSet, basename="entry-addresscontact")
entry_router.register(r"telephonecontact", viewsets.TelephoneContactEntryViewSet, basename="entry-telephonecontact")
entry_router.register(r"websitecontact", viewsets.WebsiteContactEntryViewSet, basename="entry-websitecontact")
entry_router.register(r"bankingcontact", viewsets.BankingContactEntryViewSet, basename="entry-bankingcontact")
entry_router.register(
    r"socialmediacontact", viewsets.SocialMediaContactEntryViewSet, basename="entry-socialmediacontact"
)
entry_router.register(r"relationship", viewsets.RelationshipModelEntryViewSet, basename="entry-relationship")

urlpatterns = [
    path("", include(router.urls)),
    path("company/<int:employer_id>/", include(employer_router.urls)),
    path("person/<int:employee_id>/", include(employee_router.urls)),
    path("entry/<int:entry_id>/", include(entry_router.urls)),
]
