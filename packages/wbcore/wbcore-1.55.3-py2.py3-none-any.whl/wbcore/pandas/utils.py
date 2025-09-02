import warnings

warnings.warn(
    "The 'wbcore.pandas' module is deprecated and will be removed in a future version. "
    "Please use 'wbcore.contrib.pandas' instead.",
    DeprecationWarning,
    stacklevel=2,
)
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
