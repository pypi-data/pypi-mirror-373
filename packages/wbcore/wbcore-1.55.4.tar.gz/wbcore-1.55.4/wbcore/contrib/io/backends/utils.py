from ..models import DataBackend, Provider


def register(
    backend_title: str,
    save_data_in_import_source: bool | None = False,
    passive_only: bool | None = False,
    provider_key: str | None = None,
):
    """
    Decorator to include when a backend need automatic registration
    Args:
        backend_name:

    Returns:

    """
    if not backend_title:
        raise ValueError("At least one name must be passed to register.")

    def _decorator(backend_class):
        provider = None
        if provider_key:
            provider, created = Provider.objects.get_or_create(
                key=provider_key, defaults={"title": provider_key.capitalize()}
            )
        DataBackend.objects.update_or_create(
            backend_class_path=backend_class.__module__,
            backend_class_name=backend_class.__name__,
            defaults={
                "title": f"{backend_title} ({provider.title})" if provider else backend_title,
                "save_data_in_import_source": save_data_in_import_source,
                "passive_only": passive_only,
                "provider": provider,
            },
        )
        return backend_class

    return _decorator
