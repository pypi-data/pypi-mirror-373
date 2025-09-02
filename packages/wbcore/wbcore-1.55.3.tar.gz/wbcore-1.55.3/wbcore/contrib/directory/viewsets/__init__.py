from ..configurations import configuration_registry

CompanyModelViewSet = configuration_registry.company_model_viewset
CompanyRepresentationViewSet = configuration_registry.company_representation_viewset
PersonModelViewSet = configuration_registry.person_model_viewset
PersonRepresentationViewSet = configuration_registry.person_representation_viewset

from .contacts import (
    AddressContactEntryViewSet,
    AddressContactViewSet,
    BankingContactEntryViewSet,
    BankingContactRepresentationViewSet,
    BankingContactViewSet,
    EmailContactEntryViewSet,
    EmailContactRepresentationViewSet,
    EmailContactViewSet,
    SocialMediaContactEntryViewSet,
    SocialMediaContactRepresentationViewSet,
    SocialMediaContactViewSet,
    TelephoneContactEntryViewSet,
    TelephoneContactRepresentationViewSet,
    TelephoneContactViewSet,
    WebsiteContactEntryViewSet,
    WebsiteContactRepresentationViewSet,
    WebsiteContactViewSet,
)
from .entries import (
    BankModelViewSet,
    EntryModelViewSet,
    EntryRepresentationViewSet,
    PersonInChargeRepresentationViewSet,
    UserIsManagerViewSet,
)
from .relationships import (
    ClientManagerRelationshipRepresentationViewSet,
    ClientManagerViewSet,
    EmployeeEmployerModelViewSet,
    EmployerEmployeeModelViewSet,
    EmployerEmployeeRelationshipModelViewSet,
    RelationshipModelEntryViewSet,
    RelationshipModelViewSet,
    RelationshipRepresentationViewSet,
    RelationshipTypeModelViewSet,
    RelationshipTypeRepresentationViewSet,
    SystemEmployeeModelViewSet,
    UserIsClientViewSet,
)
from .utils import (
    CompanyTypeModelViewSet,
    CompanyTypeRepresentationViewSet,
    CustomerStatusModelViewSet,
    CustomerStatusRepresentationViewSet,
    PositionModelViewSet,
    PositionRepresentationViewSet,
    SpecializationModelViewSet,
    SpecializationRepresentationViewSet,
)
