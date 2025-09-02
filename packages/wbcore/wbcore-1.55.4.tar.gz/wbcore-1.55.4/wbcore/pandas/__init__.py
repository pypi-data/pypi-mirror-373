import warnings

warnings.warn(
    "The 'wbcore.pandas' module is deprecated and will be removed in a future version. "
    "Please use 'wbcore.contrib.pandas' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from wbcore.contrib.pandas import fields
from wbcore.contrib.pandas.fields import (  # noqa
    PKField,
    CharField,
    DateField,
    DateRangeField,
    BooleanField,
    TextField,
    EmojiRatingField,
    FloatField,
    IntegerField,
    YearField,
    ListField,
    JsonField,
    SparklineField,
    PandasFields,
)
from wbcore.contrib.pandas.filters import (  # noqa
    PandasDjangoFilterBackend,
    PandasSearchFilter,
    PandasOrderingFilter,
)
from wbcore.contrib.pandas.filterset import PandasFilterSetMixin  # noqa
from wbcore.contrib.pandas.metadata import PandasMetadata  # noqa
from wbcore.contrib.pandas.utils import (  # noqa
    rule,
    overwrite,
    overwrite_rule,
    overwrite_row,
    overwrite_row_df,
    override_number_to_percent,
    override_number_with_currency,
    override_number_to_x,
    override_number_precision,
    override_number_to_decimal,
    override_number_to_integer_without_decorations,
    pct_change_with_negative_values,
    get_empty_series,
    sanitize_field,
    sanitize_fields,
)
from wbcore.contrib.pandas import views
from wbcore.contrib.pandas.views import PandasMixin, PandasAPIView, PandasAPIViewSet  # noqa
