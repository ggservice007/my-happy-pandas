import warnings

from my_happy_pandas._testing import *  # noqa

warnings.warn(
    (
        "pandas.util.testing is deprecated. Use the functions in the "
        "public API at pandas.testing instead."
    ),
    FutureWarning,
    stacklevel=2,
)
