# Copyright (c) 2023 NEC Corporation. All Rights Reserved.
from __future__ import annotations
from typing import Callable

import numpy as np
import pandas
from pandas.compat.numpy import function as nv
from pandas.core.dtypes.common import is_dict_like, is_list_like

from fireducks import ir, irutils
from fireducks.fireducks_ext import AggregateOptions
from fireducks.pandas import DataFrame, Series
from fireducks.pandas import utils
from fireducks.pandas.generic import _Scalar

from fireducks.irutils import (
    _is_str_list,
    make_tuple_of_column_names,
    make_tuple_of_vector_or_scalar_of_str,
)


class FallbackMonad:
    """Fallback helper"""

    def __init__(self, obj, attr, args, kwargs):
        self._obj = obj
        self._attr = attr
        self._args = args
        self._kwargs = kwargs
        self.reason = None

    def is_fallback(self):
        return self.reason is not None

    def fallback(self, reason=None):
        r = reason or self.reason
        assert r is not None
        return self._obj._fallback_call(
            self._attr, args=self._args, kwargs=self._kwargs, reason=r
        )


def infer_agg_method_name(func):
    # returns name of the method as string when the given method
    # 'f' is from numpy or pandas Series module, otherwise returns the
    # input method as it is...
    def helper(f):
        is_known_module_method = callable(f) and getattr(
            f, "__module__", None
        ) in [
            "numpy",
            "pandas.core.generic",
            "pandas.core.series",
        ]
        return getattr(f, "__name__", f) if is_known_module_method else f

    if callable(func):
        func = helper(func)
    elif isinstance(func, list):
        func = [helper(f) for f in func]
    elif isinstance(func, dict):
        func = {k: helper(v) for k, v in func.items()}
    return func


def convert_known_module_method_to_str(func: Callable):
    assert callable(func)
    # Ex: Convert numpy.sum, pandas.Series.sum to "sum"
    known_modules = ("numpy", "pandas.core.generic", "pandas.core.series")
    if getattr(func, "__module__", None) in known_modules and hasattr(
        func, "__name__"
    ):
        return getattr(func, "__name__")

    return None


def _check_func_others(func: any):
    if callable(func):
        func_str = convert_known_module_method_to_str(func)
        if func_str is None:
            return f"{func.__name__} is not a known module method", None
    elif isinstance(func, str):
        func_str = func
    else:
        return f"unknown type of aggregation function: {func}", None

    # TODO: raise error when func is invalid
    if func_str not in _check_agg_funcs:
        return f"`{func}` is not a supported aggregation function", None

    return None, func_str


def _check_func_list(func: list[str | Callable]):
    func_str: list[str] = []

    for f in func:
        reason, f_str = _check_func_others(f)
        if reason is not None:
            return reason, None

        func_str += [f_str]

    return None, func_str


def _check_func_dict(func: dict[str, str | Callable], allow_nested):
    func_str = {}

    for k, f in func.items():
        if is_list_like(f):
            if allow_nested:
                reason, f_str = _check_func_list(f)
            else:
                raise pandas.errors.SpecificationError(
                    "nested renamer is not supported"
                )
        else:
            reason, f_str = _check_func_others(f)

        if reason is not None:
            return reason, None

        func_str[k] = f_str

    return None, func_str


def flatten_func(func):
    # all funcs are string

    out = []
    if is_dict_like(func):
        for v in func.values():
            out += v if isinstance(v, list) else [v]
    elif is_list_like(func):
        out += func
    else:
        assert isinstance(func, str)
        out += [func]

    return out


def check_func(func, allow_nested):
    """
    Check error and fallback on `func` parameter of DataFrame/Series.aggregate.

    Supported aggregate:
    - df.aggregate("sum")
    - df.aggregate(["sum", "max"])
    - df.aggregate({"a": ("sum", "max"), "b": "mean"})
    - df.aggregate(a=("a", "sum")) # Do nothing, just returns None

    Args:
        func (str or Callable or list[str | Callable] or dict[str, str |
        Callable]: aggregation functions.
        allow_nested (bool): whether to allow nested list in dict such as
        `df.aggregate({"a": ["sum", "max"]})`.

    Returns:
        str or None: fallback reason or None if valid.
        func or None: valid functions in str or None if invalid.
    """

    if func is None:
        return None, None
    elif is_dict_like(func):
        reason, func_str = _check_func_dict(func, allow_nested)
    elif is_list_like(func):
        reason, func_str = _check_func_list(func)
    else:
        reason, func_str = _check_func_others(func)

    if reason is not None:
        return reason, None

    if is_bool_non_bool_agg_mixed(flatten_func(func_str)):
        return "mixed of boolean and non-boolean aggregator", None

    return None, func_str


def check_func_named(kwargs):
    # a_sum=("a", "sum")

    out = {}
    for relabel in kwargs.keys():
        column, func = kwargs[relabel]
        reason, func_str = _check_func_others(func)
        if reason is not None:
            return reason, None
        out[relabel] = (column, func_str)

    # bool and non-bool mix check. Use fallback because mixed type is not
    # supported by fireducks.
    # TODO: bool and non-bool on different columns like x=("a", "all"), y=("b",
    # "mean") do not make mixed-type column.
    funcs = [v[1] for v in out.values()]
    if is_bool_non_bool_agg_mixed(funcs):
        return "mixed of boolean and non-boolean aggregator", None

    return None, out


class AggArgs:
    def __init__(self, funcs, columns, relabels):
        self.funcs = funcs
        self.columns = columns
        self.relabels = relabels

    def to_ir(self):
        funcs = make_tuple_of_vector_or_scalar_of_str(self.funcs)
        columns = make_tuple_of_column_names(self.columns)
        relabels = make_tuple_of_column_names(self.relabels)
        return funcs, columns, relabels

    def debug_print(self):
        for t in ["funcs", "columns", "relabels"]:
            print(f"{t} -> {getattr(self, t)}")  # noqa

    @classmethod
    def from_dict(cls, dic: dict):
        args = AggArgs([], [], [])
        for col, methods in dic.items():
            args.columns += [col]
            methods = infer_agg_method_name(methods)
            args.funcs += [methods]
        return args

    @classmethod
    def from_named(cls, kwargs):
        msg = "Must provide 'func' or tuples of '(column, aggfunc)"
        if not kwargs:
            raise TypeError(msg)

        args = AggArgs([], [], [])
        for relabel, tmp in kwargs.items():
            if not isinstance(tmp, tuple) or len(tmp) != 2:
                raise TypeError(msg)
            column, func = tmp
            func = infer_agg_method_name(func)
            # func must be a String (single function name), otherwise fallback
            if not isinstance(func, str):
                return None
            args.funcs += [func]
            args.columns += [column]
            args.relabels += [relabel]
        return args


def make_agg_args(func, *args, **kwargs):
    if func is None:
        assert not args
        return AggArgs.from_named(kwargs)

    # When func is not None, args and kwargs are arguments of func.
    # Not supported.
    if args or kwargs:
        return None

    if isinstance(func, dict):
        return AggArgs.from_dict(func)

    # below part is currently used from groupby-aggregate
    if isinstance(func, str) or _is_str_list(func):
        return AggArgs([func], [], [])

    return None


def check_args(func, decoded):
    """
    This method basically performs the following two checks for a given
    aggregate function, `func`:

      - Error Check: nv_xxx() is used internally to check `kwargs` contains
      only valid numpy parameters with default values. A valid parameter
      without default value or an unknown parameter will raise an `ValueError`.

      - Fallback Check: Whether to fallback based on the values of the
      pandas-related parameters like `skipna`, `numeric_only`, etc.

    Note:

    This method checks parameters that have the same meaning with both frame
    and series. Thus `axis` should NOT be checked here. At the moment,
    some sub checkers check for `axis` parameter.

    Args:
      func (str): valid function name

    Return:
      str or None: fallback reason or None if valid.
    """

    checker = _check_agg_funcs.get(func, None)
    assert checker is not None
    return checker(decoded)


def is_bool_non_bool_agg_mixed(funcs):
    s = set(funcs)
    return not len(s - {"any", "all"}) in [0, len(s)]


def _check_agg_variance(func, decoded):
    # pandas.NDFrame.var accepts `dtype`, `out`, and `keepdims` parameters
    # (not included in the method declaration) to accommodate calls from
    # numpy. If these arguments differ from their default values,
    # DataFrame.var will raise a ValueError.
    nv.validate_stat_ddof_func((), decoded.kwargs, fname=func)

    reason = decoded.is_not_default(exclude=["axis", "func", "ddof", "kwargs"])
    if not reason:
        if not (
            isinstance(decoded.ddof, (int, np.integer))
            or (
                isinstance(decoded.ddof, (float, np.floating))
                and decoded.ddof.is_integer()
            )
        ):
            reason = "`ddof` is not a type like int"

    return reason


def check_agg_all(decoded):
    nv.validate_logical_func((), decoded.kwargs, fname="all")
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_any(decoded):
    nv.validate_logical_func((), decoded.kwargs, fname="any")
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_count(decoded):
    # 'count' doesn't have kwargs
    return decoded.is_not_default(exclude=["axis", "func"])


def check_agg_kurt(decoded):
    # 'kurt' doesn't have `ddof`,
    # but pandas uses nv.validate_stat_ddof_func() to validate kwargs for 'kurt'
    nv.validate_stat_ddof_func((), decoded.kwargs, fname="kurt")
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_max(decoded):
    nv.validate_max((), decoded.kwargs)
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_mean(decoded):
    nv.validate_mean((), decoded.kwargs)
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_median(decoded):
    nv.validate_median((), decoded.kwargs)
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_min(decoded):
    nv.validate_min((), decoded.kwargs)
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_nunique(decoded):
    # 'nunique' doesn't have kwargs
    return decoded.is_not_default(exclude=["axis", "func"])


def check_agg_quantile(decoded):
    # 'quantile' doesn't have kwargs
    return decoded.is_not_default(exclude=["axis", "func"])


def check_agg_skew(decoded):
    # 'skew' doesn't have `ddof`,
    # but pandas uses nv.validate_stat_ddof_func() to validate kwargs for 'skew'
    nv.validate_stat_ddof_func((), decoded.kwargs, fname="skew")
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_std(decoded):
    return _check_agg_variance("std", decoded)


def check_agg_sum(decoded):
    nv.validate_sum((), decoded.kwargs)
    return decoded.is_not_default(exclude=["axis", "func", "kwargs"])


def check_agg_var(decoded):
    return _check_agg_variance("var", decoded)


# Dictionary mapping aggregation function names to their respective validation
# functions.  Each key is the name of an aggregation function, and the value is
# a function that checks the validity of arguments for that aggregation
# function.
_check_agg_funcs = {
    "all": check_agg_all,
    "any": check_agg_any,
    "count": check_agg_count,
    "kurt": check_agg_kurt,
    "max": check_agg_max,
    "mean": check_agg_mean,
    "median": check_agg_median,
    "min": check_agg_min,
    "nunique": check_agg_nunique,
    "quantile": check_agg_quantile,
    "size": None,
    "skew": check_agg_skew,
    "std": check_agg_std,
    "sum": check_agg_sum,
    "var": check_agg_var,
}


def _check_aggregate_args(
    cls: pandas.DataFrame | pandas.Series, func: str, args, kwargs
):
    # DataFrame/Series.size is not aggregation function. decode_args can
    # not be used.
    if func == "size":
        if args or kwargs:
            return "`size` does not support arguments"  # OK?
        return None

    # decoded `args` and `kwargs` into arguments of DataFrame/Series.{func}
    decoded = utils.decode_args(args, kwargs, getattr(cls, func))
    reason = check_args(func, decoded)
    if reason is not None:
        return reason

    return None


def check_aggregate_args(
    cls: pandas.DataFrame | pandas.Series, func: str | list[str], args, kwargs
):
    """Check `args` and `kwargs` of DataFrame/Series.aggregate as parameters of
    func"""

    if args:
        # Since `args` is not useful with builtin aggregator such as sum,
        # fireducks fallback when it is used. See #4270 for details.
        return f"{cls.__name__}.aggregate does not support args: {args}"

    if isinstance(func, str):
        return _check_aggregate_args(cls, func, args, kwargs)

    for f in func:
        reason = _check_aggregate_args(cls, f, args, kwargs)
        if reason is not None:
            return reason
    return None


def frame_check_integer_axis(func: str, axis: int):
    assert axis == 0 or axis == 1

    # fireducks does not support axis=1 for most of the functions
    if axis == 1 and func not in ("sum", "all", "any", "count", "mean"):
        return f"{func} does not support axis=1"

    return None


def make_aggregate_options(kwargs: dict) -> AggregateOptions:
    options = AggregateOptions()
    if "ddof" in kwargs:
        options.ddof = int(kwargs["ddof"])
    return options


def frame_check_axis(
    self: DataFrame, func: str, axis
) -> tuple[str | None, int | None]:
    """Check error and fallback on the axis argument for DataFrame aggregation."""

    reason = None
    # NOTE: take care of axis=None case, when supporting new aggregate method
    if axis is None:
        # methods that raises ValueError in pandas 2x
        if func in ["count", "nunique", "quantile"]:
            self._get_axis_number(axis)  # to raise error
        # methods that supports axis=None as axis=0 with
        # FutureWarning in pandas 2x
        elif func in ["sum", "var", "std"]:
            axis = 0
        elif func in ["median", "skew", "kurt"]:
            # axis=None is treated as axis=0 with FutureWarning in pandas 1x
            if utils._pd_version_under2:
                axis = 0
            else:
                # reduction to a scalar is not possible
                # calling self.<func>(axis=0).<func>(axis=0)
                reason = f"{func} doesn't support axis=None"
        elif func in ["mean", "max", "min"]:
            # axis=None is treated as axis=0 with FutureWarning in pandas 1x
            if utils._pd_version_under2:
                axis = 0
            else:
                axis = None  # reduction of a table to a scalar
        # for rest of the cases(all, any etc.): reduction of a table to a scalar
    else:
        axis = self._get_axis_number(axis)
        reason = frame_check_integer_axis(func, axis)

    if reason is not None:
        return reason, None

    return None, axis


# Ex: DataFrame.max, DataFrame.sum, etc.
def frame_agg_func(self: DataFrame, func: str, args, kwargs):
    # `func` is always valid because this function is called from inside
    # fireducks such as DataFrame.max.

    assert isinstance(self, DataFrame)
    assert isinstance(func, str)

    # DataFrame.size is not aggregation function. It does not come here.
    assert func != "size"

    # TODO: assert func is valid

    pandas_func = getattr(pandas.DataFrame, func)
    decoded = utils.decode_args(args, kwargs, pandas_func)

    reason, axis = frame_check_axis(self, func, decoded.axis)
    if reason is not None:
        return self._fallback_call(func, args, kwargs, reason=reason)

    reason = check_args(func, decoded)
    if reason is not None:
        return self._fallback_call(func, args, kwargs, reason=reason)

    options = make_aggregate_options(kwargs)
    func_arg = irutils.make_vector_or_scalar_of_str(func)
    # TODO: create ir.aggregate_table_scalar() and support all axis=None case
    if axis is None:
        if func == "mean":
            # when there are missing values present in the data,
            # self.mean(axis=0).mean(axis=0) might not produce correct output
            t_sum = self.sum(axis=0).sum(axis=0)
            t_cnt = self.count(axis=0).sum(axis=0)
            return t_sum / t_cnt
        else:
            # reduction of a table to a scalar: self.<func>(axis=0).<func>(axis=0)
            ret0 = Series._create(
                ir.aggregate(self._value, func_arg, 0, options)
            )
            return getattr(ret0, func)(axis=0)
    else:
        return Series._create(
            ir.aggregate(self._value, func_arg, axis, options)
        )


# Ex: Series.max
def series_agg_func(self: Series, func: str, args, kwargs):
    assert isinstance(self, Series)
    assert isinstance(func, str)
    # TODO: assert func is valid

    pandas_func = getattr(pandas.Series, func)
    decoded = utils.decode_args(args, kwargs, pandas_func)

    # check if axis is index, or 0, otherwise raise an error without fallback.
    # pandas.Series.{count,unique,quantile} dose not have axis argument,
    # implying axis=0
    if hasattr(decoded, "axis") and decoded.axis is not None:
        self._get_axis_number(decoded.axis)

    reason = check_args(func, decoded)
    if reason is not None:
        return self._fallback_call(func, args, kwargs, reason=reason)

    options = make_aggregate_options(kwargs)
    value = ir.aggregate_column_scalar(self._value, func, options)
    return _Scalar(value)._unwrap()


# Type 1. Ex: df.aggregate(["sum", "max"], *args, **kwargs)
def _frame_aggregate_all(self, decoded, m):
    assert not m.is_fallback()
    assert irutils._is_scalar_or_list_or_tuple_of(decoded.func, str)

    funcs = [decoded.func] if isinstance(decoded.func, str) else decoded.func
    for f in funcs:
        m.reason = frame_check_integer_axis(f, decoded.axis)
        if m.is_fallback():
            return m.fallback()

    m.reason = check_aggregate_args(
        pandas.DataFrame, funcs, decoded.args, decoded.kwargs
    )
    if m.is_fallback():
        return m.fallback()

    funcs = irutils.make_vector_or_scalar_of_str(decoded.func)
    options = make_aggregate_options(decoded.kwargs)
    value = ir.aggregate(self._value, funcs, decoded.axis, options)
    if isinstance(decoded.func, str):  # scalar
        return Series._create(value)
    return DataFrame._create(value)


def create_aggregate_specified_ir(value, aggArgs, axis):
    funcs, columns, relabels = aggArgs.to_ir()
    return ir.aggregate_specified(value, funcs, columns, relabels, axis)


# Type2: Ex. df.aggregate({"a": "sum", "b": ["max", "sum"]}, *args, **kwargs)
def _frame_aggregate_dict(self, decoded, m):
    assert not m.is_fallback()
    assert is_dict_like(decoded.func)

    if decoded.axis == 1:  # not supported for dict case
        return m.fallback(reason="unsupported aggregated args on axis=1")

    if decoded.args or decoded.kwargs:
        return m.fallback(
            reason="args and/or kwargs are used with dict aggregate"
        )

    aggArgs = AggArgs.from_dict(decoded.func)
    value = create_aggregate_specified_ir(self._value, aggArgs, decoded.axis)

    if all([isinstance(func, str) for func in aggArgs.funcs]):
        return Series._create(value)  # Series when all funcs are scalar

    return DataFrame._create(value)


# Type3: Ex. df.aggregate(a_sum=("a", "sum"))
def _frame_aggregate_named(self, decoded, m):
    assert not m.is_fallback()
    assert decoded.func is None

    # Because func in `df.aggregate(func=None, *args, **kwargs)` is None,
    # args is always empty
    assert not decoded.args

    if decoded.axis == 1:  # not supported for named case
        return m.fallback(reason="unsupported aggregated args on axis=1")

    m.reason, kwargs = check_func_named(decoded.kwargs)
    if m.is_fallback():
        return m.fallback()

    aggArgs = AggArgs.from_named(kwargs)
    assert aggArgs is not None

    value = create_aggregate_specified_ir(self._value, aggArgs, decoded.axis)
    return DataFrame._create(value)


# DataFrame.aggregate
def frame_aggregate(self, *args, **kwargs):
    # Three types:
    # 1. df.aggregate("sum") or df.aggregate(["sum", "max"])
    # 2. df.aggregate({"a": "sum", "b": "max"})
    # 3. df.aggregate(a_sum=("a", "sum"))

    # pandas signature is `aggregate(self, func=None, axis=0, *args, **kwargs)`
    decoded = utils.decode_args(args, kwargs, pandas.DataFrame.aggregate)
    assert hasattr(decoded, "func")
    assert hasattr(decoded, "axis")

    m = FallbackMonad(self, "aggregate", args, kwargs)

    # axis=None is not allowed in DataFrame.aggregate
    decoded.axis = self._get_axis_number(decoded.axis)

    m.reason, decoded.func = check_func(decoded.func, allow_nested=True)
    if m.is_fallback():
        return m.fallback()

    if decoded.func is None:  # Type3
        return _frame_aggregate_named(self, decoded, m)
    elif is_dict_like(decoded.func):  # Type2
        return _frame_aggregate_dict(self, decoded, m)
    return _frame_aggregate_all(self, decoded, m)  # Type1


# s.aggregate("sum", *args, **kwargs) => scalar
def _series_aggregate_scalar(self: Series, decoded, m: FallbackMonad):
    assert not m.is_fallback()
    assert isinstance(decoded.func, str)

    m.reason = check_aggregate_args(
        pandas.Series, decoded.func, decoded.args, decoded.kwargs
    )
    if m.is_fallback():
        return m.fallback()

    options = make_aggregate_options(decoded.kwargs)
    value = ir.aggregate_column_scalar(self._value, decoded.func, options)
    return _Scalar(value)._unwrap()


def series_create_aggregate_ir(value, func, options, index=None):
    func = irutils.make_vector_or_scalar_of_str(func)
    value = ir.aggregate(value, func, axis=0, options=options)
    ret = Series._create(value)
    if index is not None:
        ret._set_axis(index, _inplace_index_setter=True)
    return ret


# s.aggregate(["sum", "max"], *args, **kwargs)
def _series_aggregate_list(self: Series, decoded, m: FallbackMonad):
    assert not m.is_fallback()
    assert is_list_like(decoded.func) and not is_dict_like(decoded.func)

    m.reason = check_aggregate_args(
        pandas.Series, decoded.func, decoded.args, decoded.kwargs
    )
    if m.is_fallback():
        return m.fallback()

    options = make_aggregate_options(decoded.kwargs)
    return series_create_aggregate_ir(self._value, decoded.func, options)


# s.aggregate({"foo": "sum", "bar": "max"}, *args, **kwargs)
def _series_aggregate_dict(self: Series, decoded, m: FallbackMonad):
    assert not m.is_fallback()
    assert is_dict_like(decoded.func)  # is_list_like returns True with dict

    funcs = list(decoded.func.values())
    index_names = list(decoded.func.keys())

    if decoded.args or decoded.kwargs:
        return m.fallback(
            reason="args and/or kwargs are used with dict aggregate"
        )

    options = AggregateOptions()
    return series_create_aggregate_ir(self._value, funcs, options, index_names)


# s.aggregate(foo="sum", bar="max")
def _series_aggregate_named(self: Series, decoded, m: FallbackMonad):
    assert not m.is_fallback()
    assert decoded.func is None
    assert not decoded.args

    # Named aggregate is same as dict aggregate.
    # Ex: df.aggregate(foo="sum", bar="max"]) is same as df.aggregate({"foo":
    # "sum", "bar": "max"})
    func = dict(decoded.kwargs.items())

    m.reason, func = check_func(func, allow_nested=False)
    if m.is_fallback():
        return m.fallback()

    assert isinstance(func, dict)

    options = AggregateOptions()
    return series_create_aggregate_ir(
        self._value, list(func.values()), options, list(func.keys())
    )


# Series.aggregate
def series_aggregate(self, *args, **kwargs):
    # 1. s.aggregate("sum") => scalar
    # 2. s.aggregate(["sum", "max"]) => Series
    # 3. s.aggregate({"foo": "sum", "bar": "max"}) => Series
    # 4. s.aggregate(foo="sum", bar="max") => Series

    # pandas signature is `aggregate(self, func=None, axis=0, *args, **kwargs)`
    decoded = utils.decode_args(args, kwargs, pandas.Series.aggregate)
    assert hasattr(decoded, "func")
    assert hasattr(decoded, "axis")

    m = FallbackMonad(self, "aggregate", args, kwargs)

    # axis=None is not allowed in Series.aggregate
    decoded.axis = self._get_axis_number(decoded.axis)

    m.reason, decoded.func = check_func(decoded.func, allow_nested=False)
    if m.is_fallback():
        return m.fallback()

    if decoded.func is None:
        return _series_aggregate_named(self, decoded, m)
    elif isinstance(decoded.func, str):
        return _series_aggregate_scalar(self, decoded, m)
    elif is_dict_like(decoded.func):
        return _series_aggregate_dict(self, decoded, m)
    return _series_aggregate_list(self, decoded, m)
