from datetime import datetime
from io import BytesIO
from typing import Generator, Optional

from django.db import models


class AbstractDataBackend:
    def __init__(self, import_credential: Optional[models.Model] = None, data_backend=None, **kwargs):
        self.data_backend = data_backend
        self.import_credential = import_credential

    def is_object_valid(self, obj: models.Model) -> bool:
        """
        Can be overriden to define how an object is consired valid by the backend. Default to return True

        Args:
            obj: The tested object

        Returns:
            True if the object is considered valid
        """
        default_qs = self.get_default_queryset()
        if default_qs is not None:
            return isinstance(obj, default_qs.model) and default_qs.filter(pk=obj.pk).exists()
        return False

    def get_default_queryset(self) -> models.QuerySet | None:
        """
        Returns the defaults queryset to loop over by the backend to retreive import files. Used on daily import when no queryset is explicitly provided.

        Returns:
            The default queryset if it exists, none otherwise (Default)
        """
        return None

    def get_provider_id(self, obj: models.Model) -> str | None:
        """
        Override if backend support another and different identifier scheme. We expect this function to the external provider identifier given a certain object.

        Args:
            obj: The object to extract the external identifier

        Returns:
            The external provider identifier it it exists. None otherwise (Default)
        """
        return None

    def get_files(self, execution_time: datetime, **kwargs) -> Generator[tuple[str, BytesIO], None, None] | None:
        """
        Override to implement the import file creation logic

        Args:
            execution_time: The time at which the import takes place
            **kwargs: Possible keywords arguments to be passed down to the importer.

        Returns:
            A generator of bitestream object.
        """
        pass
