import factory

from wbcore.contrib.example_app.models import Role


class RoleFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Role %d" % n)

    class Meta:
        model = Role
