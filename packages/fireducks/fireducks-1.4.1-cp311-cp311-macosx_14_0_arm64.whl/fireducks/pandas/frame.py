# Copyright (c) 2023 NEC Corporation. All Rights Reserved.
"""FireDucks: Dataframe with FIRE"""

from __future__ import annotations

from firefw import tracing

import logging
import os
import warnings
from datetime import datetime
from pandas.core.dtypes.common import is_integer, is_dict_like
from pandas.io.formats.info import DataFrameInfo
from pandas.compat.numpy import function as nv
import datetime

import numpy as np

with tracing.scope(tracing.Level.DEFAULT, "import pandas"):
    import pandas
    from pandas.util._decorators import deprecate_nonkeyword_arguments
    from pandas.util._validators import validate_bool_kwarg, validate_ascending
    import pandas.api.extensions as pandas_extensions
    from pandas._libs.lib import is_all_arraylike

from pandas import Timestamp, Timedelta

import fireducks.core
from fireducks import ir, irutils
from fireducks.pandas.binop import (
    # get_binop_vector_scalar,
    # get_binop_vector_vector,
    get_binop_table_scalar,
    get_binop_table_vector,
    get_binop_table_table,
)

import fireducks.pandas.hinting as hinting

import fireducks.pandas.utils as utils
from fireducks.pandas.utils import (
    _pd_version_under2,
    _unwrap,
    is_interactive_terminal,
    is_notebook_like,
)

from fireducks.pandas.generic import (
    FireDucksPandasCompat,
    _Scalar,
    _install_aggregators,
    _install_binops,
    _install_fallback_mutating_method,
    _install_unary_op_fallbacks,
    _wrap_pandas,
)

from fireducks.pandas.series import Series
from fireducks.pandas.wrappers import (
    Index,
    MultiIndex,
    DatetimeIndex,
    CategoricalIndex,
    Categorical,
)
from fireducks.pandas.expr import QueryParser
from fireducks.pandas.metadata import IRMetadataWrapper

logger = logging.getLogger(__name__)


def _setup_DataFrame(cls):
    _install_aggregators(cls, pandas.DataFrame)
    _install_binops(cls, pandas.DataFrame)
    _install_unary_op_fallbacks(cls, pandas.DataFrame)

    # `_set_value` is used to call _fallback_mutating_method in
    # `test_anti_dep_fallback`. If you change it to non-fallback, please fix
    # the test. See GT #1069
    _install_fallback_mutating_method(cls, "_set_value")
    _install_fallback_mutating_method(cls, "__delitem__")

    _wrap_pandas(cls, pandas.DataFrame)
    return cls


def create_metadata(df: pandas.DataFrame):
    """Create IR metadata to pass to from_pandas"""
    from fireducks.fireducks_ext import (
        Metadata,
        ColumnMetadata,
        Scalar,
        ColumnName,
    )

    from fireducks.pandas.metadata import make_scalar as make_ext_scalar

    index = df.columns
    logger.debug("create_metadata: df.columns.nlevels=%d", index.nlevels)
    logger.debug("create_metadata: df.columns.names=%s", index.names)
    logger.debug(
        "create_metadata: isMultiindex=%s",
        isinstance(index, pandas.MultiIndex),
    )

    def to_column_name(name, isMulti):
        if isinstance(name, (frozenset, tuple)):
            scalars = [make_ext_scalar(e) for e in name]
            return (
                ColumnName.MultiFromScalars(scalars)
                if isMulti
                else ColumnName.SingleFromScalars(scalars)
            )

        return ColumnName.Single(make_ext_scalar(name))

    def to_column_index_name(index, isMulti):
        if isMulti:
            return ColumnName.MultiFromScalars(
                [make_ext_scalar(e) for e in index.names]
            )
        else:
            return ColumnName.Single(make_ext_scalar(index.name))

    isMulti = isinstance(index, pandas.MultiIndex)
    column_names = [to_column_name(name, isMulti) for name in index]
    columns = [ColumnMetadata(name) for name in column_names]
    column_index_names = to_column_index_name(index, isMulti)
    return Metadata(
        columns, column_index_names, isinstance(df.index, pandas.MultiIndex)
    )


def _from_pandas_frame(df: pandas.DataFrame):
    """
    Returns fire.Value
    """
    logger.debug("_from_pandas_frame")
    if fireducks.core.get_ir_prop().has_metadata:
        # rename to ensure no duplicated column name. Here we will rename only
        # columns, but those should not conflict with index. We use
        # `__fireducks_dummy_` prefix.
        copy = df.copy(deep=False)
        copy.columns = [
            f"__fireducks_dummy_{i}" for i in range(len(df.columns))
        ]
        f = fireducks.core.make_available_value(copy, ir.Ty_pyobj)
        metadata = create_metadata(df)
        # logger.debug('_from_pandas_frame: metadata=%s', metadata)
        m = fireducks.core.make_available_value(metadata, ir.MetadataType)
        return ir.from_pandas_frame_metadata(f, m)
    else:
        f = fireducks.core.make_available_value(df, ir.Ty_pyobj)
        return ir.from_pandas_dataframe(f)


def _get_projected_class_from_hint(before: TableHint, after: TableHint, key):
    assert before is not None
    assert after is not None
    assert len(after.columns) > 0

    if len(after.columns) > 1:
        return DataFrame

    # If key is a part of multi-level name, result should be DataFrame.
    # Ex:
    #   - before: ("a", "b"), key: "a"        => DataFrame  after: "b"
    #   - before: ("a", "b"), key: ("a",)     => DataFrame  after: "b"
    #   - before: ("a", "b"), key: ("a", "b") => Series     after: ("a", "b")
    #   - before: ("a",),     key: "a"        => DataFrame  after: "a"
    #   - before: ("a",),     key: ("a",)     => Series     after: ("a",)
    #   - before: ("a", ""),  key: "a"        => Series     after: "a"
    #   - before: ("a", ""),  key: ("a",)     => Series     after: ("a",)

    if before.columns.is_multilevel:

        def find_projected_col(columns, key):
            key = list(key) if isinstance(key, tuple) else [key]
            for col in columns:
                if col.name[: len(key)] == key:
                    return col
            return None

        def get_actual_rank(name):
            non_empty = [x for x in name if x != ""]
            if len(name) == len(non_empty):
                return len(name)
            return 0 if len(non_empty) == 1 else len(non_empty)

        bcol = find_projected_col(before.columns, key)
        assert bcol is not None

        # rank: "a"->0, ("a",)->1, ("a", "b")->2
        key_rank = len(key) if isinstance(key, tuple) else 0
        bcol_rank = get_actual_rank(bcol.name)
        if bcol_rank > key_rank:
            return DataFrame

    return Series


def _is_columns_dict(obj):
    if not isinstance(obj, dict):
        return False

    return all([irutils.is_column_name(x) for x in obj.keys()]) and all(
        [isinstance(x, Series) for x in obj.values()]
    )


def _parse_frame_creation_args(args, kwargs):
    value = kwargs.get("_value")
    hint = kwargs.get("__hint")

    if value is not None:
        return value, None, hint

    if len(kwargs) == 0 and len(args) == 1 and _is_columns_dict(args[0]):
        value = ir.create_table_from_columns(
            columns=irutils.make_tuple_of_tables(args[0].values()),
            column_names=irutils.make_tuple_of_column_names(args[0].keys()),
        )
        return value, None, hint

    obj = kwargs.pop("__fireducks_from_pandas", None)
    if obj is None:
        reason = "args of DataFrame.__init__"
        tmp = [_unwrap(x, reason=reason) for x in args]
        obj = pandas.DataFrame(*tmp, **_unwrap(kwargs))
    assert isinstance(obj, pandas.DataFrame)

    if hint is None:
        hint = hinting.create_hint_from_pandas_frame(obj)

    return _from_pandas_frame(obj), obj, hint


@_setup_DataFrame
class DataFrame(FireDucksPandasCompat):
    _constructor_sliced: type[Series] = Series
    _metadata = []

    def __init__(self, *args, **kwargs):
        """
        Three types of constructors.

        1. Construct from fire.Value
             Used when kwargs has `_value`
        2. Construct from pandas.DataFrame
             Used when kwargs has `__fireducks_from_pandas`
        3. Construct from pandas-like arguments
             Used in other cases
        """
        logger.debug("DataFrame.__init__")

        value, obj, hint = _parse_frame_creation_args(args, kwargs)
        super().__init__(value, pandas_object=obj, hint=hint)

        if fireducks.core.get_fireducks_options().benchmark_mode:
            self._evaluate()

    def __dir__(self):
        reason = "DataFrame.__dir__ is called"
        return self.head()._fallback_call("__dir__", reason=reason)

    def __finalize__(self, other, method=None):
        logger.debug("DataFrame.__finalize__: method=%s", method)
        if isinstance(other, DataFrame):
            for name in set(self._metadata) & set(other._metadata):
                assert isinstance(name, str)
                logger.debug("DataFrame.__finalize__: setattr name=%s", name)
                object.__setattr__(self, name, getattr(other, name, None))
        return self

    def __getattr__(self, name):
        logger.debug("DataFrame.__getattr__: name=%s", name)

        # avoiding unnecessary fallback for internal attributes. To support
        # checking by hasattr(obj, "_fireducks_foo"), assert should not be used
        # here.
        if name.startswith("_fireducks"):
            return object.__getattribute__(self, name)

        unsupp = [
            # avoiding unnecessary fallback for methods which might be called
            # from utilities like ipython display formatters...
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
            "javascript",
            "markdown",
            "mimebundle",
            "pdf",
            "json",
        ]
        if name in unsupp + ["_repr_" + x + "_" for x in repr_unsupp]:
            return object.__getattribute__(self, name)

        # Because fireducks.DataFrame do not explicitly define all
        # pandas.DataFrame API, undefined API reaches here when it is called.
        # It should be handled as API, not as column name, we have to check if
        # it is API.
        if name not in pandas.DataFrame.__dict__:
            if self._is_column_name(name):
                return self[name]

        reason = f"{type(self).__name__}.__getattr__ for {name} is called"
        return utils.fallback_attr(self._unwrap, name, reason)

    def __len__(self):
        return self.shape[0]

    def __iter__(self):
        return iter(self._get_column_names())

    def __abs__(self):
        return self.abs()

    def __contains__(self, cname):
        if irutils.irable_scalar(cname):
            return cname in self.columns
        reason = f"input '{cname}' is not of irable-scalar type"
        return self.head()._fallback_call(
            "__contains__", args=(cname,), reason=reason
        )

    def __neg__(self):
        return DataFrame._create(ir.negate(self._value))

    def __round__(self, decimals=0):
        return self.round(decimals)

    def _ipython_display_(self):
        try:
            __IPYTHON__
        except NameError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has "
                "no attribute '_ipython_display_'"
            )
        from IPython.display import display

        if is_notebook_like():
            # notebook by-default prints in html-format
            # hence, to avoid calling all available formatters and select
            # the suitable one based on UI, limiting the format to html only
            data = {"text/html": self._repr_html_()}
        elif is_interactive_terminal():
            # terminal by-default prints in text-format
            data = {"text/plain": "\n" + repr(self)}
        else:
            # leaving it to the UI to select the suitable display format
            data = {
                "text/html": self._repr_html_(),
                "text/plain": "\n" + repr(self),
            }
        display(data, raw=True)

    def __repr__(self):
        ret, is_trunc = self.__get_trunc_repr_method_result__(
            method="__repr__"
        )
        if is_trunc:
            truncated_shape_info = ret.rsplit("\n", 1)[1]
            nrow, ncol = self.shape  # actual
            actual_shape_info = (
                "[" + str(nrow) + " rows x " + str(ncol) + " columns]"
            )
            # replacing truncated shape info with actual shape info
            truncated_shape_info_len = len(truncated_shape_info)
            return ret[:-truncated_shape_info_len] + actual_shape_info
        else:
            return ret

    def _repr_html_(self):
        ret, is_trunc = self.__get_trunc_repr_method_result__(
            method="_repr_html_"
        )
        if is_trunc:
            truncated_shape_info = "\n".join(ret.rsplit("\n", 2)[1:])
            nrow, ncol = self.shape  # actual
            actual_shape_info = (
                "<p>"
                + str(nrow)
                + " rows x "
                + str(ncol)
                + " columns</p>\n</div>"
            )
            # replacing truncated shape info with actual shape info
            truncated_shape_info_len = len(truncated_shape_info)
            return ret[:-truncated_shape_info_len] + actual_shape_info
        else:
            return ret

    def _repr_latex_(self):
        if self._fireducks_meta.is_cached("pandas_object"):
            return utils._wrap(
                self._fireducks_meta.get_cache("pandas_object")._repr_latex_()
            )

        # to avoid fallback...
        is_no_op = (
            not pandas.get_option("display.latex.repr")
            if _pd_version_under2
            else pandas.get_option("styler.render.repr") != "latex"
        )
        if is_no_op:
            return None

        reason = f"{type(self).__name__}._repr_latex_ is called"
        return utils.fallback_attr(self._unwrap, "_repr_latex_", reason)

    def __invert__(self):
        return DataFrame._create(ir.invert(self._value))

    def __setattr__(self, name, value):
        logger.debug("DataFrame.__setattr__: name=%s", name)

        # Known fireducks.DataFrame properties
        # Because columns is property, __setattr__ is called when columns = ..
        if name in ["_value", "columns", "index"]:
            return object.__setattr__(self, name, value)

        if name in ["attrs"]:
            return self._fallback_mutating_method(
                "__setattr__", args=[name, value]
            )

        # Existing user-defined properties
        try:
            object.__getattribute__(self, name)
            return object.__setattr__(self, name, value)
        except AttributeError:
            pass

        if name in self.columns:
            return self.__setitem__(name, value)

        # New user-defined properties
        object.__setattr__(self, name, value)

    @classmethod
    def _create(cls, value, *, hint=None):
        """
        Create new DataFrame instance from fire.Value
        """
        assert value.type() == ir.TableType
        return DataFrame(_value=value, __hint=hint)

    def _create_or_inplace(self, value, inplace):
        inplace = validate_bool_kwarg(inplace, "inplace")
        if inplace:
            return self._rebind(value, invalidate_cache=True)
        return DataFrame._create(value).__finalize__(self)

    @classmethod
    def _get_axis_number(cls, axis):
        # For some aggregation methods in Pandas 1.5.3, the default value for
        # the `axis` argument is no_default.
        if utils._pd_version_under2 and axis == pandas_extensions.no_default:
            axis = 0
        return pandas.DataFrame._get_axis_number(axis)

    def _get_column_names(self):
        # To prevent fallback, cache is explicitly checked here
        if self._fireducks_meta.is_cached("pandas_object"):
            return list(
                self._fireducks_meta.get_cache("pandas_object").columns
            )
        else:
            if fireducks.core.get_ir_prop().has_metadata:
                return self._get_metadata().column_names
            return list(self.columns)

    def _is_column_name(self, name):
        # logger.debug("__getattr____: hint=%s", self._fireducks_hint)
        if hinting.is_column_name(self._fireducks_hint, name):
            return True
        return name in self._get_column_names()

    # fireducks method for debug
    def _print(self):
        ch = ir.print_table(self._value)
        fireducks.core.evaluate([ch])

    def _to_pandas(self, options=None):
        if fireducks.core.get_ir_prop().has_metadata:
            result = _to_pandas_frame_metadata(self._value, options)
        else:
            value = ir.to_pandas(self._value)
            result = fireducks.core.evaluate([value], options)[0]
        assert isinstance(
            result, pandas.DataFrame
        ), f"{type(result)} is not pandas.DataFrame"

        return result

    @classmethod
    def from_pandas(cls, df):
        if not isinstance(df, pandas.DataFrame):
            raise RuntimeError(
                "DataFrame.from_pandas: illegal argument: "
                f"{df.__class__.__name__}"
            )
        return DataFrame(__fireducks_from_pandas=df)

    #
    # Pandas methods (alphabetical)
    #

    # fireducks.DataFrame.__getitem__ returns Series even when DataFrame has
    # multilevel column index. This method can force returning DataFrame.
    def _project(self, key, as_frame=False):
        logger.debug("_project: hint=%s", self._fireducks_hint)
        hint = hinting.infer_project(self._fireducks_hint, key)
        logger.debug("_project: hint=%s", hint)

        cls = Series
        if isinstance(key, list):
            cls = DataFrame
        elif hint is not None and hint.columns is not None:
            if len(hint.columns) == 0:
                raise KeyError(key)
            cls = _get_projected_class_from_hint(
                self._fireducks_hint, hint, key
            )

        # FIXME: Remove as_frame after hint replace it
        if as_frame:
            cls = DataFrame

        key = irutils.make_vector_or_scalar_of_column_name(key)
        return cls._create(
            ir.project(self._value, key), hint=hint
        ).__finalize__(self, method="project")

    def __getitem__(self, key):
        logger.debug("DataFrame.__getitem__: type(key)=%s", type(key))
        to_filter, mask, ignore_index = utils.is_filter_like(key)
        if to_filter:
            return DataFrame._create(
                ir.filter(self._value, mask._value, no_align=ignore_index)
            )

        elif isinstance(key, slice) and utils.is_int_or_none_slice(key):
            if key.step is None or key.step == 1:
                return self._slice(key)

        if isinstance(key, Index):
            key = list(key)
        if irutils.is_column_name(key) or (
            isinstance(key, list)
            and all([irutils.is_column_name(x) for x in key])
        ):
            return self._project(key)

        reason = f"Unsupported key type: {type(key)}"
        return self._fallback_call("__getitem__", args=[key], reason=reason)

    def __setitem__(self, key: str, value):
        logger.debug("DataFrame.__setitem__")

        def _fallback(key=key, value=value, reason=None):
            self._fallback_mutating_method(
                "__setitem__",
                args=(key, value),
                reason=reason,
            )

        if not irutils.is_column_name_or_column_names(key):
            return _fallback(reason="key doesn't look like a column name")

        if irutils.irable_scalar(value):
            key = irutils.make_vector_or_scalar_of_column_name(key)
            value = irutils.make_vector_or_scalar_of_scalar(value)
            self._rebind(
                ir.assign_scalar(self._value, key, value),
                invalidate_cache=True,
            )
            return self

        # index can be ignored for these cases...
        ignore_index = isinstance(value, (list, range, np.ndarray, Index))

        if isinstance(value, list):
            # See GT #1864
            unwrap_not_required = all(
                [x is None or isinstance(x, (int, float, str)) for x in value]
            )
            if unwrap_not_required:
                # To bypass unwrap in Series.__init__, create pandas.Series.
                value = Series.from_pandas(pandas.Series(value))

        if isinstance(value, np.ndarray) and (
            value.ndim == 1 or (value.ndim == 2 and value.shape[1] == 1)
        ):
            if value.dtype.names is not None:
                raise ValueError(
                    "fireducks does not support setting numpy.recarray into a column"
                )
            value = Series(value.ravel())

        if isinstance(value, (Index, range)):
            value = Series(value)

        if not isinstance(value, FireDucksPandasCompat):
            return _fallback(reason="value is not FireDucksPandasCompat")

        if isinstance(key, Index):
            key = list(key)
        keys = irutils.make_vector_or_scalar_of_column_name(key)
        self._rebind(
            ir.setitem(
                self._value,
                keys,
                value._value,
                ignore_index,
            ),
            invalidate_cache=True,
        )
        return self

    def __setstate__(self, state):
        logger.debug("DataFrame.__setstate__")
        obj = object.__new__(pandas.DataFrame)
        obj.__setstate__(state)
        self.__init__(__fireducks_from_pandas=obj)

    def abs(self):
        return DataFrame._create(ir.abs(self._value))

    def aggregate(self, *args, **kwargs):
        from fireducks.pandas.aggregate import frame_aggregate

        return frame_aggregate(self, *args, **kwargs)

    agg = aggregate

    def _agg_func(self, func, args, kwargs):
        from fireducks.pandas.aggregate import frame_agg_func

        return frame_agg_func(self, func, args, kwargs)

    def assign(self, **kwargs):
        data = self.copy()
        for k, v in kwargs.items():
            data[k] = v(data) if callable(v) else v
        return data

    def _set_column_index_names(self, name):  # inplace
        logger.debug("DataFrame._set_column_index_names")
        name = irutils.make_column_name(name)
        value = ir.set_column_index_names(self._value, name)
        self._rebind(value, invalidate_cache=True)

    @property
    def columns(self):
        """The column labels of the DataFrame."""
        logger.debug("DataFrame.columns")
        if self._fireducks_meta.is_cached("pandas_object"):
            columns = utils._wrap(
                self._fireducks_meta.get_cache("pandas_object").columns
            )
            columns._set_fireducks_frame(self, "columns")
            return columns

        if fireducks.core.get_ir_prop().has_metadata:
            metadata = self._get_metadata()
            pandas_columns = metadata.create_column_index()
            columns = utils._wrap(pandas_columns)
            columns._set_fireducks_frame(self, "columns")
            return columns

        columns = utils.fallback_attr(
            self._unwrap,
            "columns",
            reason=f"{type(self).__name__}.columns",
        )
        columns._set_fireducks_frame(self, "columns")
        return columns

    @columns.setter
    def columns(self, value):
        logger.debug("columns: type=%s", type(value))
        if value is None:
            raise TypeError(
                "Index(...) must be called with a collection of some kind"
                ", None was passed"
            )
        if not irutils._is_irable_scalar_arraylike(value):
            return self._fallback_mutating_method(
                "__setattr__",
                args=["columns", value],
                reason="columns_setter: input is not an array-like of irable-scalar",
            )
        cols = irutils.make_tuple_of_column_names(value)
        self._rebind(ir.rename(self._value, cols), invalidate_cache=True)
        return self

    def corr(self, *args, **kwargs):
        decoded = utils.decode_args(args, kwargs, pandas.DataFrame.corr)
        if decoded.numeric_only is pandas_extensions.no_default:
            decoded.numeric_only = True
        decoded.numeric_only = validate_bool_kwarg(
            decoded.numeric_only, "numeric_only"
        )
        reason = []

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

        return DataFrame._create(
            ir.table_corr(
                self._value,
                decoded.method,
                decoded.min_periods,
                decoded.numeric_only,
            )
        )

    def drop_duplicates(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.drop_duplicates)
        arg.inplace = validate_bool_kwarg(arg.inplace, "inplace")
        arg.ignore_index = validate_bool_kwarg(
            arg.ignore_index, "ignore_index"
        )
        supported_keep = {"first", "last", False}

        if (
            arg.subset is None
            or isinstance(arg.subset, str)
            or (
                utils._is_str_list_or_index(arg.subset) and len(arg.subset) > 0
            )
        ) and arg.keep in supported_keep:
            if arg.subset is None:
                arg.subset = []  # empty means all column
            if isinstance(arg.subset, str):
                arg.subset = [arg.subset]
            logger.debug(f"subset.size={len(arg.subset)}")
            arg.subset = irutils.make_tuple_of_column_names(arg.subset)
            arg.keep = "none" if not arg.keep else arg.keep
            keep_org_index_when_no_dup = not _pd_version_under2
            value = ir.drop_duplicates(
                self._value,
                arg.subset,
                arg.keep,
                arg.ignore_index,
                keep_org_index_when_no_dup,
            )
            return self._create_or_inplace(value, arg.inplace)

        return self._fallback_may_inplace(
            "drop_duplicates",
            args,
            kwargs,
            pos=3,
            reason="unsupported argument",
        )

    @deprecate_nonkeyword_arguments(version=None, allowed_args=["self"])
    def dropna(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.dropna)
        if isinstance(arg.axis, (list, tuple)):
            raise TypeError(
                "supplying multiple axes to axis is no longer supported."
            )

        axis = self._get_axis_number(arg.axis)

        reason = None
        if axis == 1:
            if arg.subset is not None:
                reason = "dropna(axis=1) with subset"
        else:
            supported = (
                arg.subset is None
                or isinstance(arg.subset, str)
                or (
                    utils._is_str_list_or_index(arg.subset)
                    and len(arg.subset) > 0
                )
            )
            if not supported:
                reason = "dropna(axis=0) with unsupported subset"

        if not reason:
            if arg.subset is None:
                arg.subset = []  # empty means all column when axis=1
            if isinstance(arg.subset, str):
                arg.subset = [arg.subset]
            logger.debug(f"subset.size={len(arg.subset)}")
            subset = irutils.make_tuple_of_column_names(arg.subset)
            axis = irutils.make_scalar(axis)
            # ignore_index is introduced in pandas-2
            ignore_index = (
                validate_bool_kwarg(arg.ignore_index, "ignore_index")
                if hasattr(arg, "ignore_index")
                else False
            )
            if arg.thresh is pandas_extensions.no_default:
                if arg.how is pandas_extensions.no_default or arg.how == "any":
                    value = ir.dropna(
                        self._value, subset, axis, ignore_index, True, 0
                    )
                    return self._create_or_inplace(value, arg.inplace)
                elif arg.how == "all":
                    value = ir.dropna(
                        self._value, subset, axis, ignore_index, False, 1
                    )
                    return self._create_or_inplace(value, arg.inplace)
            else:
                if arg.how is pandas_extensions.no_default:
                    value = ir.dropna(
                        self._value,
                        subset,
                        axis,
                        ignore_index,
                        False,
                        arg.thresh,
                    )
                    return self._create_or_inplace(value, arg.inplace)

        return self._fallback_may_inplace(
            "dropna",
            args,
            kwargs,
            pos=3,
            reason="unsupported argument",
        )

    def duplicated(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.duplicated)
        supported_keep = {"first", "last", False}

        if (
            arg.subset is None
            or isinstance(arg.subset, str)
            or (
                utils._is_str_list_or_index(arg.subset) and len(arg.subset) > 0
            )
        ) and arg.keep in supported_keep:
            if arg.subset is None:
                arg.subset = []  # empty means all column
            if isinstance(arg.subset, str):
                arg.subset = [arg.subset]
            logger.debug(f"subset.size={len(arg.subset)}")
            arg.subset = irutils.make_tuple_of_column_names(arg.subset)
            arg.keep = "none" if not arg.keep else arg.keep
            return Series._create(
                ir.duplicated(self._value, arg.subset, arg.keep)
            )

        return self._fallback_call(
            "duplicated", args, kwargs, reason="unsupported argument"
        )

    def _get_dtypes(self):
        # This method is evaluation point.
        #
        # This method returns PandasWrapper, not fireducks.Series because
        # contents of Series is numpy.dtype, i.e. python object, which can not
        # be converted to arrow.

        if fireducks.core.get_ir_prop().has_metadata:
            dtypes, unsupported = self._get_metadata()._get_dtypes(self)
            if len(unsupported) == 0:
                return dtypes, None
            reason = "DataFrame.dtypes includes unsupported type: " + ",".join(
                unsupported
            )
        else:
            reason = "IR does not support metadata"
        return None, reason

    @property
    def dtypes(self):
        def wrap(obj):
            return utils.PandasWrapper(obj, Series)

        if self._fireducks_meta.is_cached("pandas_object"):
            return wrap(self._fireducks_meta.get_cache("pandas_object").dtypes)

        if self._fireducks_meta.is_cached("dtypes"):
            return self._fireducks_meta.get_cache("dtypes")

        dt, reason = self._get_dtypes()
        if reason is None:
            dt = wrap(dt)
            self._fireducks_meta.set_cache("dtypes", dt)
            return dt

        # No need to cache 'dtypes' when fallback occurs,
        # since fallback caches the 'pandas_object' itself
        return utils.fallback_attr(
            self._unwrap, "dtypes", reason=reason, wrap_func=wrap
        )

    def explode(self, column, ignore_index=False):
        if isinstance(column, list):
            if not column:
                raise ValueError("column must be nonempty")
            is_supported_names = all(
                [irutils.is_column_name(x) for x in column]
            )
            if is_supported_names and len(column) > len(set(column)):
                raise ValueError("column must be unique")
        else:
            is_supported_names = irutils.is_column_name(column)

        if not is_supported_names:
            reason = f"unsupported column of type: {type(column).__name__}"
            return self._fallback_call(
                "explode", args=[column, ignore_index], reason=reason
            )

        column = [column] if not isinstance(column, list) else column
        column = irutils.make_tuple_of_column_names(column)
        # according to pandas behavior. all true values would be treated
        # as true. e.g., ignore_index="a" would be treated as ignore_index=True
        ignore_index = bool(ignore_index)
        return DataFrame._create(ir.explode(self._value, column, ignore_index))

    def eval(self, *args, **kwargs):
        kwargs["level"] = kwargs.pop("level", 0) + 5
        return self._fallback_call_unpacked("eval", *args, **kwargs)

    def filter(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.filter)
        if arg.axis is None:
            arg.axis = 1

        reason = arg.is_not_default(["like", "regex"])
        if reason:
            pass
        elif not irutils._is_scalar_or_list_or_tuple_of(arg.items, str):
            reason = "items is not a list of str"
        elif not (arg.axis == 1 or arg.axis == "columns"):
            reason = "axis is not 1"
        else:
            labels = self._get_column_names()
            cols = [r for r in arg.items if r in labels]
            return self[cols]

        return self._fallback_call("filter", args, kwargs, reason=reason)

    def groupby(self, by=None, *args, **kwargs):
        logger.debug("groupby: type(by)=%s", type(by))
        from fireducks.pandas.groupby import DataFrameGroupBy

        return DataFrameGroupBy(self, by=by, *args, **kwargs)

    # for output formatting, it relies on pandas itself
    def info(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.info)
        # mostly copied from pandas DataFrame.info() implementation
        return DataFrameInfo(
            data=self,
            memory_usage=arg.memory_usage,
        ).render(
            buf=arg.buf,
            max_cols=arg.max_cols,
            verbose=arg.verbose,
            show_counts=arg.show_counts,
        )

    def insert(self, *args, **kwargs):
        # TODO: unwrap args when it includes fireducks.pandas.Series
        self._fallback_mutating_method("insert", args, kwargs)

    def isna(self):
        return DataFrame._create(ir.isnull(self._value))

    def isnull(self):
        return DataFrame._create(ir.isnull(self._value))

    def join(self, *args, **kwargs):
        class MergeOperation:
            def __init__(self, left, right):
                self.left = left
                self.right = right

        arg = utils.decode_args(args, kwargs, pandas.DataFrame.join)
        if not isinstance(arg.other, DataFrame):
            reason = "other is not DataFrame"
        elif arg.how not in ("left", "right", "inner", "outer"):
            reason = "how is not left, right, inner, or outer"
        elif not isinstance(arg.lsuffix, str):
            reason = "lsuffix is not str"
        elif not isinstance(arg.rsuffix, str):
            reason = "rsuffix is not str"
        else:
            reason = arg.is_not_default(
                [
                    "on",
                    # "how", "lsuffix", "rsuffix",
                    "sort",
                    "validate",
                ]
            )

        if reason:
            return self._fallback_call("join", args, kwargs, reason=reason)

        op = MergeOperation(self, arg.other)
        on = irutils.make_tuple_of_column_names([])
        left_on = right_on = on

        lsuffix = irutils.make_optional_string(arg.lsuffix)
        rsuffix = irutils.make_optional_string(arg.rsuffix)

        return DataFrame._create(
            ir.join(
                self._value,
                arg.other._value,
                arg.how,
                on,
                left_on,
                True,
                right_on,
                True,
                lsuffix,
                rsuffix,
            )
        ).__finalize__(op, "merge")

    def memory_usage(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.memory_usage)
        return Series._create(
            ir.get_table_memory_usage(self._value, arg.deep, arg.index)
        )

    def melt(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.melt)
        reason = arg.is_not_default(["col_level"])

        if not reason:
            supported_value_vars = (
                arg.value_vars is None
                or irutils._is_scalar_or_list_of(arg.value_vars, str)
                or irutils._is_scalar_or_list_of(arg.value_vars, int)
            )
            if not supported_value_vars:
                reason = f"unsupported {arg.value_vars=}"

        if reason is not None:
            return self._fallback_call("melt", args, kwargs, reason=reason)

        if not _pd_version_under2:

            def reset_none_if_empty_list(*args):
                return [
                    None if isinstance(e, list) and len(e) == 0 else e
                    for e in args
                ]

            arg.id_vars, arg.value_vars = reset_none_if_empty_list(
                arg.id_vars, arg.value_vars
            )
        arg.id_vars = irutils.make_vector_or_scalar_of_column_name(arg.id_vars)
        arg.value_vars = irutils.make_vector_or_scalar_of_column_name(
            arg.value_vars
        )
        arg.var_name = irutils.make_column_name(arg.var_name)
        arg.value_name = irutils.make_column_name(arg.value_name)
        value = ir.melt(
            self._value,
            arg.id_vars,
            arg.value_vars,
            arg.var_name,
            arg.value_name,
            arg.ignore_index,
        )
        return DataFrame._create(value)

    def items(self):
        df = self.to_pandas()
        for label, column in df.items():
            yield label, utils._wrap(column)

    def merge(
        self,
        *args,
        **kwargs,
    ):
        class MergeOperation:
            def __init__(self, left, right):
                self.left = left
                self.right = right

        arg = utils.decode_args(args, kwargs, pandas.DataFrame.merge)
        reason = None

        def is_series_or_index_or_ndarray(keys):
            key_list = keys if isinstance(keys, (list, tuple)) else [keys]
            return any(
                isinstance(
                    key,
                    (Index, Series, CategoricalIndex, Categorical, np.ndarray),
                )
                for key in key_list
            )

        if not (
            isinstance(arg.suffixes, (list, tuple))
            and len(arg.suffixes) == 2
            and all([isinstance(x, (str, type(None))) for x in arg.suffixes])
        ):
            reason = "unsupported suffix"
        elif not isinstance(arg.left_index, bool) or not isinstance(
            arg.right_index, bool
        ):
            reason = "left_index or right_index is not bool"
        elif is_series_or_index_or_ndarray(arg.on):
            reason = "on is series or index or ndarray"
        elif is_series_or_index_or_ndarray(arg.left_on):
            reason = "left_on is series or index or ndarray"
        elif is_series_or_index_or_ndarray(arg.right_on):
            reason = "right_on is series or index or ndarray"
        elif not irutils.is_column_name_or_column_names(arg.on):
            reason = "on is not column name supported by IR"
        elif not irutils.is_column_name_or_column_names(arg.left_on):
            reason = "left_on is not column name supported by IR"
        elif not irutils.is_column_name_or_column_names(arg.right_on):
            reason = "right_on is not column name supported by IR"
        elif arg.how not in ("left", "right", "inner", "outer"):
            reason = f"unsupported how: {arg.how}"
        else:
            reason = arg.is_not_default(
                ["sort", "copy", "indicator", "validate"]
            )
        op = MergeOperation(self, arg.right)

        if reason is not None:
            return self._fallback_call(
                "merge", args, kwargs, reason=reason
            ).__finalize__(op, "merge")

        left_suffix = irutils.make_optional_string(arg.suffixes[0])
        right_suffix = irutils.make_optional_string(arg.suffixes[1])

        # None cannot be used as column name in merge, so check before backend.
        if (
            isinstance(arg.on, list)
            and len(arg.on) == 0
            and arg.left_index == False
            and arg.right_index == False
        ):
            raise IndexError("list index out of range")
        elif (
            isinstance(arg.left_on, list)
            and len(arg.left_on) == 0
            and arg.left_index == False
            and arg.right_index == True
        ):
            raise ValueError(
                'len(left_on) must equal the number of levels in the index of "right"'
            )
        elif (
            isinstance(arg.right_on, list)
            and len(arg.right_on) == 0
            and arg.left_index == True
            and arg.right_index == False
        ):
            raise ValueError(
                'len(right_on) must equal the number of levels in the index of "left"'
            )

        def to_list(x):
            # None can not be used as column name in merge
            if x is None:
                return []
            return x if isinstance(x, list) else [x]

        on = irutils.make_tuple_of_column_names(to_list(arg.on))
        left_on = irutils.make_tuple_of_column_names(to_list(arg.left_on))
        right_on = irutils.make_tuple_of_column_names(to_list(arg.right_on))

        return DataFrame._create(
            ir.join(
                self._value,
                arg.right._value,
                arg.how,
                on,
                left_on,
                arg.left_index,
                right_on,
                arg.right_index,
                left_suffix,
                right_suffix,
            )
        ).__finalize__(op, "merge")

    def notna(self):
        return ~self.isnull()

    def notnull(self):
        return ~self.isnull()

    def pop(self, item):
        out = self[item]
        self.drop(columns=[item], inplace=True)
        return out

    def quantile(self, *args, **kwargs):
        reason = None
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.quantile)

        axis = self._get_axis_number(arg.axis)
        if axis == 1:
            reason = f"unsupported quantile on axis = {arg.axis}"

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

        if arg.is_not_default(["numeric_only"]):
            reason = f"unsupported 'numeric_only' = {arg.numeric_only}"

        if arg.method not in {"single", "table"}:
            reason = f"unsupported 'method' = {arg.method}"

        if reason:
            return self._fallback_call("quantile", args, kwargs, reason=reason)

        is_scalar = irutils.irable_scalar(arg.q)
        if is_scalar:
            arg.q = float(arg.q)
            CONS = Series._create
        else:
            arg.q = [float(e) for e in arg.q]
            CONS = DataFrame._create
        qs = irutils.make_vector_or_scalar_of_scalar(arg.q)
        return CONS(ir.quantile(self._value, qs, arg.interpolation))

    def query(self, expr, *, inplace=False, **kwargs):
        reason = None

        if inplace:
            reason = "query with inplace"

        # parameters 'engine' and 'parser' get ignored internally,
        # when some valid values are given.Otherwise, falls back
        # to pandas for error handling etc.
        from pandas.core.computation.check import NUMEXPR_INSTALLED

        known_engines = {"python"}
        if NUMEXPR_INSTALLED:
            known_engines.add("numexpr")
        engine = kwargs.get("engine")
        if engine is None:
            engine = "python"
        if engine not in known_engines:
            reason = f"unknown engine = {engine}"

        known_parsers = {"pandas"}
        parser = kwargs.get("parser")
        if parser is None:
            parser = "pandas"  # default in pandas.eval
        if parser not in known_parsers:
            reason = f"unknown parser = {parser}"

        local_dict = kwargs.get("local_dict")
        known_kwargs = {"engine", "level", "local_dict", "parser"}
        tmp = set(kwargs.keys()) - known_kwargs
        if len(tmp) != 0:
            reason = f"unsupported kwargs: {tmp}"

        if not reason:
            level = kwargs.get("level", 0) + 2
            try:
                parser = QueryParser(self, level, local_dict=local_dict)
                key = parser.visit(expr)
                if isinstance(key, Series):
                    dtype = utils._deduce_dtype(key)
                    if dtype is not None and dtype == bool:
                        return DataFrame._create(
                            ir.filter(self._value, key._value)
                        )
                    else:
                        reason = "non-boolean key is given"
                else:
                    reason = (
                        "Non-series parser output of type: "
                        f"{type(key).__name__}"
                    )
            except Exception as e:
                reason = "QueryParser exception: " + str(e)

        kwargs = kwargs | {
            "level": kwargs.get("level", 0) + 5,
            "inplace": inplace,
            "local_dict": local_dict,
        }
        return self._fallback_call(
            "query", args=[expr], kwargs=kwargs, reason=reason
        )

    def rename(
        self,
        mapper=None,
        *,
        index=None,
        columns=None,
        inplace=False,
        axis=None,
        copy=None,
        level=None,
        errors="ignore",
    ):
        mapper, index, columns, axis, copy, level, errors = _unwrap(
            [mapper, index, columns, axis, copy, level, errors]
        )

        reason = None
        _columns = None

        if axis is not None:
            if columns is not None or index is not None:
                raise TypeError(
                    "Cannot specify both 'axis' "
                    "and any of 'index' or 'columns'"
                )

        if mapper is not None:
            if columns is not None or index is not None:
                raise TypeError(
                    "Cannot specify both 'mapper' "
                    "and any of 'index' or 'columns'"
                )
            if axis == 1:
                _columns = mapper

        if columns is not None:
            if index is not None:
                reason = "Unsupported rename with both columns and index"
            _columns = columns

        if callable(_columns) and (
            self._fireducks_meta.is_cached("pandas_object")
            or fireducks.core.get_ir_prop().has_metadata
        ):
            _columns = {c: _columns(c) for c in self.columns}
        if isinstance(_columns, dict):
            if errors != "ignore":  # TODO support at kernel side
                reason = f"Unsupported rename with errors='{errors}'"
            if level is not None:
                reason = f"Unsupported rename with level='{level}'"
            if copy is not None and not copy:
                reason = f"Unsupported rename with copy='{copy}'"

            for k in _columns.keys():
                if isinstance(k, tuple):
                    reason = f"MultiIndex key: {k} is not supported"
                    break

            if reason is None:
                cols = irutils.make_tuple_of_column_names(
                    list(_columns.keys())
                )
                newcols = irutils.make_tuple_of_column_names(
                    list(_columns.values())
                )
                ret = ir.rename_specified(self._value, cols, newcols)
                return self._create_or_inplace(ret, inplace)
        else:
            reason = (
                "Unsupported rename using columns of "
                + f"type: '{type(_columns).__name__}'"
            )

        fallback = self._get_fallback(inplace)
        return fallback(
            "rename",
            kwargs={
                "mapper": mapper,
                "index": index,
                "columns": columns,
                "inplace": inplace,
                "axis": axis,
                "copy": copy,
                "level": level,
                "errors": errors,
            },
            reason=reason,
        )

    def rolling(self, *args, **kwargs):
        from fireducks.pandas.rolling import Rolling

        ns = utils.decode_args(args, kwargs, pandas.DataFrame.rolling)
        reason = ns.is_not_default(["win_type"])
        if reason:
            return self._fallback_call("rolling", args, kwargs, reason=reason)
        return Rolling(self, args, kwargs)

    def round(self, decimals=0, *args, **kwargs):
        nv.validate_round(args, kwargs)

        if is_integer(decimals):
            return DataFrame._create(ir.round(self._value, int(decimals)))
        elif is_dict_like(decimals):
            cols, vals, reason = utils.get_key_value_tuples(
                decimals, ensure_int_val=True
            )
            if not reason:
                return DataFrame._create(
                    ir.column_wise_apply(self._value, "round", cols, vals)
                )
        else:
            reason = (
                "unsupported type for 'decimals' "
                f"parameter: {type(decimals).__name__}"
            )

        return self._fallback_call(
            "round", [decimals, *args], kwargs, reason=reason
        )

    def set_flags(self, *args, **kwargs):
        # Incompatibility: 023
        warnings.warn("set_flags is not supported", DeprecationWarning)
        return self._fallback_call("set_flags", args, kwargs)

    @deprecate_nonkeyword_arguments(
        version=None, allowed_args=["self", "keys"]
    )
    def set_index(self, *args, **kwargs):
        return self._set_index(*args, **kwargs)

    def _set_index(self, *args, as_axis=False, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.set_index)
        reason = None

        labels = arg.keys
        if isinstance(labels, list):
            if type(labels) is not list:  # FrozenList etc.
                labels = list(labels)
            if len(labels) and is_all_arraylike(labels):
                labels = MultiIndex.from_arrays(labels)

        as_new = isinstance(labels, (Series, Index, MultiIndex, np.ndarray))
        if not as_new and not irutils._is_scalar_or_list_of(
            labels, (str, int)
        ):
            reason = (
                "keys is neither an index-like nor a list of "
                "str, int or index-like"
            )

        if not reason and isinstance(labels, DatetimeIndex):
            # FIXME: frequency information is lost when converting
            # Index -> Series, hence falling back when frequency
            # information is available...
            if labels.freq is not None:
                reason = f"keys is a DatetimeIndex of frequency: {labels.freq}"

        if not reason and isinstance(labels, np.ndarray) and labels.ndim > 1:
            raise ValueError(
                "The parameter 'keys' may be a column key, one-dimensional "
                "array, or a list containing only valid column keys and "
                "one-dimensional arrays."
            )

        if as_axis and not as_new:  # should not occur
            reason = "setting axis(0) with existing column"

        if reason:
            return self._fallback_may_inplace(
                "set_index", args, kwargs, pos=3, reason=reason
            )

        drop = bool(arg.drop)
        to_append = bool(arg.append)
        verify_integrity = bool(arg.verify_integrity)
        label_names = []
        if as_new:
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
        else:
            keys = irutils.make_tuple_of_scalars(labels)
            newIndexColumns = Series([], dtype=np.float64)
        newIndexColumnNames = irutils.make_tuple_of_column_names(label_names)

        # the following boolean parameters are ordered alphabetically as
        # per the .td requirement.  Hence, be careful when changing the
        # order of:  as_axis, as_new, drop, to_append, verify_integrity
        value = ir.set_index(
            self._value,
            keys,
            newIndexColumns._value,
            newIndexColumnNames,
            as_axis,
            as_new,
            drop,
            to_append,
            verify_integrity,
        )
        return self._create_or_inplace(value, arg.inplace)

    @deprecate_nonkeyword_arguments(
        version=None, allowed_args=["self", "level"]
    )
    def reset_index(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.reset_index)
        arg.inplace = validate_bool_kwarg(arg.inplace, "inplace")
        arg.drop = validate_bool_kwarg(arg.drop, "drop")
        if arg.allow_duplicates is pandas_extensions.no_default:
            arg.allow_duplicates = False
        else:
            arg.allow_duplicates = validate_bool_kwarg(
                arg.allow_duplicates, "allow_duplicates"
            )

        # TODO GT #1689
        reason = arg.is_not_default(
            ["level", "col_level", "col_fill", "names"]
        )
        if reason:
            return self._fallback_may_inplace(
                "reset_index", args, kwargs, pos=2, reason=reason
            )

        value = ir.reset_index(
            self._value, arg.allow_duplicates, arg.drop, False
        )
        return self._create_or_inplace(value, arg.inplace)

    @property
    def shape(self) -> tuple[int, int]:
        return self._get_shape()

    @property
    def size(self) -> int:
        return np.prod(self.shape)

    @property
    def ndim(self) -> int:
        return 2

    @deprecate_nonkeyword_arguments(version=None, allowed_args=["self", "by"])
    def sort_values(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.sort_values)
        if not isinstance(arg.by, list):
            arg.by = [arg.by]
        arg.ascending = validate_ascending(arg.ascending)
        if not isinstance(arg.ascending, list):
            lst = len(arg.by) if isinstance(arg.by, list) else 1
            arg.ascending = [arg.ascending for _ in range(lst)]

        return self._sort_values(
            args,
            kwargs,
            decoded_args=arg,
            by=arg.by,
            ascending=arg.ascending,
            is_series=False,
        )

    def sort_index(self, *args, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.sort_index)
        arg.ascending = validate_ascending(arg.ascending)
        return self._sort_index(
            args,
            kwargs,
            decoded_args=arg,
            is_series=False,
        )

    def set_axis(self, *args, **kwargs):
        return self._set_axis(*args, **kwargs)

    def _set_axis(self, *args, _inplace_index_setter=False, **kwargs):
        arg = utils.decode_args(args, kwargs, pandas.DataFrame.set_axis)

        class_name = "DataFrame"
        reason, result = self._fallback_set_axis(
            args, kwargs, arg, class_name, _inplace_index_setter
        )
        if reason:
            return result

        labels = arg.labels
        inplace = (
            arg.inplace or _inplace_index_setter
            if utils._pd_version_under2
            else _inplace_index_setter
        )
        if arg.axis in ("index", 0):
            # set_index assumes
            #  - range values are existing column names
            #  - input labels are existing column names when they are of
            #    type list/tuple having irable scalars
            labels = (
                Series(labels)
                if isinstance(labels, range)
                or irutils._is_irable_scalar_arraylike(labels)
                else labels
            )
            return self._set_index(labels, inplace=inplace, as_axis=True)
        else:
            new_axis = irutils.make_tuple_of_column_names(labels)
            value = ir.rename(self._value, new_axis)
            return self._create_or_inplace(value, inplace)

    #
    # End of python API
    #

    def _build_binop(
        self, rhs, op_str: str, op_original: str, args, kwargs, inplace: bool
    ):
        logger.debug("DataFrame._build_binop: %s", op_str)

        def _fallback(reason, rhs_=rhs):
            fallback = self._get_fallback(inplace)
            return fallback(op_original, (rhs_,) + args, kwargs, reason=reason)

        arg = utils.decode_args(
            (rhs, *args), kwargs, getattr(pandas.DataFrame, op_original)
        )

        # Methods beginning with an underscore do not have 'axis', 'level',
        # and 'fill_value', arguments.
        if not hasattr(arg, "axis"):
            arg.axis = 1
        else:
            # pandas API doc does not menthon about axis=None, but
            # implementation supports it and pandas_tests also uses it.
            arg.axis = (
                self._get_axis_number(arg.axis) if arg.axis is not None else 1
            )

        rhs_t = type(rhs).__name__
        reason = None
        opc = None

        if hasattr(arg, "level") and arg.level is not None:
            reason = "level is not None"
        elif hasattr(arg, "fill_value") and arg.fill_value is not None:
            reason = "fill_value is not None"
        # TODO: use irable_scalar
        elif isinstance(
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
                datetime.time,
                np.datetime64,
                pandas.Timestamp,
                pandas.Timedelta,
            ),
        ):
            opc = get_binop_table_scalar(op_str)
            rhs = irutils.make_scalar(rhs)
        elif isinstance(rhs, _Scalar):
            opc = get_binop_table_scalar(op_str)
            rhs = rhs._value
        elif isinstance(rhs, Series):
            if arg.axis == 1:
                reason = "binop among Series with axis=1"
            else:
                opc = get_binop_table_vector(op_str)
                rhs = rhs._value
        elif isinstance(rhs, DataFrame):
            opc = get_binop_table_table(op_str)
            rhs = rhs._value

        if reason is None and opc is None:
            reason = f"unknown op: '{op_str}' on 'DataFrame' and '{rhs_t}'"

        if reason is not None:
            return _fallback(reason)

        op = fireducks.core.build_op(
            opc, [ir.TableType], [self._value, rhs], chaining=True
        )

        if inplace:
            self._rebind(op.outs[0], invalidate_cache=True)
            return self
        return DataFrame._create(op.outs[0])

    def _to_numpy_impl(self):
        if self._fireducks_meta.is_cached("values"):
            return self._fireducks_meta.get_cache("values"), None

        if not fireducks.core.get_ir_prop().has_metadata:
            reason = "no-metadata: dtype check is not possible"
            return None, reason

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
        ]
        col_dtypes = self._get_metadata()._get_raw_dtypes()
        is_numeric = len(col_dtypes) > 0 and np.all(
            [i in target_types for i in col_dtypes]
        )
        # fallback in case any non-numeric column exists
        if not is_numeric:
            reason = "with non-numeric column"
            return None, reason

        value = ir.to_numpy(self._value)
        # Workaround: For single column dataframe, dfkl's `ir.to_numpy`
        # returns 1-dim array as Series.to_numpy.
        np_arr = fireducks.core.evaluate([value])[0]
        ret = np_arr.reshape(len(np_arr), 1) if np_arr.ndim == 1 else np_arr

        # dfkl backend produces 'uint16' typed array for target column
        # of type 'float16'. Hence casting back at frontend side.
        exp_out_type = np.result_type(*col_dtypes)
        if ret.dtype != exp_out_type:
            ret = ret.astype(exp_out_type)
        self._fireducks_meta.set_cache("values", ret)
        return ret, None

    def to_numpy(self, *args, **kwargs):
        """Return a Numpy representation of the DataFrame."""
        logger.debug("DataFrame.to_numpy")
        if self._fireducks_meta.is_cached("pandas_object"):
            return self._fireducks_meta.get_cache("pandas_object").to_numpy(
                *args, **kwargs
            )

        ns = utils.decode_args(args, kwargs, pandas.DataFrame.to_numpy)
        reason = ns.is_not_default(
            [
                "dtype",
                "na_value",
                # Because ns.copy=False does not ensure no copy in pandas and
                # fireducks always copies, ns.copy can be ignored.
            ]
        )

        if reason is None:
            out, reason = self._to_numpy_impl()

        if reason is not None:
            reason = "DataFrame.to_numpy " + reason
            return self._fallback_call("to_numpy", args, kwargs, reason=reason)
        return out

    def __array__(self, *args, **kwargs):
        ns = utils.decode_args(args, kwargs, pandas.DataFrame.__array__)

        reason = ns.is_not_default(["dtype"])
        if reason is not None:
            return self._fallback_call(
                "__array__", args, kwargs, reason=reason
            )
        return self.to_numpy()

    def to_parquet(self, *args, **kwargs):
        from fireducks.pandas.io.parquet import to_parquet

        return to_parquet(self, *args, **kwargs)

    @property
    def values(self):
        """Return a Numpy representation of the DataFrame."""
        logger.debug("DataFrame.values")
        if self._fireducks_meta.is_cached("pandas_object"):
            return utils._wrap(
                self._fireducks_meta.get_cache("pandas_object").values
            )

        out, reason = self._to_numpy_impl()
        if reason is not None:
            reason = "DataFrame.values " + reason
            return utils.fallback_attr(
                self._unwrap,
                "values",
                reason=reason,
            )
        return out

    def value_counts(
        self,
        subset=None,
        normalize=False,
        sort=True,
        ascending=False,
        dropna=True,
    ):
        # according to pandas behavior. all true values would be treated
        # as true. e.g., sort=2 would be treated as sort=True
        normalize, sort, ascending, dropna = [
            bool(f) for f in (normalize, sort, ascending, dropna)
        ]
        target = self[subset] if subset is not None else self
        return Series._create(
            ir.value_counts(
                target._value, sort, ascending, dropna, normalize, False
            )
        )


def _to_pandas_frame_metadata(value, options=None):
    v0, v1 = ir.to_pandas_frame_metadata(value)
    df, meta = fireducks.core.evaluate([v0, v1], options=options)
    logger.debug("to_pandas_frame_metadata: meta=%s", meta)
    with tracing.scope(tracing.Level.VERBOSE, "to_pandas:metadata.apply"):
        return IRMetadataWrapper(meta).apply(df)
