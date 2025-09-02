# Copyright (c) 2023 NEC Corporation. All Rights Reserved.
"""
fireducks.pandas provides pandas-like API on top of fireducks.
"""

import os
import sys

env = os.environ.get("FIREDUCKS_DISABLE")
if env is not None:
    from pandas import *  # noqa
else:
    import logging

    from fireducks import __dfkl_version__

    from fireducks.core import get_fireducks_options
    from fireducks.pandas.api import (
        concat,
        from_pandas,
        get_dummies,
        isna,
        isnull,
        melt,
        merge,
        notna,
        notnull,
        to_datetime,
    )
    from fireducks.pandas.io.api import (
        read_csv,
        read_feather,
        read_json,
        read_parquet,
        to_pickle,
    )
    from fireducks.pandas.config import (
        option_context,
        options,
        set_option,
    )
    from fireducks.pandas.frame import DataFrame
    from fireducks.pandas.series import Series

    # FireDucks original API
    from fireducks.pandas.feat import (  # noqa
        aggregation,
        merge_with_mask,
        multi_target_encoding,
    )

    import fireducks.pandas.utils as _utils
    from fireducks.pandas.utils import (  # noqa
        _get_pandas_module,
    )

    from fireducks.fallback import (
        prohibit_fallback,
        prohibit_or_enforce_fallback,
    )

    from fireducks.pandas.wrappers import (
        Categorical,
        CategoricalIndex,
        DatetimeIndex,
        Index,
        IntervalIndex,
        MultiIndex,
        PeriodIndex,
        RangeIndex,
        TimedeltaIndex,
    )

    if _utils._pd_version_under2:
        # pandas does not have NumericIndex class since v2.0.
        from fireducks.pandas.wrappers import (
            Float64Index,
            Int64Index,
            UInt64Index,
            NumericIndex,
        )

    logger = logging.getLogger(__name__)

    def set_version(is_fireducks):
        global __version__, __git_version__

        if is_fireducks:
            from fireducks import __version__
        else:
            from pandas import __version__

        # python3-pandas package in debian:12 has no `__git_version__`.
        # See GT #4125
        try:
            from pandas import __git_version__ as pandas_git_version

            if is_fireducks:
                from fireducks import __git_version__
            else:
                __git_version__ = pandas_git_version
        except ImportError as e:
            pass

    # 3.7 or later supports module's __getattr__
    if sys.version_info.major > 3 or (
        sys.version_info.major == 3 and sys.version_info.minor >= 7
    ):
        # Borrow unknown attribute from pandas
        def __getattr__(name):
            logger.debug("Borrow %s from pandas", name)
            reason = f"borrow {name} from pandas"
            return _utils.fallback_attr(
                _get_pandas_module, name, reason=reason
            )

    else:
        m = sys.modules[__name__]

        class Wrapper:
            def __getattr__(self, name):
                logger.debug("Borrow %s from pandas", name)
                reason = f"borrow {name} from pandas"
                return _utils.fallback_attr(
                    _get_pandas_module, name, reason=reason
                )

        w = Wrapper()
        names = [
            "from_pandas",
            "read_csv",
            "to_pickle",
            "DataFrame",
            "Series",
            "prohibit_fallback",
            "prohibit_enforce_fallback",
            "__path__",
            "__spec__",
        ]
        for name in names:
            setattr(w, name, getattr(m, name))
        w.__name__ = "fireducks.pandas"
        sys.modules[__name__] = w

    set_version(is_fireducks=get_fireducks_options().fireducks_version)

    __all__ = (
        "__dfkl_version__",
        "from_pandas",
        # pandas api
        "__version__",
        "__git_version__",
        "DataFrame",
        "Series",
        "Categorical",
        "CategoricalIndex",
        "DatetimeIndex",
        "Index",
        "IntervalIndex",
        "MultiIndex",
        "PeriodIndex",
        "RangeIndex",
        "TimedeltaIndex",
        "concat",
        "get_dummies",
        "isna",
        "isnull",
        "melt",
        "merge",
        "notna",
        "notnull",
        "read_csv",
        "read_feather",
        "read_json",
        "read_parquet",
        "to_pickle",
    )

    # pandas does not have NumericIndex class since v2.0.
    if _utils._pd_version_under2:
        __all__ += (
            "Float64Index" "Int64Index",
            "NumericIndex",
            "UInt64Index",
        )

    def load_ipython_extension(ipython):
        from fireducks import imhook

        imhook.load_ipython_extension(ipython)

    def unload_ipython_extension(ipython):
        from fireducks import imhook

        imhook.unload_ipython_extension(ipython)
