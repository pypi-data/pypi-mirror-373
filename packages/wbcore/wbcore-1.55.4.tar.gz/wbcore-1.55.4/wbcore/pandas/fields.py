import warnings

warnings.warn(
    "The 'wbcore.pandas' module is deprecated and will be removed in a future version. "
    "Please use 'wbcore.contrib.pandas' instead.",
    DeprecationWarning,
    stacklevel=2,
)
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
