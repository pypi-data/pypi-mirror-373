# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from collections import abc
import logging

import numpy as np
from pandas.core.dtypes.common import is_scalar
import pandas._libs.missing as libmissing

from firefw import tracing

with tracing.scope(tracing.Level.DEFAULT, "import pandas"):
    import pandas
    from pandas.util._decorators import deprecate_nonkeyword_arguments
    from pandas.core.dtypes.common import (
        is_object_dtype,
    )

from fireducks import ir, irutils
from fireducks.pandas.frame import DataFrame
from fireducks.pandas.series import Series
import fireducks.pandas.utils as utils

logger = logging.getLogger(__name__)

#
# FireDucks API
#


def from_pandas(obj):
    logger.debug("from_pandas: %s", type(obj))

    if isinstance(obj, pandas.DataFrame):
        return DataFrame.from_pandas(obj)
    elif isinstance(obj, pandas.Series):
        return Series.from_pandas(obj)
    raise RuntimeError(
        "fireducks.from_pandas: unknown object is given: " f"{type(obj)}"
    )


#
# Pandas copmat API
#


@deprecate_nonkeyword_arguments(version=None, allowed_args=["objs"])
def concat(*args, **kwargs):
    arg = utils.decode_args(args, kwargs, pandas.concat)
    if isinstance(arg.objs, abc.Mapping):
        if arg.keys is None:
            arg.keys = list(arg.objs.keys())
        arg.objs = [arg.objs[k] for k in arg.keys]
    else:
        # If `objs` is a generator expression, we can get the values from
        # `objs` just once, so overwrite it with the expanded list.
        arg.objs = list(arg.objs)
        args = (arg.objs,) + args[1:]

    if not arg.objs:
        raise ValueError("No objects to concatenate")

    class Concat:
        def __init__(self, objs):
            self.objs = objs

    op = Concat(arg.objs)
    cls = None
    if all([isinstance(obj, DataFrame) for obj in arg.objs]):
        cls = DataFrame
    if all([isinstance(obj, Series) for obj in arg.objs]):
        cls = Series

    if cls is None:
        reason = "objs are not DataFrame or Series"
    else:
        reason = arg.is_not_default(
            [
                "axis",
                "join",
                "keys",
                "levels",
                "names",
                "verify_integrity",
                "sort",
                "copy",
            ]
        )

    if reason:
        return utils.fallback_call(
            utils._get_pandas_module,
            "concat",
            args,
            kwargs,
            reason=reason,
        ).__finalize__(op, method="concat")

    objs = irutils.make_tuple_of_tables(arg.objs)
    return cls._create(
        ir.concat(
            objs, ignore_index=arg.ignore_index, no_align=(cls == Series)
        )
    ).__finalize__(op, method="concat")


def get_dummies(*args, **kwargs):
    decoded = utils.decode_args(args, kwargs, pandas.get_dummies)

    reason = None
    if not isinstance(decoded.data, DataFrame):
        reason = "input is not a DataFrame"

    if is_object_dtype(np.dtype(decoded.dtype)):
        raise ValueError("dtype=object is not a valid dtype for get_dummies")

    if reason is None:
        reason = decoded.is_not_default(
            exclude=[
                "data",
                "columns",
                "prefix",
                "prefix_sep",
                "drop_first",
                "dtype",
            ]
        )

    if reason is None:
        if decoded.columns is not None and not isinstance(
            decoded.columns, list
        ):
            reason = (
                "Unsupported columns of type "
                f"'{type(decoded.columns).__name__}'"
            )
        if decoded.prefix is not None and not isinstance(
            decoded.prefix, (str, list)
        ):
            reason = (
                "Unsupported prefix of type "
                f"'{type(decoded.prefix).__name__}'"
            )
        if not isinstance(decoded.prefix_sep, str):
            reason = (
                "Unsupported prefix_sep of "
                f"type '{type(decoded.prefix_sep).__name__}'"
            )

        default_dtype = np.uint8 if utils._pd_version_under2 else np.bool_
        dtype = default_dtype if decoded.dtype is None else decoded.dtype
        if not utils.is_supported_dtype(dtype):
            reason = f"Unsupported dtype '{decoded.dtype}'"

    if reason is not None:
        return utils.fallback_call(
            utils._get_pandas_module,
            "get_dummies",
            args,
            kwargs,
            reason=reason,
        )

    data = decoded.data
    dtype = utils.to_supported_dtype(dtype)
    columns = irutils.make_vector_or_scalar_of_column_name(decoded.columns)
    prefix = irutils.make_vector_or_scalar_of_column_name(decoded.prefix)
    prefix_sep = decoded.prefix_sep
    drop_first = bool(decoded.drop_first)
    value = ir.get_dummies(
        data._value, columns, prefix, prefix_sep, dtype, drop_first
    )
    return DataFrame._create(value)


def isnull(obj):
    if is_scalar(obj):
        return libmissing.checknull(obj)
    elif isinstance(obj, type):
        return False
    elif isinstance(obj, (DataFrame, Series)):
        return obj.isnull()

    return utils.fallback_call(
        utils._get_pandas_module,
        "isnull",
        args=[obj],
        reason="obj is not DataFrame or Series",
    )


isna = isnull


def melt(frame, *args, **kwargs):
    if isinstance(frame, DataFrame):
        return frame.melt(*args, **kwargs)

    return utils.fallback_call(
        utils._get_pandas_module,
        "melt",
        [frame] + args,
        kwargs,
        reason="obj is not DataFrame",
    )


def merge(left, right, *args, **kwargs):
    return left.merge(right, *args, **kwargs)


def notna(obj):
    if isinstance(obj, (DataFrame, Series)):
        return ~(obj.isnull())

    return utils.fallback_call(
        utils._get_pandas_module,
        "notna",
        args=[obj],
        reason="obj is not DataFrame or Series",
    )


notnull = notna


def to_datetime(*args, **kwargs):
    arg = utils.decode_args(args, kwargs, pandas.to_datetime)
    reason = arg.is_not_default(exclude=["arg", "format", "errors"])

    data = arg.arg
    if not isinstance(data, Series):
        reason = f"to_datetime on non-Series input of type: '{type(data)}'"

    if arg.errors not in {"raise", "coerce"}:
        reason = f"unsupported errors: '{arg.errors}'"

    if arg.format is not None:
        if isinstance(arg.format, str):
            if arg.format.startswith("ISO") or arg.format == "mixed":
                reason = f"unsupported format: '{arg.format}'"
        else:
            reason = f"non-string format: '{arg.format}'"

    if reason is not None:
        return utils.fallback_call(
            utils._get_pandas_module,
            "to_datetime",
            args,
            kwargs,
            reason=reason,
        )
    fmt = irutils.make_scalar(arg.format)
    return Series._create(ir.to_datetime(data._value, fmt, arg.errors))


import sys
import pandas


def _get_pandas_api_module(reason=None):
    return pandas.api


# Borrow unknown module attributes from pandas
def __getattr__(name):
    logger.debug("Borrow %s from pandas.api", name)
    if name in ["__path__", "__spec__"]:
        return object.getattr(sys.modules[__name__], name)
    reason = f"borrow {name} from pandas.api"
    return utils.fallback_attr(_get_pandas_api_module, name, reason=reason)
