from typing import Dict, Generator, Iterable, Type


def get_inheriting_subclasses(
    _class, only_leaf: bool = True, only_managed_model_classes: bool = True
) -> Generator[Type, None, None]:
    """
    Utility function to yield all inheriting subclasses. Useful to get all children classes for instance.

    Args:
        _class: The class to yield the subclasses from
        only_leaf: If True, returns only the leaf nodes (Default: True)
        only_managed_model_classes: If True, returns only the class implementing the managed Django model (Default: True)
    Returns:
        Generator of classes
    """
    subclasses = _class.__subclasses__()
    for subclass in subclasses:
        yield from get_inheriting_subclasses(subclass, True, only_managed_model_classes)
    if (not only_leaf or len(_class.__subclasses__()) == 0) and (
        not only_managed_model_classes
        or (
            only_managed_model_classes
            and (_meta := getattr(_class, "_meta", None))
            and _meta.managed
            and hasattr(_class, "objects")
        )
    ):
        yield _class


def uniquify_dict_iterable(iterable: Iterable[Dict], unique_key: str) -> Iterable[Dict]:
    keys = list()
    for item in iterable:
        if key := item.get(unique_key):
            if key not in keys:
                keys.append(key)
                yield item
        else:
            yield item
