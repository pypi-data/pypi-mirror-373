import factory

from ..models import Token


class TokenFactory(factory.django.DjangoModelFactory):
    valid_until = None
    protected_view_name = "wbcore:authentication:user"
    number_usage_left = None
    is_valid = True
    user = factory.SubFactory("wbcore.contrib.authentication.factories.UserFactory")

    class Meta:
        model = Token
        django_get_or_create = ["user", "protected_view_name"]
