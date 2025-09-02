import factory

from wbcore.contrib.workflow.models import Data, DataValue


class DataFactory(factory.django.DjangoModelFactory):
    label = factory.Faker("text", max_nb_chars=64)
    help_text = factory.Faker("text", max_nb_chars=128)
    data_type = factory.Iterator(Data.DataType.values)
    workflow = factory.SubFactory("wbcore.contrib.workflow.factories.WorkflowFactory")
    required = factory.Faker("pybool")

    class Meta:
        model = Data


class DataValueFactory(factory.django.DjangoModelFactory):
    value = factory.Faker("text", max_nb_chars=64)
    data = factory.SubFactory(DataFactory)
    process = factory.SubFactory("wbcore.contrib.workflow.factories.ProcessFactory")

    class Meta:
        model = DataValue
