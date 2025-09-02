# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import pandas
from fireducks.pandas.utils import (
    PandasClassWrapper,
    _fireducks_class,
    _pd_version_under2,
    _unwrap,
    decode_args,
)

from fireducks import irutils
import logging

logger = logging.getLogger(__name__)


class Categorical(PandasClassWrapper):
    _pandas_cls = pandas.core.arrays.categorical.Categorical


class Index(PandasClassWrapper):
    _pandas_cls = pandas.core.indexes.base.Index

    def __new__(cls, *args, _pandas_obj=None, **kwargs):
        if _pandas_obj is None:
            _pandas_obj = cls._pandas_cls(*_unwrap(args), **_unwrap(kwargs))
            cls = _fireducks_class(type(_pandas_obj))
        self = object.__new__(cls)
        PandasClassWrapper.__init__(self, _pandas_obj=_pandas_obj)
        return self

    def __init__(self, *args, _pandas_obj=None, name=None, **kwargs):
        object.__setattr__(self, "_fireducks_frame", None)

    def __setattr__(self, name, value):
        if name in ("name", "names"):
            setattr(self._pandas_obj, name, value)
            return self._set_backend_attr(name, value)
        super().__setattr__(name, value)

    def _set_fireducks_frame(self, fireducks_frame, target):
        object.__setattr__(self, "_fireducks_frame", fireducks_frame)
        object.__setattr__(self, "_fireducks_columns_or_index", target)

    def _set_backend_attr(self, name, value, fallback_reason=None):
        if self._fireducks_frame is None:  # no backend data is set
            return

        logger.debug(
            "Detected %s.%s update: %s",
            self._fireducks_columns_or_index,
            name,
            value,
        )
        if name not in ("name", "names"):
            raise AttributeError(
                f"Unknown attribute '{self._pandas_cls.__name__}.{name}' at backend"
            )

        value = value if name == "names" else [value]
        to_fallback = fallback_reason or not all(
            [irutils.irable_scalar(x) for x in value]
        )
        if to_fallback:
            if not fallback_reason:
                attr = f"{self._fireducks_columns_or_index}.{name}"
                fallback_reason = f" {attr} = unsupported input"
            name_, value_ = (
                self._fireducks_columns_or_index,
                self._pandas_obj,
            )
            return self._fireducks_frame._fallback_mutating_method(
                "__setattr__",
                args=[name_, value_],
                reason=fallback_reason,
            )
        if self._fireducks_columns_or_index == "columns":
            if not isinstance(self, MultiIndex):
                value = value[0]
            # If MultiIndex the tuple must be treated as a list.
            if isinstance(self, MultiIndex) and isinstance(value, tuple):
                value = list(value)
            return self._fireducks_frame._set_column_index_names(value)
        else:
            return self._fireducks_frame._set_index_names(value)

    def set_names(self, *args, **kwargs):
        arg = decode_args(args, kwargs, self._pandas_cls.set_names)
        ret = self._pandas_obj.set_names(*args, **kwargs)
        if arg.inplace:
            reason = "level is not None" if arg.level is not None else None
            # setting names for backend side frame index or columns
            self._set_backend_attr("names", arg.names, fallback_reason=reason)
        return ret


class CategoricalIndex(Index):
    _pandas_cls = pandas.core.indexes.category.CategoricalIndex


class DatetimeIndex(Index):
    _pandas_cls = pandas.core.indexes.datetimes.DatetimeIndex


class IntervalIndex(Index):
    _pandas_cls = pandas.core.indexes.interval.IntervalIndex


class MultiIndex(Index):
    _pandas_cls = pandas.core.indexes.multi.MultiIndex


if _pd_version_under2:
    # pandas does not have NumericIndex class since v2.0.

    class NumericIndex(Index):
        _pandas_cls = pandas.core.indexes.numeric.NumericIndex

    class Int64Index(Index):
        _pandas_cls = pandas.core.indexes.numeric.Int64Index

    class UInt64Index(Index):
        _pandas_cls = pandas.core.indexes.numeric.UInt64Index

    class Float64Index(Index):
        _pandas_cls = pandas.core.indexes.numeric.Float64Index


class PeriodIndex(Index):
    _pandas_cls = pandas.core.indexes.period.PeriodIndex


class RangeIndex(Index):
    _pandas_cls = pandas.core.indexes.range.RangeIndex


class TimedeltaIndex(Index):
    _pandas_cls = pandas.core.indexes.timedeltas.TimedeltaIndex
