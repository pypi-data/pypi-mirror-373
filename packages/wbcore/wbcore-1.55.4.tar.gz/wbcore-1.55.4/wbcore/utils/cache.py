from functools import lru_cache

from django.db.models import QuerySet


@lru_cache
def mapping(queryset: QuerySet, mapping_field: str = "key", id_field: str = "id", **filter_kwargs) -> dict:
    return dict(queryset.filter(**filter_kwargs).values_list(mapping_field, id_field))
