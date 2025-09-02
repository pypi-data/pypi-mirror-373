from django.db.models import Model
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from wbcore.contrib.authentication.models import User
from wbcore.serializers import Serializer
from wbcore.test.utils import get_data_from_factory
from wbcore.viewsets import ModelViewSet


def get_create_view(
    client: Client,
    instance: Model,
    superuser: User,
    url: str,
    viewset: ModelViewSet,
) -> HttpResponse:
    """
    Create a new instance through a view using the Django REST Framework client.

    Parameters:
        - client (django.test.Client): The Django test client.
        - instance (django.db.models.Model): The model instance to be created.
        - superuser (django.contrib.auth.models.User): The superuser for authentication.
        - url (str): The URL endpoint for the view.
        - viewset (wbcore.viewsets.ModelViewSet): The viewset for the model.

    Returns:
        django.http.HttpResponse: The HTTP response from the view.
    """
    instance_data = get_data_from_factory(instance, viewset, delete=True, superuser=superuser)
    return client.post(url, instance_data)


def get_detail_view(client: Client, pk: int, url: str) -> HttpResponse:
    """
    Retrieve the details of a model instance through a detail view using the Django REST Framework client.

    Parameters:
        - client (django.test.Client): The Django test client.
        - pk (int): The primary key of the model instance to retrieve.
        - url (str): The base URL endpoint for the detail view.

    Returns:
        django.http.HttpResponse: The HTTP response from the detail view.
    """
    detail_url = reverse(url, args=[pk])
    return client.get(detail_url)


def get_update_view(client: Client, instance: Model, serializer: Serializer, url: str) -> HttpResponse:
    """
    Update a model instance through an update view using the Django REST Framework client.

    Parameters:
        - client (django.test.Client): The Django test client.
        - instance (django.db.models.Model): The model instance to be updated.
        - serializer (Serializer): The serializer used to serialize the instance.
        - url (str): The base URL endpoint for the update view.

    Returns:
        django.http.HttpResponse: The HTTP response from the update view.
    """
    update_url = reverse(url, args=[instance.pk])
    serialized_data = serializer(instance).data
    return client.put(update_url, data=serialized_data, content_type="application/json")


def get_partial_view(client: Client, instance_id: int, data: dict, url: str) -> HttpResponse:
    """
    Facilitates partial updates to a specific instance of a model using the Django REST Framework client.

    Parameters:
        - client (django.test.Client): The Django test client.
        - instance_id (int): The unique identifier (primary key) of the instance to be partially updated.
        - data (dict): A dictionary containing the fields and their respective new values that need to be updated in the instance.
        - url (str): The base URL endpoint for the patch view.
    Returns:
        django.http.HttpResponse: The HTTP response from the patch view.
    """
    update_url = reverse(url, args=[instance_id])
    return client.patch(update_url, data=data, content_type="application/json")


def get_delete_view(client: Client, url: str, pk: int) -> HttpResponse:
    """
    Delete a model instance through a delete view using the Django REST Framework client.

    Parameters:
        - client (django.test.Client): The Django test client.
        - url (str): The base URL endpoint for the delete view.
        - pk (int): The primary key of the model instance to delete.

    Returns:
        django.http.HttpResponse: The HTTP response from the delete view.
    """
    delete_url = reverse(url, args=[pk])
    return client.delete(delete_url)


def find_instances_in_response(instances: list[Model], response: HttpResponse) -> tuple:
    """
    Find instances in the data contained in an HTTP response.

    This method takes a list of instances and an HTTP response object, and it checks if each instance
    is present in the data of the response based on their unique identifier (e.g., 'id').

    Parameters:
        - instances (list): A list of instances (models) to search for in the response data.
        - response (HttpResponse): An HTTP response object containing data to search within.

    Returns:
        tuple: A tuple of Boolean values indicating whether each instance was found in the response.
            Each element in the tuple corresponds to an instance in the same order as in the 'instances' list.
            If an instance is found, the corresponding value is True; otherwise, it is False.
    """
    found_instances = [False] * len(instances)

    for item in response.data["results"]:
        for index, instance in enumerate(instances):
            if item.get("id") == instance.id:
                found_instances[index] = True

    return tuple(found_instances)
