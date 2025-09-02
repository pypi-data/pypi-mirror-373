import warnings


def deprecate_warning(message: str):
    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(
        message,
        category=DeprecationWarning,
        stacklevel=2,
    )
    warnings.simplefilter("default", DeprecationWarning)
