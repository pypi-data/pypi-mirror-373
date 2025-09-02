# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from abc import abstractmethod
import pandas
from fireducks import ir, irutils
from fireducks.pandas import utils, DataFrame, Series


# https://pandas.pydata.org/docs/reference/window.html
_known_funcs = ["count", "sum", "mean", "median", "var", "std", "min", "max"]


def is_supported_function(func):
    return func in _known_funcs


class Rolling:
    def __init__(self, obj, args, kwargs):
        self._obj = obj
        self._rolling_args = args
        self._rolling_kwargs = kwargs

    def _unwrap(self, reason=None):
        return self._obj._fallback_call(
            "rolling", self._rolling_args, self._rolling_kwargs, reason=reason
        )

    def __str__(self):
        return utils.fallback_call(self._unwrap, "__str__")

    def __repr__(self):
        return utils.fallback_call(self._unwrap, "__repr__")

    def __getattr__(self, name):
        reason = f"{type(self).__name__}.__getattr__ for {name} is called"
        return utils.fallback_attr(self._unwrap, name, reason)

    def _fallback_call(self, method, args, kwargs, *, reason=None):
        return utils.fallback_call(
            self._unwrap, method, args, kwargs, reason=reason
        )

    def aggregate(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self._obj.__class__)
        ns = utils.decode_args(
            args, kwargs, pandas.core.window.rolling.Rolling.aggregate
        )

        rolling_ns = utils.decode_args(
            self._rolling_args, self._rolling_kwargs, pandas_cls.rolling
        )

        funcs = ns.func
        if not isinstance(rolling_ns.window, int):
            reason = "window is not int"
        else:
            reason = rolling_ns.is_not_default(
                [
                    "center",
                    "win_type",
                    "on",
                    "axis",
                    "closed",
                    "step",
                    "method",
                ]
            )

        if isinstance(funcs, str):
            if not is_supported_function(funcs):
                reason = f"unsupported function: '{funcs}'"
        elif isinstance(funcs, (list, tuple)):
            if len(funcs) == 0:
                raise ValueError("no results")
            reason = "list of function is not supported"
        else:
            reason = f"unsupported func of type: {type(funcs).__name__}"

        if not reason:
            if rolling_ns.min_periods is None:
                if isinstance(rolling_ns.window, int):
                    if utils._pd_version_under2:
                        rolling_ns.min_periods = (
                            0 if funcs == "count" else rolling_ns.window
                        )
                    else:
                        rolling_ns.min_periods = rolling_ns.window
                else:
                    reason = (
                        "unsupported min_periods=None with "
                        f"window of type: '{type(rolling_ns.window)}'"
                    )
            elif isinstance(rolling_ns.min_periods, int):
                if rolling_ns.min_periods > rolling_ns.window:
                    raise ValueError(
                        f"min_periods {rolling_ns.min_periods} must be"
                        f"<= window {rolling_ns.window}"
                    )
            else:
                reason = f"unsupported min_periods: '{rolling_ns.min_periods}'"

        if reason:
            return self._fallback_call(
                "aggregate", args, kwargs, reason=reason
            )

        window = rolling_ns.window
        funcs = irutils.make_vector_or_scalar_of_str(funcs)
        return self._obj.__class__._create(
            ir.rolling_aggregate(
                self._obj._value, window, rolling_ns.min_periods, funcs
            )
        )

    agg = aggregate

    def __getitem__(self, key):
        projected = self._obj.__getitem__(key)
        return Rolling(projected, self._rolling_args, self._rolling_kwargs)

    def count(self):
        return self.aggregate("count")

    def sum(self):
        return self.aggregate("sum")

    def mean(self):
        return self.aggregate("mean")

    def median(self):
        return self.aggregate("median")

    def min(self):
        return self.aggregate("min")

    def max(self):
        return self.aggregate("max")

    def var(self):
        return self.aggregate("var")

    def std(self):
        return self.aggregate("std")
