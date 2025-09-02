from datetime import timedelta

import pytest
from faker import Faker

from wbcore.contrib.authentication.tasks import delete_unregistered_user_account

from ..models import User

fake = Faker()


@pytest.mark.django_db
def test_delete_unregistered_user_account(user_factory):
    val_datetime = fake.date_time()

    registered_user = user_factory.create(is_register=True, is_active=True)
    unregistered_but_active_user = user_factory.create(
        is_register=False, is_active=True
    )  # in case we have (but we shouldn't) unregistered but active user, we don't clean them
    unregistered_user_in_retention_period = user_factory.create(
        is_register=False, is_active=False, date_joined=val_datetime
    )  # unregistered user created within the retention period
    unregistered_user_obselete = user_factory.create(
        is_register=False, is_active=False, date_joined=val_datetime - timedelta(seconds=1)
    )  # unregistered user created outside of the retention period
    delete_unregistered_user_account(prune_user_account_before_datetime=val_datetime)
    assert set(User.objects.exclude(email="AnonymousUser")) == {
        registered_user,
        unregistered_but_active_user,
        unregistered_user_in_retention_period,
    }
    with pytest.raises(User.DoesNotExist):
        unregistered_user_obselete.refresh_from_db()
