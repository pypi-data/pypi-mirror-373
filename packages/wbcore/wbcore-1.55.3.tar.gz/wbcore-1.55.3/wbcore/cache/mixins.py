from functools import cached_property
from typing import Any

import pandas as pd
from django.core.cache import cache

from wbcore.utils.strings import camel_to_snake_case


class CacheMixin:
    extra_cache_kwargs: dict[str, Any]
    CACHE_EMPTY_VALUE = pd.DataFrame()
    CACHE_MAIN_KEY: str = "df"
    CACHE_METHOD: str = "_get_dataframe"

    @cached_property
    def cache_enabled(self) -> bool:
        return getattr(self, "CACHE_ENABLED", False)

    def _get_cache_timeout(self) -> int | None:
        cache_timeout = getattr(self, "CACHE_TIMEOUT", None)
        if callable(cache_timeout):
            return cache_timeout()
        return cache_timeout

    def _get_cache_key(self) -> str:
        cache_key = camel_to_snake_case(self.__class__.__name__)
        if cache_key_prefix := getattr(self, "CACHE_KEY_PREFIX", None):
            if callable(cache_key_prefix):
                cache_key_prefix = cache_key_prefix()
            cache_key += "-" + cache_key_prefix
        return cache_key

    def deserialize_cache_results(self, cached_res: dict[str, Any]) -> Any:
        res = cached_res.pop(self.CACHE_MAIN_KEY, self.CACHE_EMPTY_VALUE)
        # we loop over the other cached kwargs and set them as class attributes
        for k, v in cached_res.items():
            setattr(self, k, v)
        return res

    def serialize_cache_results(self, res: Any) -> dict[str, Any]:
        cached_res = {self.CACHE_MAIN_KEY: res}
        cached_res.update(self.extra_cache_kwargs)
        return cached_res

    def _get_cached_res(self) -> Any:
        if cached_res := cache.get(self._get_cache_key()):
            return self.deserialize_cache_results(cached_res)
        return self.CACHE_EMPTY_VALUE
