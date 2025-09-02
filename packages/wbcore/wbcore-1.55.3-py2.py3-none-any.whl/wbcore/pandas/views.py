import warnings

warnings.warn(
    "The 'wbcore.pandas' module is deprecated and will be removed in a future version. "
    "Please use 'wbcore.contrib.pandas' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from wbcore.contrib.pandas.views import PandasMixin, PandasAPIView, PandasAPIViewSet  # noqa
