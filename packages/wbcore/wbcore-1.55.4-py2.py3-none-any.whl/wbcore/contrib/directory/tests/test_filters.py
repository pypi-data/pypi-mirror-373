import pytest
from rest_framework.test import APIRequestFactory

from wbcore.contrib.directory.models import EmployerEmployeeRelationship, Person

from ..filters.entries import PersonFilter


@pytest.mark.django_db
class TestSpecificFiltersEntries:
    # def test_filter_address(self, address_contact_factory, company_factory):
    #     address_contact_factory(city="Geneva")
    #     mvs = PersonModelViewSet(kwargs={})
    #     mvs.request = APIRequestFactory().get("")
    #     qs = mvs.get_serializer_class().Meta.model.objects.all()
    #     assert mvs.filterset_class().filter_address(qs, "", "Geneva")
    #     assert mvs.filterset_class().filter_address(qs, "", "Lausanne").count() == 0
    #
    #     mvs = CompanyModelViewSet(kwargs={})
    #     mvs.request = APIRequestFactory().get("")
    #     address_contact_factory(city="Geneva", entry=company_factory())
    #     qs = mvs.get_serializer_class().Meta.model.objects.all()
    #     assert mvs.filter_class().filter_address(qs, "", "Geneva")
    #     assert mvs.filter_class().filter_address(qs, "", "Lausanne").count() == 0

    def test_get_union_employee(self, company_factory, user_factory):
        request = APIRequestFactory().get("")
        user1 = user_factory.create(is_active=True, is_superuser=True)
        user2 = user_factory.create(is_active=True, is_superuser=True)
        company1 = company_factory.create()
        company2 = company_factory.create()
        EmployerEmployeeRelationship.objects.create(employee=user1.profile, employer=company1, primary=True)
        EmployerEmployeeRelationship.objects.create(employee=user2.profile, employer=company2, primary=True)

        request.user = user1
        persons = Person.objects.all()
        assert (
            PersonFilter(request=request)
            .get_union_employee(persons, "", company1)
            .filter(id=user1.profile.id)
            .exists()
        )  #
        assert (
            PersonFilter(request=request)
            .get_union_employee(persons, "", company2)
            .filter(id=user1.profile.id)
            .exists()
        )
        assert (
            not PersonFilter(request=request)
            .get_union_employee(persons, "", company1)
            .filter(id=user2.profile.id)
            .exists()
        )  #
        assert (
            PersonFilter(request=request)
            .get_union_employee(persons, "", company2)
            .filter(id=user2.profile.id)
            .exists()
        )
