# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import logging
import warnings

import numpy as np
import pandas

from pandas.core.common import get_cython_func
from pandas.core.groupby.base import (
    # groupby_other_methods,
    # dataframe_apply_allowlist,
    reduction_kernels,
    transform_kernel_allowlist,
)
from pandas.core.util.numba_ import maybe_use_numba
from pandas.util._validators import validate_bool_kwarg

from fireducks import ir, irutils
from fireducks.irutils import (
    _is_str_list,
    irable_scalar,
    is_column_name,
    make_column_name,
    make_vector_or_scalar_of_str,
    make_tuple_of_vector_or_scalar_of_str,
    make_tuple_of_column_names,
)
import fireducks.pandas.utils as utils

from fireducks.pandas.aggregate import (
    infer_agg_method_name,
    make_agg_args,
)
from fireducks.pandas import (
    DataFrame,
    Series,
)

logger = logging.getLogger(__name__)

if utils._pd_version_under2:
    from pandas.core.groupby.base import series_apply_allowlist
else:
    # pandas doesn't have series_apply_allowlist since v2.2.0.
    series_apply_allowlist = frozenset(
        {
            "is_monotonic_decreasing",
            "diff",
            "is_monotonic_increasing",
            "nsmallest",
            "fillna",
            # "mad", # not in v2.2.0
            "hist",
            "cov",
            "plot",
            "skew",
            "nlargest",
            "quantile",
            # "tshift", # not in v2.2.0
            "idxmax",
            "dtype",
            "corr",
            "take",
            "unique",
            "idxmin",
        }
    )


def _install_agg(cls, method, parent=None):
    """Define a method as a wrapper to call agg."""

    # do not override
    if hasattr(cls, method):
        return

    def wrapper(self, *args, **kwargs):
        # TODO: Why not fallback in agg?
        if args or kwargs:
            return self._fallback_call(
                method,
                args=args,
                kwargs=kwargs,
                reason="args and kwargs are not supported",
            )
        return self.agg(method)

    utils.install_wrapper(cls, method, wrapper, parent)


def preprocess_groupby_target(target, by):
    # by must be a column-name-like object, a Series,
    # Or a list of column-name-like object and Series
    assert is_supported_group_keys(by)

    if isinstance(by, Series):
        new_key = utils.get_unique_column_name(target.columns)
        target = target.copy()
        target[new_key] = by
        added_cols = [new_key]
        return target, new_key, added_cols

    elif isinstance(by, list):
        new_key = []
        added_cols = []
        for idx, key in enumerate(by):
            if isinstance(key, Series):
                tmp_key = utils.get_unique_column_name(target.columns)
                if len(added_cols) == 0:
                    # create a copy on the first encounter of a Series as key
                    target = target.copy()
                target[tmp_key] = key
                new_key.append(tmp_key)
                added_cols.append(tmp_key)
            else:
                new_key.append(key)
        return target, new_key, added_cols

    return target, by, []


def process_agg_output(out, added_cols, as_index, self_by):
    if added_cols:
        # self_by must be a Series, Or a list of <column-name-like object and Series>
        if as_index:
            if isinstance(self_by, Series):
                names = self_by.name
            else:
                names = [
                    k.name if isinstance(k, Series) else k for k in self_by
                ]
            out._set_index_names(names)
        else:
            # key of type Series should not be included in the final output,
            # when as_index = False
            warnings.warn(
                "A grouping was used that is not in the columns of the"
                " DataFrame and so was excluded from the result. This"
                " grouping will be included in a future version of pandas."
                " Add the grouping as a column of the DataFrame to"
                " silence this warning.",
                FutureWarning,
            )
            out = out.drop(columns=added_cols)
    return out


def is_supported_group_keys(keys):
    if isinstance(keys, Series):
        return True

    if isinstance(keys, list):
        return all([isinstance(x, Series) or is_column_name(x) for x in keys])

    return is_column_name(keys)


def is_supported_selection(selection):
    def is_selection_supported_type(obj):
        return isinstance(obj, (int, float, str, bytes))

    if selection is None:
        return True
    if isinstance(selection, (list, tuple)) and all(
        [is_selection_supported_type(x) for x in selection]
    ):
        return True
    if is_selection_supported_type(selection):
        return True

    return False


def make_groupkey_ops(by):
    if not isinstance(by, list):
        by = [by]
    return make_tuple_of_column_names(by)


def make_selection_ops(selection):
    if isinstance(selection, list):
        cols = [make_column_name(col) for col in selection]
        selection = ir.make_vector_or_scalar_of_column_name_from_vector(cols)
    else:
        selection = make_column_name(selection)
        selection = ir.make_vector_or_scalar_of_column_name_from_scalar(
            selection
        )
    return selection


def find_unsupported_agg_funcs(funcs):
    supported_hash_funcs = {
        "first",
        "last",
        "sum",
        "mean",
        "median",
        "std",
        "var",
        "max",
        "min",
        "count",
        "size",
        "nunique",
        "list",
        "any",
        "all",
        "quantile",
        "skew",
        "kurt",
        "prod",
    }  # yapf: disable

    def is_unsupported(f):
        return not isinstance(f, str) or f not in supported_hash_funcs

    flat = np.asarray(
        sum([f if isinstance(f, list) else [f] for f in funcs], [])
    )
    return flat[[is_unsupported(f) for f in flat]]


def _setup_FireDucksGroupBy(cls):
    utils.install_fallbacks(cls, ["__len__"])
    utils.install_fallbacks(cls, ["__dir__"], override=True)
    return cls


@_setup_FireDucksGroupBy
class FireDucksGroupBy:
    def __init__(
        self,
        obj,
        by=None,
        axis=0,
        level=None,
        as_index=True,
        sort=True,
        dropna=True,
        *groupby_args,
        selection=None,
        observed=True,
        **groupby_kwargs,
    ):
        self._obj = obj
        self._by = by
        self._as_index = as_index
        self._sort = sort
        self._dropna = dropna
        self._selection = selection

        # `observed` argument is always used as True, but is checked to return a ValueError.
        validate_bool_kwarg(observed, "observed")

        # Fallback if args has unsupported arguments.
        self._groupby_args = groupby_args
        self._groupby_kwargs = groupby_kwargs
        if axis != 0:
            self._groupby_kwargs["axis"] = axis
        if level is not None:
            self._groupby_kwargs["level"] = level

        self._unwrap_cache = None

    def _has_unsupported_groupby_args(self):
        if not is_supported_group_keys(self._by):
            return "unsupported group key"

        if not is_supported_selection(self._selection):
            return "unsupported selection"

        if self._groupby_args or self._groupby_kwargs:
            return "unsupported args or kwargs is used"

        return None

    def _is_supporeted_transoform_func(self, func):
        if not isinstance(func, str):
            return False

        return func in [
            "mean",
            "max",
            "min",
            "sum",
            "prod",
            "count",
            "std",
            "var",
            "nunique",
        ]

    def _unwrap(self, reason=None):
        if self._unwrap_cache is not None:
            return self._unwrap_cache

        logger.debug("%s._unwrap", type(self).__name__)
        kwargs = self._groupby_kwargs | {
            "by": self._by,
            "as_index": self._as_index,
            "sort": self._sort,
            "dropna": self._dropna,
            "observed": True,
        }
        grpby = self._obj._fallback_call(
            "groupby", args=self._groupby_args, kwargs=kwargs, reason=reason
        )
        if isinstance(grpby, utils.PandasWrapper):
            grpby = grpby._pandas_obj
        if self._selection is not None:
            return grpby[self._selection]
        self._unwrap_cache = grpby
        return grpby

    def _fallback_call(self, method, args=None, kwargs=None, *, reason=None):
        return utils.fallback_call(
            self._unwrap, method, args, kwargs, reason=reason
        )

    def __getattr__(self, name):
        logger.debug("SeriesGroupBy.__getattr__: name=%s", name)
        reason = f"{type(self).__name__}.__getattr__ for {name} is called"
        return utils.fallback_attr(self._unwrap, name, reason)

    def __iter__(self):
        return self._fallback_call(
            "__iter__",
            reason="DataFrameGroupby.__iter__ is not supported",
        )

    def aggregate(self, func=None, *args, **kwargs):
        """fireducks is implemented assuming numeric_only argument is
        'True'."""

        logger.debug("GroupBy.aggregate: %s", type(self))

        func_ = func
        reason = self._has_unsupported_groupby_args()

        if not reason:
            func = infer_agg_method_name(func)
            aggArgs = make_agg_args(func, *args, **kwargs)
            if aggArgs is None:
                reason = "unsupported aggregated args"

        if not reason:
            fn = func[0] if _is_str_list(func) and len(func) == 1 else func

            if isinstance(fn, str):
                # these methods returns more than 1 rows per group.
                # hence when any of them is specified as scalar value
                # to aggregate(), calling the respective member method.
                # Otherwise, when specified with any other aggregator
                # it will fallback to pandas.
                if fn in ("shift", "head", "tail", "rank"):
                    return getattr(self, fn)()

        if not reason:
            unsup_agg = find_unsupported_agg_funcs(aggArgs.funcs)
            if len(unsup_agg) > 0:
                reason = f"agg function is not supported {unsup_agg}"

            # To raise the same error as pandas, fallback is used when column
            # is not selected
            def is_selected(selection, col):
                if not isinstance(selection, list):
                    return selection == col
                return col in selection

            if self._selection is not None:
                for col in aggArgs.columns:
                    if not is_selected(self._selection, col):
                        reason = "column for aggregation is not selected"

        if reason:
            # fireducks: GT #807
            if func_ is DataFrame.sum:
                func_ = pandas.DataFrame.sum
            return self._fallback_call(
                "agg",
                args=(func_,) + args,
                kwargs=kwargs,
                reason=reason,
            )

        return self._aggregate(func, aggArgs)

    agg = aggregate

    def apply(self, func, *args, **kwargs):
        if callable(func):
            # Creat a wrapper of func to pass pandas's apply when fallback.
            #
            # If func accepts pandas, we can simply pass first argument, i.e.
            # pandas.DataFrame, to func and return result of func.
            #
            # If func accepts fireducks, we have to do _wrap and _unwrap.
            #
            # Here we assume that if func is from numpy it accepts pandas,
            # otherwise it accepts fireducks.

            # pandas.GroupBy.apply() replaces built-in max/min/sum with
            # numpy max/min/sum. Since this wrapper hides builtin funcs
            # from pandas, we replace those here.
            # See GT #675
            _builtin_table = {sum: np.sum, max: np.max, min: np.min}
            func = _builtin_table.get(func, func)

            if getattr(func, "__module__", None) == "numpy":

                def wrapper(df, *args_, **kwargs_):
                    # ignore numpy error as panadas.
                    with np.errstate(all="ignore"):
                        return func(df, *args_, **kwargs_)

            else:

                def wrapper(df, *args_, **kwargs_):
                    return utils._unwrap(
                        func(utils._wrap(df), *args_, **kwargs_),
                        reason="return value of user function passed to apply",
                    )

            return self._fallback_call(
                "apply",
                args=(wrapper,) + args,
                kwargs=kwargs,
                reason="DataFrameGroupby.apply is not supported",
            )
        return self._fallback_call(
            "apply",
            args=(func,) + args,
            kwargs=kwargs,
            reason="func is not callable",
        )

    def _evaluate(self):
        return self._unwrap()

    def transform(self, func, *args, engine=None, **kwargs):
        use_numba = maybe_use_numba(engine)
        if use_numba:
            # Incompatibility: 013
            warnings.warn("numba is not supported", UserWarning)

        # - Wrapper function cannot use numba.
        # - String function catnot wrap.
        # - If func is in the list of get_cython_func(),
        #   pandas.Groupby._transform() will call the internal function.
        if use_numba or not callable(func) or get_cython_func(func):
            wrapper = func
        else:

            def wrapper(df, *args_, **kwargs_):
                return utils._unwrap(
                    func(utils._wrap(df), *args_, **kwargs_),
                    reason="return value of user function passed to apply",
                )

        reason = "transform function is not supported"
        kwargs["engine"] = engine
        return self._fallback_call(
            "transform",
            args=(wrapper,) + args,
            kwargs=kwargs,
            reason=reason,
        )


def _setup_SeriesGroupBy(cls):
    pandas_class = pandas.core.groupby.generic.SeriesGroupBy

    # pandas.DataFrame has corrwith function, but pandas.Series doesn't have
    # corrwith function
    for m in reduction_kernels - set(["corrwith"]):
        _install_agg(cls, m, pandas_class)

    for m in series_apply_allowlist:
        _install_agg(cls, m, pandas_class)

    return cls


@_setup_SeriesGroupBy
class SeriesGroupBy(FireDucksGroupBy):
    """SeriesGroupBy is groupby which returns Series.

    There are two cases where SeriesGroupBy is created:
        1. groupby on Series: series.groupby()
        2. groupby and selection on DataFrame: df.groupby(key)[col]
    """

    def _aggregate(self, func, aggArgs):
        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )
        selection = make_selection_ops(self._selection)
        funcs, columns, relabels = aggArgs.to_ir()
        value = ir.groupby_select_agg(
            target._value,
            make_groupkey_ops(by_cols),
            funcs,
            columns,
            relabels,
            selection,
            self._as_index,
            self._dropna,
            self._sort,
        )

        cls = DataFrame
        if isinstance(func, str):
            cls = Series
        ret = cls._create(value)
        return process_agg_output(ret, added_cols, self._as_index, self._by)

    def aggregate(self, func=None, *args, **kwargs):
        logger.debug("SeriesGroupBy.aggregate: %s", type(self))

        reason = None
        if (
            self._selection is None
            or isinstance(self._selection, (tuple, list))
            or not is_supported_selection(self._selection)
        ):
            reason = "Series.groupby is not supported"

        if not reason:
            if isinstance(self._selection, str) and func is None and not args:
                # For SeriesGroupBy with kwargs case:
                # df.groupby("a")["b"].agg(Sum="sum", Max="max")
                # is to be converted as:
                # df.groupby("a").agg(Sum=("b", "sum"), Max=("b", "max"))
                new_kwargs = {}
                for k, v in kwargs.items():
                    if isinstance(v, str):
                        new_kwargs[k] = (self._selection, v)
                    else:
                        reason = "unsupported aggregated args"
                        break

                if not reason:
                    return DataFrameGroupBy(
                        self._obj,
                        *self._groupby_args,
                        by=self._by,
                        as_index=self._as_index,
                        sort=self._sort,
                        dropna=self._dropna,
                        **self._groupby_kwargs,
                    ).aggregate(func, *args, **new_kwargs)

        if reason:
            return self._fallback_call(
                "agg",
                args=(func,) + args,
                kwargs=kwargs,
                reason=reason,
            )

        return super().aggregate(func, *args, **kwargs)

    agg = aggregate

    @property
    def dtype(self):
        return self.__getattr__("dtype")

    @property
    def is_monotonic_decreasing(self):
        return self.__getattr__("is_monotonic_decreasing")

    @property
    def is_monotonic_increasing(self):
        return self.__getattr__("is_monotonic_increasing")

    def transform(self, func, *args, **kwargs):
        if (
            self._has_unsupported_groupby_args() is not None
            or isinstance(self._by, Series)
            or (
                isinstance(self._by, list)
                and any([isinstance(k, Series) for k in self._by])
            )
            or not self._as_index
            or args
            or kwargs
            or not self._is_supporeted_transoform_func(func)
        ):
            return super().transform(func, *args, **kwargs)

        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )

        if self._selection is None:
            value = ir.groupby_transform(
                target._value,
                make_groupkey_ops(by_cols),
                make_tuple_of_vector_or_scalar_of_str([func]),
                make_tuple_of_column_names([]),
                make_tuple_of_column_names([]),
            )
        elif isinstance(self._selection, str):
            selection = make_selection_ops(self._selection)
            value = ir.groupby_select_transform(
                target._value,
                make_groupkey_ops(by_cols),
                make_tuple_of_vector_or_scalar_of_str([func]),
                make_tuple_of_column_names([]),
                make_tuple_of_column_names([]),
                selection,
            )

        ret = Series._create(value)
        return process_agg_output(ret, added_cols, self._as_index, self._by)

    def _head_or_tail(self, is_head, n=5):
        reason = []
        if (
            self._selection is None
            or isinstance(self._selection, (tuple, list))
            or not is_supported_selection(self._selection)
        ):
            reason.append("Series.groupby is not supported")

        reason_args = self._has_unsupported_groupby_args()
        if reason_args is not None:
            reason.append(reason_args)

        if not isinstance(n, int):
            reason.append(f"unsupported 'n' = {n} of type: {type(n).__name__}")

        if len(reason) > 0:
            func = "head" if is_head else "tail"
            return self._fallback_call(
                func, args=[n], reason="; ".join(reason)
            )

        with_selector = True
        selection = make_selection_ops(self._selection)
        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )
        value = ir.groupby_head_or_tail(
            target._value,
            make_groupkey_ops(by_cols),
            selection,
            with_selector,
            n,
            self._dropna,
            is_head,
        )
        return Series._create(value)

    def head(self, n=5):
        logger.debug("SeriesGroupBy.head: %s", type(self))
        return self._head_or_tail(True, n=n)

    def tail(self, n=5):
        logger.debug("SeriesGroupBy.tail: %s", type(self))
        return self._head_or_tail(False, n=n)

    def rank(self, *args, **kwargs):
        arg = utils.decode_args(
            args, kwargs, pandas.core.groupby.SeriesGroupBy.rank
        )
        reason = []

        reason_no_default = arg.is_not_default(["pct"])
        if reason_no_default is not None:
            reason.append(reason_no_default)

        if (
            self._selection is None
            or isinstance(self._selection, (tuple, list))
            or not is_supported_selection(self._selection)
        ):
            reason.append("Series.groupby is not supported")

        reason_args = self._has_unsupported_groupby_args()
        if reason_args is not None:
            reason.append(reason_args)

        if arg.method not in ("first", "dense", "average", "max", "min"):
            reason.append(f"unsupported method='{arg.method}'")

        if arg.na_option not in ("keep", "top", "bottom"):
            reason.append(f"unsupported na_option='{arg.na_option}'")

        if len(reason) > 0:
            return self._fallback_call(
                "rank", args, kwargs, reason="; ".join(reason)
            )

        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )
        value = ir.groupby_select_rank(
            target._value,
            make_groupkey_ops(by_cols),
            make_selection_ops(self._selection),
            arg.method,
            arg.na_option,
            bool(arg.ascending),
            self._dropna,
        )
        return Series._create(value)

    def shift(self, *args, **kwargs):
        arg = utils.decode_args(
            args, kwargs, pandas.core.groupby.SeriesGroupBy.shift
        )
        reason = []

        reason_no_default = arg.is_not_default(["freq", "axis", "fill_value"])
        if reason_no_default is not None:
            reason.append(reason_no_default)

        if (
            self._selection is None
            or isinstance(self._selection, (tuple, list))
            or not is_supported_selection(self._selection)
        ):
            reason.append("Series.groupby is not supported")

        reason_args = self._has_unsupported_groupby_args()
        if reason_args is not None:
            reason.append(reason_args)

        if not isinstance(arg.periods, int):
            reason.append(
                f"unsupported 'periods' = {arg.periods} "
                f"of type: {type(arg.periods).__name__}"
            )

        if len(reason) > 0:
            return self._fallback_call(
                "shift", args, kwargs, reason="; ".join(reason)
            )

        with_selector = True
        selection = make_selection_ops(self._selection)
        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )
        value = ir.groupby_shift(
            target._value,
            make_groupkey_ops(by_cols),
            selection,
            with_selector,
            arg.periods,
            self._dropna,
        )
        return Series._create(value)


def _setup_DataFrameGroupBy(cls):
    pandas_cls = pandas.core.groupby.generic.DataFrameGroupBy

    # FIXME: use groupby_other_methods
    other_methods = [
        # non-aggregation methods
        "corr",
        "cov",
        "hist",
        "plot",
        "take",
    ]
    utils.install_fallbacks(cls, other_methods, pandas_cls)

    # Exclude 'nth' because it is a callable property, not a method.
    for m in transform_kernel_allowlist - {"nth"}:
        _install_agg(cls, m, pandas_cls)
    return cls


@_setup_DataFrameGroupBy
class DataFrameGroupBy(FireDucksGroupBy):
    def __getattr__(self, name):
        logger.debug("DataFrameGroupBy.__getattr__: name=%s", name)

        # Check if `name` should be a column name. See DataFrame.__getattr__
        # for details.
        from pandas.core.groupby.generic import (
            DataFrameGroupBy as PandasDataFrameGroupBy,
        )

        if name not in PandasDataFrameGroupBy.__dict__:
            if self._obj._is_column_name(name):
                return self[name]

        reason = f"{type(self).__name__}.__getattr__ for {name} is called"
        return utils.fallback_attr(self._unwrap, name, reason)

    def __getitem__(self, key):
        if self._selection:
            raise IndexError(f"Column(s) {self._selection} already selected")
        if not isinstance(key, list) and self._as_index:
            return SeriesGroupBy(
                self._obj,
                *self._groupby_args,
                by=self._by,
                as_index=self._as_index,
                sort=self._sort,
                dropna=self._dropna,
                selection=key,
                **self._groupby_kwargs,
            )
        else:
            return DataFrameGroupBy(
                self._obj,
                *self._groupby_args,
                by=self._by,
                as_index=self._as_index,
                sort=self._sort,
                dropna=self._dropna,
                selection=key,
                **self._groupby_kwargs,
            )

    def _aggregate(self, func, aggArgs):
        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )
        if self._selection is None:
            funcs, columns, relabels = aggArgs.to_ir()
            value = ir.groupby_agg(
                target._value,
                make_groupkey_ops(by_cols),
                funcs,
                columns,
                relabels,
                self._as_index,
                self._dropna,
                self._sort,
            )
        else:
            funcs, columns, relabels = aggArgs.to_ir()
            selection = make_selection_ops(self._selection)
            value = ir.groupby_select_agg(
                target._value,
                make_groupkey_ops(by_cols),
                funcs,
                columns,
                relabels,
                selection,
                self._as_index,
                self._dropna,
                self._sort,
            )

        funcs = ["cumcount", "ngroup", "size"]
        cls = DataFrame
        logger.debug(f"check class: {func}")
        if isinstance(func, str) and self._as_index and func in funcs:
            logger.debug("check class: Series")
            cls = Series
        ret = cls._create(value)
        return process_agg_output(ret, added_cols, self._as_index, self._by)

    @property
    def dtypes(self):
        return self.__getattr__("dtypes")

    def transform(self, func, *args, **kwargs):
        if isinstance(func, str) and func not in transform_kernel_allowlist:
            msg = f"'{func}' is not a valid function name for transform"
            raise ValueError(msg)

        if (
            self._has_unsupported_groupby_args() is not None
            or isinstance(self._by, Series)
            or (
                isinstance(self._by, list)
                and any([isinstance(k, Series) for k in self._by])
            )
            or args
            or kwargs
            or not self._is_supporeted_transoform_func(func)
        ):
            return super().transform(func, *args, **kwargs)

        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )

        if self._selection is None:
            value = ir.groupby_transform(
                target._value,
                make_groupkey_ops(by_cols),
                make_tuple_of_vector_or_scalar_of_str([func]),
                make_tuple_of_column_names([]),
                make_tuple_of_column_names([]),
            )
        else:
            selection = make_selection_ops(self._selection)
            value = ir.groupby_select_transform(
                target._value,
                make_groupkey_ops(by_cols),
                make_tuple_of_vector_or_scalar_of_str([func]),
                make_tuple_of_column_names([]),
                make_tuple_of_column_names([]),
                selection,
            )

        funcs = ["cumcount", "ngroup"]
        cls = DataFrame
        if isinstance(func, str) and self._as_index and func in funcs:
            cls = Series
        ret = cls._create(value)

        return process_agg_output(ret, added_cols, self._as_index, self._by)

    def _head_or_tail(self, is_head, n=5):
        reason = []

        reason_args = self._has_unsupported_groupby_args()
        if reason_args is not None:
            reason.append(reason_args)

        if not isinstance(n, int):
            reason.append(f"unsupported 'n' = {n} of type: {type(n).__name__}")

        if len(reason) > 0:
            func = "head" if is_head else "tail"
            return self._fallback_call(
                func, args=[n], reason="; ".join(reason)
            )

        if self._selection is None:
            with_selector = False
            selection = make_selection_ops([])
        else:
            with_selector = True
            selection = make_selection_ops(self._selection)

        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )
        if added_cols and not with_selector:
            # head/tail includes all the columns in the input data
            # when called without selector. In order to exclude the apppended
            # dummy columns, adding selector with existing column names
            with_selector = True
            selection = make_selection_ops(list(self._obj.columns))

        value = ir.groupby_head_or_tail(
            target._value,
            make_groupkey_ops(by_cols),
            selection,
            with_selector,
            n,
            self._dropna,
            is_head,
        )
        return DataFrame._create(value)

    def head(self, n=5):
        logger.debug("DataFrameGroupBy.head: %s", type(self))
        return self._head_or_tail(True, n=n)

    def tail(self, n=5):
        logger.debug("DataFrameGroupBy.tail: %s", type(self))
        return self._head_or_tail(False, n=n)

    def _corrwith(self, *args, **kwargs):
        # arg = utils.decode_args(
        #    args, kwargs, pandas.core.groupby.DataFrameGroupBy.corrwith
        # )
        arg = utils.decode_args(args, kwargs, self.corrwith)
        reason = []

        reason_no_default = arg.is_not_default(
            ["drop", "axis", "method", "numeric_only"]
        )
        if reason_no_default is not None:
            reason.append(reason_no_default)

        reason_args = self._has_unsupported_groupby_args()
        if reason_args is not None:
            reason.append(reason_args)

        if reason_args is not None:
            if isinstance(self._by, Series):
                reason.append("corrwith: series as key is not supported")

        if not isinstance(arg.other, Series):
            reason.append(
                f"unsupported 'other' of type: {type(arg.other).__name__}"
            )

        if self._selection is None:
            nkeys = 1 if irable_scalar(self._by) else len(self._by)
            # shape check might cause evaluation, but better than fallback
            if (self._obj.shape[1] - nkeys) != 1:
                reason.append(
                    "Unsupported corrwith with multiple non-key-columns"
                )
            else:
                with_selector = False
                selection = make_selection_ops([])
        else:
            if (
                isinstance(self._selection, (tuple, list))
                and len(self._selection) != 1
            ):
                reason.append("Unsupported selection with multiple columns")
            else:
                with_selector = True
                selection = make_selection_ops(self._selection)

        if len(reason) > 0:
            return self._fallback_call(
                "corrwith",
                args,
                kwargs,
                reason="; ".join(reason),
            )

        by = make_groupkey_ops(self._by)
        value = ir.groupby_corrwith(
            self._obj._value,
            by,
            selection,
            arg.other._value,
            self._as_index,
            self._dropna,
            self._sort,
            with_selector,
        )
        return DataFrame._create(value)

    # pandas.core.groupby.DataFrameGroupBy.corrwith is a property
    # hence difficult to inspect signature
    def corrwith(
        self, other, axis=0, drop=False, method="pearson", numeric_only=False
    ):
        return self._corrwith(
            other,
            axis=axis,
            drop=drop,
            method=method,
            numeric_only=numeric_only,
        )

    def rank(self, *args, **kwargs):
        arg = utils.decode_args(
            args, kwargs, pandas.core.groupby.DataFrameGroupBy.rank
        )
        reason = []

        reason_no_default = arg.is_not_default(["axis", "pct"])
        if reason_no_default is not None:
            reason.append(reason_no_default)

        reason_args = self._has_unsupported_groupby_args()
        if reason_args is not None:
            reason.append(reason_args)

        if arg.method not in ("first", "dense", "average", "max", "min"):
            reason.append(f"unsupported method='{arg.method}'")

        if arg.na_option not in ("keep", "top", "bottom"):
            reason.append(f"unsupported na_option='{arg.na_option}'")

        if len(reason) > 0:
            return self._fallback_call(
                "rank", args, kwargs, reason="; ".join(reason)
            )

        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )
        if self._selection is None:
            value = ir.groupby_rank(
                target._value,
                make_groupkey_ops(by_cols),
                arg.method,
                arg.na_option,
                bool(arg.ascending),
                self._dropna,
            )
        else:
            value = ir.groupby_select_rank(
                target._value,
                make_groupkey_ops(by_cols),
                make_selection_ops(self._selection),
                arg.method,
                arg.na_option,
                bool(arg.ascending),
                self._dropna,
            )

        return DataFrame._create(value)

    def shift(self, *args, **kwargs):
        arg = utils.decode_args(
            args, kwargs, pandas.core.groupby.DataFrameGroupBy.shift
        )
        reason = []

        reason_no_default = arg.is_not_default(["freq", "axis", "fill_value"])
        if reason_no_default is not None:
            reason.append(reason_no_default)

        reason_args = self._has_unsupported_groupby_args()
        if reason_args is not None:
            reason.append(reason_args)

        if not isinstance(arg.periods, int):
            reason.append(
                f"unsupported 'periods' = {arg.periods} "
                f"of type: {type(arg.periods).__name__}"
            )

        if len(reason) > 0:
            return self._fallback_call(
                "shift", args, kwargs, reason="; ".join(reason)
            )

        if self._selection is None:
            with_selector = False
            selection = make_selection_ops([])
        else:
            with_selector = True
            selection = make_selection_ops(self._selection)

        target, by_cols, added_cols = preprocess_groupby_target(
            self._obj, self._by
        )
        value = ir.groupby_shift(
            target._value,
            make_groupkey_ops(by_cols),
            selection,
            with_selector,
            arg.periods,
            self._dropna,
        )
        return DataFrame._create(value)
