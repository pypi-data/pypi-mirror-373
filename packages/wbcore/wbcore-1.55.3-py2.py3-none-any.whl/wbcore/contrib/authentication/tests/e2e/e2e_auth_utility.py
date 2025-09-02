from wbcore.contrib.authentication.factories import (
    AuthenticatedPersonFactory,
    SuperUserFactory,
)
from wbcore.contrib.authentication.models import User


def create_main_company_user(user_password: str) -> User:
    """Creates a user for the main company.

    Args:
        user_password (str): The password used for the user

    Returns:
        User: The newly created user.
    """
    user = SuperUserFactory(plaintext_password=user_password)
    profile = AuthenticatedPersonFactory(user_account=user)
    user.profile = profile
    return user
