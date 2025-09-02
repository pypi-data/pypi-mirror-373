# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from datetime import date, datetime, timezone, time
from typing import Tuple
import logging
import sys

import re
import numpy as np
import pandas
from pandas.util._decorators import deprecate_nonkeyword_arguments
from pandas.util._validators import validate_bool_kwarg, validate_ascending
from pandas.core.accessor import CachedAccessor
import pandas.api.extensions as pandas_extensions
from pandas._libs.lib import is_all_arraylike
from pandas.core.dtypes.common import is_integer, is_dict_like
from pandas.io.formats.info import SeriesInfo
from pandas.compat.numpy import function as nv

from fireducks import ir, irutils
from fireducks import pandas as fireducks_pandas
import fireducks.core

from fireducks.pandas.generic import (
    FireDucksPandasCompat,
    _Scalar,
    _install_aggregators,
    _install_binops,
    _install_unary_op_fallbacks,
    _install_fallback_mutating_method,
    _wrap_pandas,
)
import fireducks.pandas.utils as utils
from fireducks.pandas.utils import _unwrap
from fireducks.pandas.wrappers import Index, MultiIndex, DatetimeIndex

from fireducks.pandas.binop import (
    get_binop_vector_scalar,
    get_binop_vector_vector,
)

logger = logging.getLogger(__name__)


class CategoricalAccessor(utils.ReadOnlyAccessor):
    def __init__(self, obj):
        object.__setattr__(self, "obj", obj)
        obj._fireducks_meta.add_internal_referrer(self)

    def _unwrap(self, reason):
        return utils.fallback_attr(
            self.obj._unwrap, "cat", reason="CategoricalAccessor._unwrap"
        )

    @property
    def categories(self):
        return Index(
            Series._create(ir.cat_categories(self.obj._value)).to_pandas()
        )


def add_extractors(fields):
    def adder(cls):
        for field in fields:

            def getter(self, name=field):
                return Series._create(
                    ir.datetime_extract(self.obj._value, name)
                )

            prop = property(fget=getter)  # TODO: fset is required?
            setattr(cls, field, prop)
        return cls

    return adder


@add_extractors(
    [
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "second",
        "week",
        "quarter",
        "day_of_week",
        "day_of_year",
        "microsecond",
        "millisecond",  # not in pandas
        "subsecond",  # not in pandas
        "nanosecond",
        "is_leap_year",
        "days_in_month",
        "date",
        "time",
    ]
)
class DatetimeMethods(utils.ReadOnlyAccessor):
    def __init__(self, obj):
        object.__setattr__(self, "obj", obj)
        obj._fireducks_meta.add_internal_referrer(self)

    def _unwrap(self, reason):
        return utils.fallback_attr(
            self.obj._unwrap, "dt", reason="DatetimeMethods._unwrap"
        )

    def day_name(self, locale=None):
        mapper = utils.get_cal_name_mapper("day_name", locale)
        return self.dayofweek._map(mapper, map_as_take=True)

    def month_name(self, locale=None):
        mapper = utils.get_cal_name_mapper("month_name", locale)
        return self.month._map(mapper, map_as_take=True)

    def strftime(self, date_format):
        reason = None
        if not isinstance(date_format, str):
            reason = (
                f"unsupported format of type: '{type(date_format).__name__}'"
            )
        else:
            if "%%S" in date_format:
                reason = f"unsupported format: '{date_format}'"

        if reason:
            return utils.fallback_call(
                self._unwrap,
                "strftime",
                args=[date_format],
                reason=reason,
            )
        str_format = irutils.make_scalar(date_format)
        return Series._create(ir.strftime(self.obj._value, str_format))

    def total_seconds(self):
        return Series._create(ir.datetime_total_seconds(self.obj._value))


DatetimeMethods.dayofweek = DatetimeMethods.day_of_week
DatetimeMethods.weekday = DatetimeMethods.day_of_week
DatetimeMethods.dayofyear = DatetimeMethods.day_of_year
DatetimeMethods.weekofyear = DatetimeMethods.week
DatetimeMethods.daysinmonth = DatetimeMethods.days_in_month


class StringMethods(utils.ReadOnlyAccessor):
    def __init__(self, obj):
        object.__setattr__(self, "obj", obj)

        # When once StringMethods is created, it is cached in obj. Thus,
        # StringMethod and Series, i.e. self and obj will be deleted at the
        # same time.  It means that we never have to remove self from the
        # internal referrers.
        obj._fireducks_meta.add_internal_referrer(self)

    def _unwrap(self, reason):
        return utils.fallback_attr(
            self.obj._unwrap,
            "str",
            reason="StringMethods._unwrap",
            stacklevel=8,
        )

    def _with(self, x, op, pat, na):
        reason = []

        if not isinstance(pat, str):
            reason.append(f"{x} with first argument is not of string-type")

        supported_na = {None, True, False}
        if na not in supported_na:
            reason.append(f"{x} with unsupported na: {na}")

        if len(reason) > 0:
            return utils.fallback_call(
                self._unwrap,
                x,
                args=[pat],
                reason="; ".join(reason),
            )

        na_ = -1 if na is None else int(na)
        return Series._create(op(self.obj._value, pat, na_))

    def __getitem__(self, key):
        if isinstance(key, int):
            key = (
                slice(key, key + 1, 1) if key >= 0 else slice(key, key - 1, -1)
            )
            return self.slice(
                start=key.start, stop=key.stop, step=key.step, as_element=True
            )
        if isinstance(key, slice):
            return self.slice(start=key.start, stop=key.stop, step=key.step)
        reason = "key is neither an integer nor a slice"
        return utils.fallback_call(
            self._unwrap, "__getitem__", args=[key], reason=reason
        )

    def match(self, pat, case=True, flags=0, na=None):
        if isinstance(pat, str):
            pat = "^" + pat if not pat.startswith("^") else pat
            return self.contains(
                pat, case=case, flags=flags, na=na, regex=True
            )

        reason = "match with non-string pattern"
        return utils.fallback_call(
            self._unwrap,
            "match",
            args=[pat, case, flags, na],
            reason=reason,
        )

    def contains(self, pat, case=True, flags=0, na=None, regex=True):
        reason = []

        if not isinstance(pat, str):
            reason.append("contains with first argument is not of string-type")

        supported_flags = {0, re.IGNORECASE}
        if flags not in supported_flags:
            reason.append(f"contains with unsupported flags: {flags}")

        supported_na = {None, True, False}
        if na not in supported_na:
            reason.append(f"contains with unsupported na: {na}")

        if len(reason) > 0:
            return utils.fallback_call(
                self._unwrap,
                "contains",
                args=[pat, case, flags, na, regex],
                reason="; ".join(reason),
            )

        # flags=re.IGNORECASE has more priority over "case" parameter
        ignorecase = True if flags == re.IGNORECASE else not case
        na_ = -1 if na is None else int(na)

        return Series._create(
            ir.str_contains(self.obj._value, pat, ignorecase, na_, regex)
        )

    def cat(self, others=None, sep=None, na_rep=None, join="left"):
        reason = []

        if others is None:
            reason.append("Unsupported 'others' = None")
        elif isinstance(others, (np.ndarray, tuple, list, pandas.Index)):
            others = Series(others)
        elif not isinstance(others, (Series, fireducks_pandas.DataFrame)):
            reason.append(
                f"Unsupported 'others' of type {type(others).__name__}"
            )

        if sep is None:
            sep = ""
        elif not isinstance(sep, str):
            reason.append(f"Unsupported 'sep' of type {type(sep).__name__}")

        if na_rep is not None:
            reason.append("'na_rep' is not None")

        if join != "left":
            reason.append(f"Unsupported 'join' = {join}")

        if len(reason) > 0:
            return utils.fallback_call(
                self._unwrap,
                "cat",
                args=[others, sep, na_rep, join],
                reason="; ".join(reason),
            )

        return Series._create(
            ir.str_concat(self.obj._value, others._value, sep)
        )

    def endswith(self, pat, na=None):
        return self._with("endswith", ir.str_endswith, pat, na)

    def slice(self, start=None, stop=None, step=None, as_element=False):
        start = start or 0
        stop = stop or 2**63 - 1  # int64 max.
        step = step or 1
        as_element = validate_bool_kwarg(as_element, "as_element")
        return Series._create(
            ir.str_slice(self.obj._value, start, stop, step, as_element)
        )

    def _split(
        self, pat=None, *, n=-1, expand=False, regex=None, reverse=False
    ):
        reason = []

        if pat is None:
            pat = " "
        elif not isinstance(pat, str):
            reason.append(f"Unsupported 'pat' of type {type(pat).__name__}")
        elif len(pat) == 0:
            reason.append(f"Unsupported 'pat' of empty string")

        if not isinstance(n, int):
            reason.append(f"Unsupported 'n' of type {type(n).__name__}")

        if not isinstance(expand, (bool, np.bool_)):
            reason.append(f"Unsupported 'expand' = {expand}")

        if len(reason) > 0:
            # pandas rsplit doesn't have parameter "regex"
            kwargs = {"n": n, "expand": expand}
            if not reverse:
                name = "split"
                kwargs["regex"] = regex
            else:
                name = "rsplit"
                assert regex is None

            return utils.fallback_call(
                self._unwrap,
                name,
                args=[pat],
                kwargs=kwargs,
                reason="; ".join(reason),
            )

        n = max(-1, n)
        if regex in {True, False, None}:
            regex = len(pat) > 1 if regex is None else regex
        else:
            # according to pandas behavior. all true values would be treated
            # as true. e.g., regex=2.3 would be treated as regex=True
            regex = bool(regex)

        expand = bool(expand)
        out_cls = fireducks_pandas.DataFrame if expand else Series
        return out_cls._create(
            ir.str_split(self.obj._value, pat, n, expand, regex, reverse)
        )

    def split(self, pat=None, *, n=-1, expand=False, regex=None):
        return self._split(pat, n=n, expand=expand, regex=regex, reverse=False)

    def rsplit(self, pat=None, *, n=-1, expand=False, regex=None):
        return self._split(pat, n=n, expand=expand, regex=regex, reverse=True)

    def startswith(self, pat, na=None):
        return self._with("startswith", ir.str_startswith, pat, na)

    def pad(self, width, side="left", fillchar=" "):
        """
        Pad strings in the Series/Index up to width.
        """
        if not isinstance(width, int):
            raise TypeError(
                f"width must be of integer type, not {type(width).__name__}"
            )
        if side not in ("left", "right", "both"):
            raise ValueError(f"Invalid side: {side}")
        if isinstance(fillchar, str) and len(fillchar) > 1:
            raise TypeError("fillchar must be a character, not str")
        if side != "both":
            return Series._create(
                ir.str_pad(self.obj._value, max(0, width), side, fillchar)
            )
        reason = "pad with side=both"
        return utils.fallback_call(
            self._unwrap,
            "pad",
            args=[width, side, fillchar],
            reason=reason,
        )

    def zfill(self, width):
        """
        Pad strings in the Series/Index by prepending ‘0’ characters.
        """
        return self.pad(width, side="left", fillchar="0")

    def _strip(self, to_strip, side):
        if to_strip is None:
            return Series._create(ir.str_trim_wsp(self.obj._value, side))
        elif isinstance(to_strip, str):
            return Series._create(ir.str_trim(self.obj._value, to_strip, side))
        else:
            reason = f"to_strip of type: {type(to_strip).__name__}"
            func = (
                "lstrip"
                if side == "left"
                else ("rstrip" if side == "right" else "strip")
            )
            return utils.fallback_call(
                self._unwrap, func, args=[to_strip], reason=reason
            )

    def strip(self, to_strip=None):
        """
        Remove leading and trailing characters.
        """
        return self._strip(to_strip, side="both")

    def lstrip(self, to_strip=None):
        """
        Remove leading characters.
        """
        return self._strip(to_strip, side="left")

    def rstrip(self, to_strip=None):
        """
        Remove trailing characters.
        """
        return self._strip(to_strip, side="right")

    def replace(self, pat, repl, n=-1, case=None, flags=0, regex=False):
        reason = []

        if not isinstance(pat, str):
            reason.append("replace with 'pat' is not of string-type")

        if not isinstance(repl, str):
            reason.append("replace with 'repl' is not of string-type")

        if not isinstance(n, int):
            reason.append("replace with 'n' is not of integer-type")

        if flags != 0:
            reason.append("replace with non-zero 'flags'")

        supported_case = {None, True}
        if case not in supported_case:
            reason.append(f"replace with unsupported case: {case}")

        if len(reason) > 0:
            return utils.fallback_call(
                self._unwrap,
                "replace",
                args=[pat, repl, n, case, flags, regex],
                reason="; ".join(reason),
            )

        # according to pandas behavior. all true values would be treated
        # as true. e.g., regex=2.3 would be treated as regex=True
        regex = bool(regex)
        n = max(-1, n)

        return Series._create(
            ir.str_replace(self.obj._value, pat, repl, n, regex)
        )

    def _str_unary_method(self, method, return_bool=False):
        if return_bool:
            value = ir.str_unary_bool_returning_method(self.obj._value, method)
        else:
            value = ir.str_unary_method(self.obj._value, method)
        return Series._create(value)

    def lower(self):
        """
        Converts all characters to lowercase
        """
        return self._str_unary_method("lower")

    def upper(self):
        """
        Converts all characters to uppercase
        """
        return self._str_unary_method("upper")

    def capitalize(self):
        """
        Converts all the Strings in the target Series to be capitalized.
        """
        return self._str_unary_method("capitalize")

    def title(self):
        """
        Converts all the Strings in the target Series to titlecase.
        """
        return self._str_unary_method("title")

    def swapcase(self):
        """
        Converts all the Strings in the target Series to swapcase.
        """
        return self._str_unary_method("swapcase")

    # this method is not available in native pandas, but added in fireducks
    # pandas way of reversing string column:
    # df[cname].str.apply(lambda x: x[::-1])
    def reverse(self):
        """
        Reverses all the Strings in the target Series.
        """
        return self._str_unary_method("reverse")

    def len(self):
        """
        Computes the length of each element
        """
        return self._str_unary_method("len")

    def islower(self):
        """
        Checks whether all characters in each string are lowercase.
        """
        return self._str_unary_method("islower", return_bool=True)

    def isupper(self):
        """
        Checks whether all characters in each string are uppercase.
        """
        return self._str_unary_method("isupper", return_bool=True)

    def isalnum(self):
        """
        Checks whether all characters in each string are alphanumeric.
        """
        return self._str_unary_method("isalnum", return_bool=True)

    def isalpha(self):
        """
        Checks whether all characters in each string are alphabetic.
        """
        return self._str_unary_method("isalpha", return_bool=True)

    def isnumeric(self):
        """
        Checks whether all characters in each string are numeric.
        """
        return self._str_unary_method("isnumeric", return_bool=True)

    def isdecimal(self):
        """
        Checks whether all characters in each string are decimal.
        """
        return self._str_unary_method("isdecimal", return_bool=True)

    def isspace(self):
        """
        Checks whether all characters in each string are whitespace.
        """
        return self._str_unary_method("isspace", return_bool=True)

    def istitle(self):
        """
        Checks whether all characters in each string are titlecase.
        """
        return self._str_unary_method("istitle", return_bool=True)


def _from_pandas_series(obj: pandas.Series):
    """
    Returns fire.Value
    """
    logger.debug("_from_pandas_series")
    if fireducks.core.get_ir_prop().has_series:
        return ir.from_pandas_series(
            fireducks.core.make_available_value(obj, ir.Ty_pyobj)
        )

    # When Series.name is None, pandas use '0' as column name.
    # To keep it None, it is explicitly given.
    if obj.name is None:
        df = pandas.DataFrame({None: obj})
    else:
        df = pandas.DataFrame(obj)
    from fireducks.pandas.frame import _from_pandas_frame

    return _from_pandas_frame(df)


def _setup_Series(cls):
    _install_aggregators(cls, pandas.Series)
    _install_binops(cls, pandas.Series)
    _install_unary_op_fallbacks(cls, pandas.Series)
    _install_fallback_mutating_method(cls, "__delitem__")

    # NOTE: pandas.Series has __long__. But we don't define it because it
    # should be for backward compat with python2
    utils.install_fallbacks(
        cls, ["__contains__", "__float__", "__int__"], pandas.Series
    )

    _wrap_pandas(cls, pandas.Series)
    return cls


def _parse_series_creation_args(args, kwargs):
    value = kwargs.get("_value")
    hint = kwargs.get("__hint")

    obj = None
    if value is None:
        obj = kwargs.pop("__fireducks_from_pandas", None)
        if obj is None:
            if (
                len(kwargs) == 0
                and len(args) == 1
                and isinstance(args[0], Series)
            ):
                value = ir.copy(args[0]._value, deep=True)
                return value, None, hint

            reason = "args of Series.__init__"
            if kwargs is None and isinstance(args[0], list) and len(args) == 0:
                # to suppress FutureWarning specifying dtype as np.float64
                obj = pandas.Series(
                    *utils._unwrap(args, reason=reason), dtype=np.float64
                )
            else:
                obj = pandas.Series(
                    *utils._unwrap(args, reason=reason),
                    **utils._unwrap(kwargs, reason=reason),
                )
        assert isinstance(obj, pandas.Series)
        value = _from_pandas_series(obj)

    return value, obj, hint


def arraylike_to_series(array, ser):
    """
    construct Series from array-like objects by mocking an input Series.
    The output Series will have same name and index
    as in input Series to be mocked
    """
    assert isinstance(ser, Series)
    cname = ser.name
    empty_frame_with_index = ser.to_frame()[[]]
    empty_frame_with_index[cname] = array
    return empty_frame_with_index.squeeze()


# Wrap PyTable
@_setup_Series
class Series(FireDucksPandasCompat):
    cat = CachedAccessor("cat", CategoricalAccessor)
    dt = CachedAccessor("dt", DatetimeMethods)
    str = CachedAccessor("str", StringMethods)

    def _fire_getrefcount(self):
        """
        _fire_getrefcount should return external reference count to this
        object. Reference from self._value **should** be included because it is
        removed by the caller.
        """

        # -1: reference from the argument of getrefcount
        # -1: reference from `self` of this method
        count = sys.getrefcount(self) - 2

        for referrer in self._fireducks_meta.get_internal_referrers():
            if isinstance(referrer, (StringMethods, DatetimeMethods)):
                # StringMethods/DatetimeMethods has four known internal
                # referrers:
                #   - Series.str/dt
                #   - Series._fireducks_meta._internal_referrers
                #   - `referrer` variable of this loop
                #   - argument of `sys.getrefcount`
                cnt = sys.getrefcount(referrer)
                logger.debug(
                    "Series._fire_getrefcount: this object is referred "
                    "by %s which has %d referrers but %d are "
                    "internal(will be ignored).",
                    type(referrer).__name__,
                    cnt,
                    4,
                )
                assert cnt >= 4
                # replace a reference to self from StringMethods(- 1) with
                # external referrers to StringMethods(+ cnt - 4)
                count = count - 1 + cnt - 4
            else:
                logger.debug(
                    "Series._fire_getrefcount: unknown referrer: %s",
                    type(referrer),
                )

        logger.debug("Series._fire_getrefcount: adjusted count=%s", count)
        return count

    def __init__(self, *args, **kwargs):
        value, obj, hint = _parse_series_creation_args(args, kwargs)
        super().__init__(value, pandas_object=obj, hint=hint)

        if fireducks.core.get_fireducks_options().benchmark_mode:
            self._evaluate()

    def __setstate__(self, state):
        logger.debug("Series.__setstate__")
        obj = object.__new__(pandas.Series)
        obj.__setstate__(state)
        self.__init__(__fireducks_from_pandas=obj)

    @classmethod
    def _create(cls, value, *, hint=None):
        assert value.type() == ir.TableType
        return Series(_value=value)

    def _create_or_inplace(self, value, inplace):
        inplace = validate_bool_kwarg(inplace, "inplace")
        if inplace:
            return self._rebind(value, invalidate_cache=True)
        return Series._create(value).__finalize__(self)

    @classmethod
    def _get_axis_number(cls, axis):
        # For some aggregation methods in Pandas 1.5.3, the default value for
        # the `axis` argument is no_default.
        if utils._pd_version_under2 and axis == pandas_extensions.no_default:
            axis = 0
        return pandas.Series._get_axis_number(axis)

    @classmethod
    def from_pandas(cls, obj):
        if not isinstance(obj, pandas.Series):
            raise RuntimeError(
                "Series.from_pandas: illegal argument: "
                f"{obj.__class__.__name__}"
            )
        return Series(__fireducks_from_pandas=obj)

    def _build_binop(
        self, rhs, op_str: str, op_original: str, args, kwargs, inplace: bool
    ):
        def _fallback(reason, rhs_=rhs):
            fallback = self._get_fallback(inplace)
            return fallback(
                op_original,
                args=(rhs_,),
                kwargs=kwargs,
                reason=reason,
            )

        if isinstance(rhs, (list, range, np.ndarray)):
            # arraylike to series conversion
            rhs = arraylike_to_series(rhs, self)

        rhs_t = type(rhs).__name__
        reason = None
        opc = None

        if args:
            reason = f"args is used: {args}"
        elif kwargs:
            reason = f"kwargs is used: {kwargs}"
        # TODO: use irable_scalar
        elif rhs is pandas.NaT or isinstance(
            rhs,
            (
                bool,
                int,
                float,
                str,
                np.bool_,
                np.int32,
                np.int64,
                np.uint64,
                np.float32,
                np.float64,
                date,
                time,
                np.datetime64,
                pandas.Timestamp,
                pandas.Timedelta,
            ),
        ):
            opc = get_binop_vector_scalar(op_str)
            rhs = irutils.make_scalar(rhs)
        elif isinstance(rhs, Series):
            opc = get_binop_vector_vector(op_str)
            rhs = rhs._value
        elif isinstance(rhs, _Scalar):
            opc = get_binop_vector_scalar(op_str)
            rhs = rhs._value
        elif isinstance(rhs, datetime) and rhs.tzinfo is None:
            # timezone-naive datetime can be converted to !fireducks.scalar
            opc = get_binop_vector_scalar(op_str)
            ts = int(rhs.replace(tzinfo=timezone.utc).timestamp() * 1e9)
            rhs = ir.make_scalar_timestamp_ns(ts)

        if reason is None and opc is None:
            reason = f"unknown op: '{op_str}' on 'Series' and '{rhs_t}'"

        if reason is not None:
            return _fallback(reason)

        logger.debug("build_binop: %s", type(self))
        op = fireducks.core.build_op(
            opc, [ir.TableType], [self._value, rhs], chaining=True
        )

        if inplace:
            self._rebind(op.outs[0], invalidate_cache=True)
            return self
        return Series._create(op.outs[0])

    def __abs__(self):
        return self.abs()

    def _to_pandas(self, options=None):
        ir_prop = fireducks.core.get_ir_prop()

        if (not ir_prop.has_series) and ir_prop.has_metadata:
            from fireducks.pandas.frame import _to_pandas_frame_metadata

            result = _to_pandas_frame_metadata(self._value, options)
            assert (
                isinstance(result, pandas.DataFrame)
                and len(result.columns) <= 1  # 0 means empty Series
            ), f"{type(result)}[{len(result.columns)}] is not pandas.Series"
            if len(result.columns) == 0:
                return pandas.Series(index=result.index)
            return result.iloc[:, 0]
        elif ir_prop.has_series:
            value = ir.to_pandas_series(self._value)
            result = fireducks.core.evaluate([value], options)[0]
            assert isinstance(
                result, pandas.Series
            ), f"{type(result)} is not pandas.Series"
            return result

        # Other cases are not supported because no backend requires it.
        assert False, "No supported IR property"

    def __getitem__(self, key):
        logger.debug("Series.__getitem__: type(key)=%s", type(key))
        to_filter, mask, ignore_index = utils.is_filter_like(key)
        if to_filter:
            return Series._create(
                ir.filter(self._value, mask._value, no_align=ignore_index)
            )

        elif isinstance(key, slice) and utils.is_int_or_none_slice(key):
            if key.step is None or key.step == 1:
                return self._slice(key)

        if (
            fireducks.core.get_fireducks_options().fast_fallback
            and self._fireducks_meta.is_cached("pandas_object")
            and not isinstance(key, _Scalar)
        ):
            obj = self._fireducks_meta.get_cache("pandas_object")
            ret = obj.__getitem__(utils._unwrap(key))
            ret = utils._wrap(ret)
            return ret

        reason = f"Unsupported key type: {type(key)}"
        return self._fallback_call("__getitem__", args=(key,), reason=reason)

    def __getattr__(self, name):
        logger.debug("Series.__getattr__: name=%s", name)

        if name.startswith("_fireducks"):
            raise AttributeError(name)

        unsupp = [
            # avoiding unnecessary fallback for methods which might be called
            # from utilities like ipython display formatters...
            "_ipython_display_",
            "_ipython_canary_method_should_not_exist_",
            # avoiding unnecessary fallback for numpy, pandas does not have these attribute.
            "__array_function__",
            "__array_interface__",
            "__array_struct__",
            "__name__",
        ]
        repr_unsupp = [
            "pretty",
            "svg",
            "png",
            "jpeg",
            "html",
            "javascript",
            "markdown",
            "latex",
            "mimebundle",
            "pdf",
            "json",
        ]
        if name in unsupp + ["_repr_" + x + "_" for x in repr_unsupp]:
            return object.__getattribute__(self, name)

        reason = f"{type(self).__name__}.__getattr__ for {name} is called"
        return utils.fallback_attr(self._unwrap, name, reason)

    def __invert__(self):
        return Series._create(ir.invert(self._value))

    def __len__(self):
        return self.shape[0]

    def __neg__(self):
        return Series._create(ir.negate(self._value))

    def __round__(self, decimals=0):
        return self.round(decimals)

    def __repr__(self):
        ret, is_trunc = self.__get_trunc_repr_method_result__(
            method="__repr__"
        )
        if is_trunc:
            truncated_shape_info = ret.split("\n")[-1]
            actual_shape_info = re.sub(
                r"Length: [0-9]*",
                f"Length: {len(self)}",
                truncated_shape_info,
            )
            # replacing truncated shape info with actual shape info
            truncated_shape_info_len = len(truncated_shape_info)
            return ret[:-truncated_shape_info_len] + actual_shape_info
        else:
            return ret

    def __setattr__(self, name, value):
        logger.debug("Series.__setattr__: name=%s", name)
        if name in ["_value", "index", "name"]:
            object.__setattr__(self, name, value)
        else:
            self._fallback_mutating_method("__setattr__", args=[name, value])

    def __setitem__(self, key, value):
        logger.debug("Series.__setitem__")
        reason = "Series.__setitem is always fallback"
        self._fallback_mutating_method(
            "__setitem__", args=[key, value], reason=reason, stacklevel=8
        )

    def abs(self):
        return Series._create(ir.abs(self._value))

    def aggregate(self, *args, **kwargs):
        from fireducks.pandas.aggregate import series_aggregate

        return series_aggregate(self, *args, **kwargs)

    agg = aggregate

    def _agg_func(self, func, args, kwargs):
        from fireducks.pandas.aggregate import series_agg_func

        return series_agg_func(self, func, args, kwargs)

    def between(self, *args, **kwargs):
        decoded = utils.decode_args(args, kwargs, pandas.Series.between)

        inclusive = decoded.inclusive
        if inclusive not in ["both", "neither", "left", "right"]:
            raise ValueError(
                "Inclusive has to be either string of 'both',"
                "'left', 'right', or 'neither'."
            )

        left = decoded.left
        right = decoded.right
        if isinstance(left, datetime) and isinstance(right, datetime):
            if left.tzinfo is None and right.tzinfo is None:
                # timezone-naive datetime can be converted to !fireducks.scalar
                lts = int(left.replace(tzinfo=timezone.utc).timestamp() * 1e9)
                rts = int(right.replace(tzinfo=timezone.utc).timestamp() * 1e9)
                left = ir.make_scalar_timestamp_ns(lts)
                right = ir.make_scalar_timestamp_ns(rts)
                return Series._create(
                    ir.between(self._value, left, right, inclusive)
                )

        if irutils.irable_scalar(left) and irutils.irable_scalar(right):
            left = irutils.make_scalar(left)
            right = irutils.make_scalar(right)
            return Series._create(
                ir.between(self._value, left, right, inclusive)
            )

        # otherwise: normal execution
        lmask = (
            self >= left
            if inclusive == "left" or inclusive == "both"
            else self > left
        )
        rmask = (
            self <= right
            if inclusive == "right" or inclusive == "both"
            else self < right
        )
        return lmask & rmask

    def corr(self, *args, **kwargs):
        decoded = utils.decode_args(args, kwargs, pandas.Series.corr)
        reason = []

        if not isinstance(decoded.other, Series):
            reason.append(
                "unsupported 'other' of type ="
                f"'{type(decoded.other).__name__}'"
            )

        supported_methods = ["pearson"]
        if isinstance(decoded.method, str):
            if decoded.method not in supported_methods:
                reason.append(f"unsupported method={decoded.method}")
        else:
            reason.append(
                "unsupported 'method' of type ="
                f"'{type(decoded.method).__name__}'"
            )

        if decoded.min_periods is None:
            decoded.min_periods = 1
        elif not isinstance(decoded.min_periods, int):
            reason.append(f"unsupported min_periods={decoded.min_periods}")

        decoded.min_periods = max(0, decoded.min_periods)

        if len(reason) > 0:
            return self._fallback_call(
                "corr",
                args,
                kwargs,
                reason="; ".join(reason),
            )
        return _Scalar(
            ir.series_corr(
                self._value,
                decoded.other._value,
                decoded.method,
                decoded.min_periods,
            )
        )._unwrap()

    def drop_duplicates(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.drop_duplicates)
        arg.inplace = validate_bool_kwarg(arg.inplace, "inplace")
        supported_keep = {"first", "last", False}

        # ignore_index is introduced in pandas-2
        ignore_index = (
            False
            if utils._pd_version_under2
            else validate_bool_kwarg(arg.ignore_index, "ignore_index")
        )
        if arg.keep in supported_keep:
            subset = irutils.make_tuple_of_column_names([])  # NA for Series
            arg.keep = "none" if arg.keep is False else arg.keep
            keep_org_index_when_no_dup = False  # as per pandas 1.5.3, 2.2.2
            value = ir.drop_duplicates(
                self._value,
                subset,
                arg.keep,
                ignore_index,
                keep_org_index_when_no_dup,
            )
            return self._create_or_inplace(value, arg.inplace)

        return self._fallback_may_inplace(
            "drop_duplicates",
            args,
            kwargs,
            pos=2,
            reason="unsupported argument",
        )

    def dropna(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.dropna)
        axis = self._get_axis_number(arg.axis)  # raises error for invalid axis
        axis = irutils.make_scalar(axis)
        subset = irutils.make_tuple_of_column_names([])  # not applicable
        # ignore_index is introduced in pandas-2
        ignore_index = (
            validate_bool_kwarg(arg.ignore_index, "ignore_index")
            if hasattr(arg, "ignore_index")
            else False
        )
        value = ir.dropna(self._value, subset, axis, ignore_index, True, 0)
        return self._create_or_inplace(value, arg.inplace)

    def duplicated(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.duplicated)

        supported_keep = {"first", "last", False}
        if arg.keep in supported_keep:
            subset = irutils.make_tuple_of_column_names([])  # NA for Series
            arg.keep = "none" if arg.keep is False else arg.keep
            return Series._create(ir.duplicated(self._value, subset, arg.keep))

        return self._fallback_call(
            "duplicated",
            args=[arg.keep],
            reason=f"unsupported keep = {arg.keep}",
        )

    def _get_dtypes(self):
        if fireducks.core.get_ir_prop().has_metadata:
            dtypes, unsupported = self._get_metadata()._get_dtypes(self)
            if len(unsupported) == 0:
                assert len(dtypes) == 1
                return dtypes.iloc[0], None
            reason = "Series.dtype is unsupported type: " + ",".join(
                unsupported
            )
        else:
            reason = "IR does not support metadata"
        return None, reason

    @property
    def dtype(self):
        if self._fireducks_meta.is_cached("pandas_object"):
            return self._fireducks_meta.get_cache("pandas_object").dtypes

        if self._fireducks_meta.is_cached("dtypes"):
            return self._fireducks_meta.get_cache("dtypes")

        dt, reason = self._get_dtypes()
        if reason is None:
            self._fireducks_meta.set_cache("dtypes", dt)
            return dt

        # No need to cache 'dtypes' when fallback occurs,
        # since fallback caches the 'pandas_object' itself
        return utils.fallback_attr(self._unwrap, "dtypes", reason=reason)

    dtypes = dtype

    def explode(self, ignore_index=False):
        column = irutils.make_tuple_of_column_names([])  # NA for Series
        # according to pandas behavior. all true values would be treated
        # as true. e.g., ignore_index="a" would be treated as ignore_index=True
        ignore_index = bool(ignore_index)
        return Series._create(ir.explode(self._value, column, ignore_index))

    def groupby(self, by=None, *args, **kwargs):
        logger.debug("series.groupby: type(by)=%s", type(by))
        from fireducks.pandas.groupby import SeriesGroupBy

        return SeriesGroupBy(self, by=by, *args, **kwargs)

    # for output formatting, it relies on pandas itself
    def info(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.info)
        # mostly copied from pandas Series.info() implementation
        return SeriesInfo(
            data=self,
            memory_usage=arg.memory_usage,
        ).render(
            buf=arg.buf,
            max_cols=arg.max_cols,
            verbose=arg.verbose,
            show_counts=arg.show_counts,
        )

    def isin(self, values):
        values_orig = values
        if isinstance(values, np.ndarray) and values.ndim == 1:
            values = list(values)

        if irutils.check_uniform_typed_list_or_tuple(values):
            first_target = values[0] if len(values) > 0 else None
            # TODO: use irable_scalar
            if first_target is None or isinstance(
                first_target,
                (
                    str,
                    int,
                    np.int32,
                    np.int64,
                    float,
                    np.float32,
                    np.float64,
                    date,
                    time,
                    np.datetime64,
                    pandas.Timestamp,
                    pandas.Timedelta,
                ),
            ):
                values = irutils.make_tuple_of_scalars(values)
                return Series._create(ir.isin(self._value, values))
        if isinstance(values, pandas.Index):
            values = Series(values)
        if isinstance(values, Series):
            return Series._create(ir.isin_vector(self._value, values._value))
        reason = f"Unsupported `values` of type: {type(values_orig).__name__}"
        if hasattr(values_orig, "dtype"):
            reason = reason + f" (dtype={values_orig.dtype})"
        return self._fallback_call("isin", args=[values_orig], reason=reason)

    def isna(self):
        return Series._create(ir.isnull(self._value))

    def isnull(self):
        return Series._create(ir.isnull(self._value))

    def _map(self, arg, na_action=None, map_as_take=False):
        if isinstance(arg, dict):
            arg = Series(arg.values(), index=arg.keys())

        if isinstance(arg, Series):
            return Series._create(
                ir.column_dict_map(self._value, arg._value, map_as_take)
            )

        if isinstance(arg, type) and arg in (str, int, float):
            return self.astype(arg)

        if callable(arg) and hasattr(arg, "__module__"):
            if (
                arg.__module__ == "pandas.core.tools.datetimes"
                and arg.__name__ == "to_datetime"
            ):
                return self.astype("datetime64[ns]")

        reason = "input 'arg' is neither a dict nor a type to be casted"
        return self._fallback_call("map", args=[arg, na_action], reason=reason)

    def map(self, arg, na_action=None):
        return self._map(arg, na_action)

    def memory_usage(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.memory_usage)
        return _Scalar(
            ir.get_column_memory_usage(self._value, arg.deep, arg.index)
        )._unwrap()

    def notna(self):
        return ~self.isnull()

    def notnull(self):
        return ~self.isnull()

    # To unwrap `index` which might be in kwargs, _fallback_may_inplace has to
    # be called explicitly here.
    def rename(self, index=None, **kwargs):
        reason = "Series.rename is fallback"
        return self._fallback_may_inplace(
            "rename", (index,), kwargs, reason=reason
        )

    def repeat(self, repeats, axis=None):
        if axis is not None:
            reason = "axis is not None"
            return self._fallback_call(
                "repeat", args=[repeats], kwargs={"axis": axis}, reason=reason
            )
        if irutils._is_scalar_or_list_or_tuple_of(
            repeats, int
        ) or irutils._is_scalar_or_list_or_tuple_of(repeats, float):
            repeats = irutils.make_tuple_of_scalars(repeats)
            return Series._create(ir.repeat(self._value, repeats))
        if isinstance(repeats, Series):
            return Series._create(
                ir.repeat_vector(self._value, repeats._value)
            )
        return self._fallback_call("repeat", [repeats])

    def reset_index(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.reset_index)
        arg.inplace = validate_bool_kwarg(arg.inplace, "inplace")
        arg.drop = validate_bool_kwarg(arg.drop, "drop")
        if arg.allow_duplicates is pandas_extensions.no_default:
            arg.allow_duplicates = False
        else:
            arg.allow_duplicates = validate_bool_kwarg(
                arg.allow_duplicates, "allow_duplicates"
            )

        to_rename = False
        reason = arg.is_not_default(["name"])
        if reason and irutils.is_column_name(arg.name):
            to_rename = True
            reason = None

        reason = reason or arg.is_not_default(["level"])
        if reason:
            return self._fallback_may_inplace(
                "reset_index", args, kwargs, pos=3, reason=reason
            )

        if arg.drop:
            value = ir.reset_index(
                self._value, arg.allow_duplicates, arg.drop, True
            )
            return self._create_or_inplace(value, arg.inplace)
        else:  # DataFrame to be created
            if arg.inplace:
                raise TypeError(
                    "Cannot reset_index inplace on a Series "
                    + "to create a DataFrame"
                )
            if to_rename:
                new_name = irutils.make_tuple_of_column_names([arg.name])
                target = ir.rename(self._value, new_name)
            else:
                target = self._value
            return fireducks_pandas.DataFrame._create(
                ir.reset_index(target, arg.allow_duplicates, arg.drop, True)
            )

    def rolling(self, *args, **kwargs):
        from fireducks.pandas.rolling import Rolling

        ns = utils.decode_args(args, kwargs, pandas.Series.rolling)
        reason = ns.is_not_default(["win_type"])
        if reason:
            return self._fallback_call("rolling", args, kwargs, reason=reason)
        return Rolling(self, args, kwargs)

    def round(self, decimals=0, *args, **kwargs):
        nv.validate_round(args, kwargs)

        if is_integer(decimals):
            return Series._create(ir.round(self._value, int(decimals)))

        reason = (
            "unsupported type for 'decimals' "
            f"parameter: {type(decimals).__name__}"
        )
        return self._fallback_call(
            "round", [decimals, *args], kwargs, reason=reason
        )

    @property
    def name(self):
        """The name of the Series column"""
        logger.debug("Series.name")
        # To prevent fallback, cache is explicitly checked here
        if self._fireducks_meta.is_cached("pandas_object"):
            return self._fireducks_meta.get_cache("pandas_object").name
        else:
            if fireducks.core.get_ir_prop().has_metadata:
                return self._get_metadata().column_names[0]
            return utils.fallback_attr(
                self._unwrap,
                "name",
                reason=f"Series.name",
            )

    @name.setter
    def name(self, value):
        logger.debug("Series.name: type=%s", type(value))
        if not irutils.irable_scalar(value):
            return self._fallback_mutating_method(
                "__setattr__",
                args=["name", value],
                reason="series_name_setter: input is not an irable-scalar",
            )
        new_name = irutils.make_tuple_of_column_names([value])
        self._rebind(ir.rename(self._value, new_name), invalidate_cache=True)
        return self

    @property
    def nbytes(self) -> int:
        return self.memory_usage(index=False, deep=False)

    @property
    def ndim(self) -> int:
        return 1

    @property
    def shape(self) -> Tuple[int, ...]:
        if (
            fireducks.core.get_fireducks_options().fast_fallback
            and self._fireducks_meta.is_cached("pandas_object")
        ):
            obj = self._fireducks_meta.get_cache("pandas_object")
            return obj.shape

        return (self._get_shape()[0],)

    @property
    def size(self) -> int:
        return self.shape[0]

    def value_counts(
        self,
        normalize=False,
        sort=True,
        ascending=False,
        bins=None,
        dropna=True,
    ):
        if bins is None:
            # according to pandas behavior. all true values would be treated
            # as true. e.g., sort=2 would be treated as sort=True
            normalize, sort, ascending, dropna = [
                bool(f) for f in (normalize, sort, ascending, dropna)
            ]
            return Series._create(
                ir.value_counts(
                    self._value, sort, ascending, dropna, normalize, True
                )
            )

        reason = "bins is not None"
        return self._fallback_call(
            "value_counts",
            args=[normalize, sort, ascending, bins, dropna],
            reason=reason,
        )

    def quantile(self, *args, **kwargs):
        reason = None
        arg = utils.decode_args(args, kwargs, pandas.Series.quantile)

        # arrow implementation of nearest seems not to
        # return same value as in pandas
        supported_interpolation = {
            "linear",
            "lower",
            "higher",
            "midpoint",
            # "nearest",
        }
        if arg.interpolation not in supported_interpolation:
            reason = f"unsupported 'interpolation' = {arg.interpolation}"

        if reason:
            return self._fallback_call("quantile", args, kwargs, reason=reason)

        is_scalar = irutils.irable_scalar(arg.q)
        if is_scalar:
            arg.q = float(arg.q)
            return _Scalar(
                ir.quantile_scalar(self._value, arg.q, arg.interpolation)
            )._unwrap()
        else:
            arg.q = [float(e) for e in arg.q]
            qs = irutils.make_vector_or_scalar_of_scalar(arg.q)
            return Series._create(
                ir.quantile(self._value, qs, arg.interpolation)
            )

    def set_axis(self, *args, **kwargs):
        return self._set_axis(*args, **kwargs)

    def _set_axis(self, *args, _inplace_index_setter=False, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.set_axis)

        class_name = "Series"
        reason, result = self._fallback_set_axis(
            args, kwargs, arg, class_name, _inplace_index_setter
        )
        if reason:
            return result

        label_names = []
        labels = arg.labels
        keys = irutils.make_tuple_of_scalars([])
        if isinstance(labels, MultiIndex):
            # keeping original names to be used at backend
            label_names = list(labels.names)
            ncol = len(label_names)
            is_with_dup_names = ncol != len(set(labels.names))
            if is_with_dup_names:
                # cudf backend doesn't support duplicate names
                newIndexColumns = labels.to_frame(
                    index=False, name=range(ncol)
                )
            else:
                newIndexColumns = labels.to_frame(index=False)
        else:
            newIndexColumns = Series(labels)
        # TODO: fallback if 'newIndexColumns' have mixed types
        newIndexColumnNames = irutils.make_tuple_of_column_names(label_names)

        # the following boolean parameters are ordered alphabetically as
        # per the .td requirement.  Hence, be careful when changing the
        # order of:  as_axis, as_new, drop, to_append, verify_integrity
        value = ir.set_index(
            self._value,
            keys,
            newIndexColumns._value,
            newIndexColumnNames,
            as_axis=True,
            as_new=True,
            drop=True,
            to_append=False,
            verify_integrity=False,
        )
        inplace = (
            arg.inplace or _inplace_index_setter
            if utils._pd_version_under2
            else _inplace_index_setter
        )
        return self._create_or_inplace(value, inplace)

    @deprecate_nonkeyword_arguments(version=None, allowed_args=["self"])
    def sort_values(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.sort_values)
        arg.ascending = validate_ascending(arg.ascending)
        return self._sort_values(
            args,
            kwargs,
            decoded_args=arg,
            by=[],
            ascending=[arg.ascending],
            is_series=True,
        )

    def sort_index(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.Series.sort_index)
        arg.ascending = validate_ascending(arg.ascending)
        return self._sort_index(
            args,
            kwargs,
            decoded_args=arg,
            is_series=True,
        )

    def unique(self):
        value = ir.unique(self._value)
        return fireducks.core.evaluate([value])[0]

    def to_frame(self, *args, **kwargs):
        ns = utils.decode_args(args, kwargs, pandas.Series.to_frame)
        reason = ns.is_not_default(["name"])
        to_rename = reason is not None
        cname = ns.name if to_rename else ""
        return fireducks_pandas.DataFrame._create(
            ir.to_frame(
                self._value, irutils.make_column_name(cname), to_rename
            )
        )

    def to_numpy(self, *args, **kwargs):
        if self._fireducks_meta.is_cached("pandas_object"):
            return self._fireducks_meta.get_cache("pandas_object").to_numpy(
                *args, **kwargs
            )

        if self._fireducks_meta.is_cached("values"):
            return self._fireducks_meta.get_cache("values")

        ns = utils.decode_args(args, kwargs, pandas.Series.to_numpy)
        reason = ns.is_not_default(
            [
                "dtype",
                "na_value",
                # Because ns.copy=False does not ensure no copy in pandas and
                # fireducks always copies, ns.copy can be ignored.
            ]
        )
        if reason is not None:
            return self._fallback_call("to_numpy", args, kwargs, reason=reason)

        value = ir.to_numpy(self._value)
        ret = fireducks.core.evaluate([value])[0]
        self._fireducks_meta.set_cache("values", ret)
        return ret

    def __array__(self, *args, **kwargs):
        ns = utils.decode_args(args, kwargs, pandas.Series.__array__)

        reason = ns.is_not_default(["dtype"])
        if reason is not None:
            return self._fallback_call(
                "__array__", args, kwargs, reason=reason
            )
        return self.to_numpy()

    @property
    def values(self):
        """Return a Numpy representation of the Series."""
        logger.debug("Series.values")
        if self._fireducks_meta.is_cached("pandas_object"):
            return utils._wrap(
                self._fireducks_meta.get_cache("pandas_object").values
            )

        if self._fireducks_meta.is_cached("values"):
            return self._fireducks_meta.get_cache("values")

        if fireducks.core.get_ir_prop().has_metadata:
            target_types = [
                "int8",
                "int16",
                "int32",
                "int64",
                "uint8",
                "uint16",
                "uint32",
                "uint64",
                "float16",
                "float32",
                "float64",
                "bool",
                "utf8",
                "timestamp",
                "duration[s]",
                "duration[ms]",
                "duration[us]",
                "duration[ns]",
            ]

            # for non-numeric cases (like categorical etc.), pandas output
            # might differ for to_numpy() and values
            col_dtypes = self._get_metadata()._get_raw_dtypes()
            assert len(col_dtypes) == 1
            if col_dtypes[0] in target_types:
                value = ir.to_numpy(self._value)
                ret = fireducks.core.evaluate([value])[0]
                self._fireducks_meta.set_cache("values", ret)
                return ret

        return utils.fallback_attr(
            self._unwrap,
            "values",
            reason="Series.values with non-numeric column",
        )
