from django.db import models


class PermissionMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    @property
    def view_perm_str(cls) -> str:
        """
        Get the view string permission identifer

        Returns:
            The view string permission identifier
        """
        return f"{cls._meta.app_label}.view_{cls._meta.model_name}"

    @classmethod
    @property
    def change_perm_str(cls) -> str:
        """
        Get the change string permission identifer

        Returns:
            The change string permission identifier
        """
        return f"{cls._meta.app_label}.change_{cls._meta.model_name}"

    @classmethod
    @property
    def delete_perm_str(cls) -> str:
        """
        Get the delete string permission identifer

        Returns:
            The delete string permission identifier
        """
        return f"{cls._meta.app_label}.delete_{cls._meta.model_name}"

    @classmethod
    @property
    def select_perm_str(cls) -> str:
        """
        Get the select string permission identifer

        Returns:
            The select string permission identifier
        """
        return f"{cls._meta.app_label}.select_{cls._meta.model_name}"

    @classmethod
    @property
    def admin_perm_str(cls) -> str:
        """
        Get the admin string permission identifer

        Returns:
            The admin string permission identifier
        """
        return f"{cls._meta.app_label}.administrate_{cls._meta.model_name}"

    @classmethod
    @property
    def add_perm_str(cls) -> str:
        """
        Get the add string permission identifer

        Returns:
            The add string permission identifier
        """
        return f"{cls._meta.app_label}.add_{cls._meta.model_name}"
