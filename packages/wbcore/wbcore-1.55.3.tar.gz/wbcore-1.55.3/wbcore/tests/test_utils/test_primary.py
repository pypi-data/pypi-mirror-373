import pytest
from django.db import models
from faker import Faker

from wbcore.utils.models import PrimaryMixin

fake = Faker()


class TestPrimaryModel(PrimaryMixin):
    PRIMARY_ATTR_FIELDS = ["pivot"]

    pivot = models.CharField(max_length=32, blank=True, null=True)
    field = models.CharField(max_length=32)


@pytest.mark.django_db
class TestPrimaryMixin:
    @pytest.fixture()
    def primary_instance(self):
        return TestPrimaryModel.objects.create(primary=True, pivot="main", field=fake.word())

    def test_get_related_queryset(self):
        instance1 = TestPrimaryModel.objects.create(primary=False, pivot="main", field=fake.word())
        instance2 = TestPrimaryModel.objects.create(primary=False, pivot="main", field=fake.word())
        instance_other = TestPrimaryModel.objects.create(primary=False, pivot="other", field=fake.word())
        assert set(instance1.get_related_queryset()) == {
            instance1,
            instance2,
        }  # Test the queryset are all instance related to pivot "main"
        assert set(instance2.get_related_queryset()) == {
            instance1,
            instance2,
        }  # Test the queryset are all instance related to pivot "main"
        assert set(instance_other.get_related_queryset()) == {
            instance_other
        }  # Test the queryset are all instance related to pivot "other"

    @pytest.mark.parametrize("field", ("Foo Bar"))
    def test_saving_primary(self, field):
        initial_instance = TestPrimaryModel.objects.create(primary=False, pivot="main", field=field)
        assert (
            initial_instance.primary is True
        )  # assert that a non primary saved instance become primary in absence of already primary instance for that pivot
        second_instance = TestPrimaryModel.objects.create(primary=True, pivot="main", field=field)
        assert (
            second_instance.primary is True
        )  # assert that a primary saved instance become primary and the previous primary is unassigned
        initial_instance.refresh_from_db()
        assert initial_instance.primary is False

        unlinked_instance = TestPrimaryModel.objects.create(primary=False, pivot=None, field=field)
        assert unlinked_instance.primary is False  # check that primary logic doesn't apply for unlink instance

    def test_simple_deletion(self, primary_instance):
        assert primary_instance.pivot is not None
        primary_instance.delete()
        primary_instance.refresh_from_db()
        assert primary_instance.pivot is None

    def test_real_deletion(self, primary_instance):
        assert primary_instance.pivot is not None
        primary_instance.delete(no_deletion=False)
        with pytest.raises(TestPrimaryModel.DoesNotExist):
            primary_instance.refresh_from_db()

    def test_deletion_forward_primary_to_next_related_objects(self, primary_instance):
        second_instance = TestPrimaryModel.objects.create(
            primary=False, pivot=primary_instance.pivot, field=fake.word()
        )
        assert second_instance.primary is False  # Basic check
        assert primary_instance.primary is True  # Basic check
        primary_instance.delete()

        second_instance.refresh_from_db()
        primary_instance.refresh_from_db()

        assert primary_instance.pivot is None  # Check if deleted primary is simply unliked
        assert primary_instance.primary is False  # and set to false
        assert second_instance.primary is True  # Check if next non primary related objects become primary
