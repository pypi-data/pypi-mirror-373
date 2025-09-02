from selenium.webdriver.remote.webdriver import WebDriver

from wbcore.contrib.directory.factories import (
    ClientManagerRelationshipFactory,
    CompanyFactory,
    CompanyTypeFactory,
    CustomerStatusFactory,
    EmployerEmployeeRelationshipFactory,
    EntryFactory,
    PersonFactory,
    SpecializationFactory,
)
from wbcore.contrib.directory.models import (
    ClientManagerRelationship,
    Company,
    CustomerStatus,
    Person,
)
from wbcore.contrib.directory.serializers import (
    ClientManagerModelSerializer,
    CompanyModelSerializer,
    PersonModelSerializer,
)
from wbcore.test import (
    click_element_by_path,
    fill_out_form_fields,
    open_create_instance,
)

# from wbcrm.factories import ActivityFactory


def set_up_companies() -> list[Company]:
    """Creates three companies (called Company A to C), for testing purposes.

    In addition to the three companies, two company types and two activities are created in which the companies participate.\n
    Company A and Company C are of company type "Type A", Company B is of the type "Type B".\n
    Company A participates in an Activity that was 15 days ago, Company B and C participate in an Activity that was 60 days ago.
    """
    type_a = CompanyTypeFactory(title="Type A")
    type_b = CompanyTypeFactory(title="Type B")
    com_a = CompanyFactory(name="Company A", type=type_b)
    com_b = CompanyFactory(name="Company B", type=type_a)
    com_c = CompanyFactory(name="Company C", type=type_b)
    return [com_a, com_b, com_c]


def set_up_persons() -> list[Person]:
    """Creates three persons (called Henry Kalb, Konrad Zuse & Ada Lovelace), for testing purposes."""
    status_a = CustomerStatusFactory(title="Status A")
    status_b = CustomerStatusFactory(title="Status B")
    status_c = CustomerStatusFactory(title="Status C")
    company_a = CompanyFactory(customer_status=status_a)
    company_b = CompanyFactory(customer_status=status_b)
    company_c = CompanyFactory(customer_status=status_c)
    spec_a = SpecializationFactory(title="Specialization A")
    spec_b = SpecializationFactory(title="Specialization B")
    spec_c = SpecializationFactory(title="Specialization C")
    person_a = PersonFactory(first_name="Henry", last_name="Kalb", prefix=Person.Prefix.MR)
    person_b = PersonFactory(first_name="Konrad", last_name="Zuse", prefix=Person.Prefix.DR)
    person_c = PersonFactory(first_name="Ada", last_name="Lovelace", prefix=Person.Prefix.MRS)
    person_a.specializations.set([spec_a])
    person_b.specializations.set([spec_b, spec_c])
    person_c.specializations.set([spec_c])
    EmployerEmployeeRelationshipFactory(employer=company_a, employee=person_a, primary=True)
    EmployerEmployeeRelationshipFactory(employer=company_a, employee=person_b, primary=False)
    EmployerEmployeeRelationshipFactory(employer=company_b, employee=person_b, primary=True)
    EmployerEmployeeRelationshipFactory(employer=company_c, employee=person_c, primary=True)
    return [person_a, person_b, person_c]


def create_new_company_instance(
    driver: WebDriver,
    field_list: list[str],
    name="Test Company",
    status_title="Test Status",
    is_create_instance_open=True,
) -> Company:
    """A function that automatically creates a new company for selenium e2e-tests. After creating the instance this function will close the create-widget.

    Args:
        driver (WebDriver): The Selenium webdriver.
        field_list (list[str]): List of fields to be filled in the creation mask. The field names must match the names in the CompanyModelSerializer.
        name (str, optional): The title for the new company instance. Defaults to "Test Company".
        status_title (str, optional): The status for the new company instance. Defaults to "Test Status".
        is_create_instance_open (bool, optional): Should be true if the create-widget is already open. Defaults to True.

    Returns:
        Company: The newly created company.
    """
    if not is_create_instance_open:
        open_create_instance(driver, "CRM", "Create Company")

    if CustomerStatus.objects.filter(title=status_title).exists():
        status = CustomerStatus.objects.get(title=status_title)
    else:
        status = CustomerStatusFactory(title=status_title)
    company: Company = CompanyFactory.build(name=name, customer_status=status)
    serializer = CompanyModelSerializer(company)

    fill_out_form_fields(driver, serializer, field_list, company)
    click_element_by_path(driver, "//button[@label='Save and close']")
    return company


def create_new_person_instance(
    driver: WebDriver,
    field_list: list[str],
    first_name: str,
    last_name: str,
    prefix: str,
    is_create_instance_open=True,
) -> Person:
    """A function that automatically creates a new person for selenium e2e-tests. After creating the instance this function will close the create-widget.

    Args:
        driver (WebDriver): The Selenium webdriver.
        field_list (list[str]): List of fields to be filled in the creation mask. The field names must match the names in the PersonModelSerializer.
        first_name (str): The first name for the newly created person.
        last_name (str):  The last name for the newly created person.
        prefix (str):  The prefix for the newly created person.
        is_create_instance_open (bool, optional): Should be true if the create-widget is already open. Defaults to True.

    Returns:
        Person: The newly created person.
    """
    if not is_create_instance_open:
        open_create_instance(driver, "CRM", "Create Person")

    person: Person = PersonFactory.build(first_name=first_name, last_name=last_name, prefix=prefix)
    serializer = PersonModelSerializer(person)

    fill_out_form_fields(driver, serializer, field_list, person)
    click_element_by_path(driver, "//button[@label='Save and close']")
    return person


def create_new_cmr_instance(
    driver: WebDriver,
    field_list: list[str],
    is_primary=True,
    is_create_instance_open=True,
) -> ClientManagerRelationship:
    """A function that automatically creates a new client-manager-relationship for selenium e2e-tests. After creating the instance this function will close the create-widget.

    Args:
        driver (WebDriver): The Selenium webdriver.
        field_list (list[str]): List of fields to be filled in the creation mask. The field names must match the names in the ClientManagerModelSerializer.
        is_primary (str): True if the relationship shell be a primary relationship. Defaults to True.
        is_create_instance_open (bool, optional): Should be true if the create-widget is already open. Defaults to True.

    Returns:
        ClientManagerRelationship: The newly created CMR.
    """
    if not is_create_instance_open:
        open_create_instance(driver, "CRM", "Create Client Manager Relationship")
    manager = PersonFactory()
    entry = EntryFactory()
    cmr = ClientManagerRelationshipFactory.build(client=entry, relationship_manager=manager, primary=is_primary)
    serializer = ClientManagerModelSerializer(cmr)
    fill_out_form_fields(driver, serializer, field_list, cmr)
    click_element_by_path(driver, "//button[@label='Save and close']")
    return cmr
