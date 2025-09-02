import factory
import pytz

from ..models import UserActivity
from .users import UserFactory


class UserActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserActivity

    IP = factory.Faker("ipv4")
    date = factory.Faker("date_time", tzinfo=pytz.utc)
    user = factory.SubFactory(UserFactory)
    # status
    # jti
    # type
    user_agent_info = factory.Faker("sentences")
    latest_refresh = factory.Faker("date_time", tzinfo=pytz.utc)
