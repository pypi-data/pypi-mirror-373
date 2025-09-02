# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from inspect import (
    Parameter as InspectParameter,
    signature as inspect_signature,
    unwrap as inspect_unwrap,
)
import functools
import logging
import types
import weakref

from collections import defaultdict
from collections.abc import Iterable, Mapping
from pandas.core.common import is_bool_indexer
from pandas.core.dtypes.common import is_integer, is_dict_like
from pandas.core.dtypes.inference import is_named_tuple
from pandas.core.groupby.generic import NamedAgg
import numpy as np
import pandas

import fireducks.core
import fireducks.pandas
import fireducks.fallback as ff
from fireducks import is_enterprise

__all__ = ["_pd_version_under2"]

import firefw as fire

from fireducks.pandas.binop import (
    COMPARISON_BINOPS,
    LOGICAL_BINOPS,
    REV_LOGICAL_BINOPS,
    INPLACE_LOGICAL_BINOPS,
)

from fireducks.irutils import (
    _is_str_list,
    _is_list_or_tuple_of,
    make_scalar,
    make_column_name,
    make_tuple_of_scalars,
    make_tuple_of_column_names,
    make_tuple_of_vector_or_scalar_of_str,
)

from fireducks.ir import (
    make_tuple_scalar,
    make_tuple_column_name,
)

logger = logging.getLogger(__name__)


def get_cal_name_mapper(field, new_locale=None):
    import locale
    import calendar

    defaults = {
        "day_name": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
        "month_name": [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
    }

    if new_locale is None:
        return dict(enumerate(defaults[field]))

    # to get current locale
    cur_locale = locale.setlocale(locale.LC_ALL)

    locale.setlocale(locale.LC_ALL, new_locale)
    ret = dict(enumerate(getattr(calendar, field)))

    # setting back to original locale
    locale.setlocale(locale.LC_ALL, cur_locale)
    return ret


def get_key_value_tuples(data, ensure_int_val=False):
    if not is_dict_like(data):
        return [], [], "input is not dict-like"

    try:
        cols = []
        vals = []
        for c, v in data.items():
            cols.append(make_column_name(c))
            if ensure_int_val:
                if not is_integer(v):
                    raise TypeError("Values must be integers")
                vals.append(make_scalar(int(v)))
            else:
                vals.append(make_scalar(v))
        cols = make_tuple_column_name(cols)
        vals = make_tuple_scalar(vals)
        return cols, vals, None
    except Exception as e:
        return [], [], f"error in parsing input dict: {e}"


def is_notebook_like():
    try:
        known_notebooks = ["ipykernel.zmqshell", "google.colab._shell"]
        return get_ipython().__class__.__module__ in known_notebooks
    except NameError:
        return False


def is_interactive_terminal():
    try:
        return (
            "terminal.interactiveshell" in get_ipython().__class__.__module__
        )
    except NameError:
        return False


def is_pandas_version_under_v2():
    from pandas.util.version import Version

    pdlv = Version(Version(pandas.__version__).base_version)
    return pdlv < Version("2")


_pd_version_under2 = is_pandas_version_under_v2()


def _is_str_list_or_index(obj):
    if isinstance(obj, fireducks.pandas.wrappers.Index):
        obj = list(obj)
    return _is_str_list(obj)


# Map from dtypes in the frontend and dtypes in IR.
#
# Since pandas backend passes dtypes in IR directly to pandas, those should be
# acceptable by pandas.
#
# If you add type here, you should update dfkl backend.
_supported_dtypes = {
    "category": "category",
    "float": "float64",
    "float32": "float32",
    "float64": "float64",
    "bool": "bool",
    "int8": "int8",
    "uint8": "uint8",
    "int": "int64",
    "int32": "int32",
    "int64": "int64",
    "str": "str",
    "string": "str",
    "datetime64": "datetime64[ns]",
    "datetime64[ns]": "datetime64[ns]",
    "datetime64[ms]": "datetime64[ms]",
    "datetime64[us]": "datetime64[us]",
    "datetime64[s]": "datetime64[s]",
    np.int8: "int8",
    np.bool_: "bool",
    np.uint8: "uint8",
    np.int32: "int32",
    np.int64: "int64",
    np.float32: "float32",
    np.float64: "float64",
    float: "float64",
    int: "int64",
    bool: "bool",
    str: "str",
}

# only supported for pandas 1x
if _pd_version_under2:
    _supported_dtypes[np.datetime64] = "datetime64[ns]"


def is_supported_dtype(dtype):
    return dtype in _supported_dtypes.keys()


def is_supported_dtypes(dtypes):
    return all([is_supported_dtype(t) for t in dtypes])


def to_supported_dtype(dtype):
    return _supported_dtypes[dtype]


def _is_index_like(indices):
    from fireducks.pandas import Index

    known_index_list = (Index, range)
    return (
        isinstance(indices, known_index_list)
        or _is_list_or_tuple_of(indices, (int, float, str))
        or (isinstance(indices, np.ndarray) and indices.ndim == 1)
    )


def _is_numeric_index_like(indices):
    from fireducks.pandas import RangeIndex

    known_numeric_index_list = (RangeIndex, range)
    if _pd_version_under2:
        from fireducks.pandas import NumericIndex, Int64Index, UInt64Index

        known_numeric_index_list += (NumericIndex, Int64Index, UInt64Index)

    return (
        isinstance(indices, known_numeric_index_list)
        or _is_list_or_tuple_of(indices, int)  # includes bool
        or (
            isinstance(indices, np.ndarray)
            and indices.ndim == 1
            and indices.dtype in ["int16", "int32", "int64", "bool"]
        )
    )


def fallback_attr(
    fallbacker, name, reason=None, *, stacklevel=0, wrap_func=None
):
    wrap_func = wrap_func or _wrap
    options = fireducks.core.get_fireducks_options()
    return ff.fallback_attr(
        fallbacker,
        name,
        reason,
        stacklevel=stacklevel,
        wrap_func=wrap_func,
        unwrap_func=_unwrap,
        log_lineno=options.fallback_lineno,
        warn_fallback=options.warn_fallback,
    )


def fallback_call(
    fallbacker, method, args=None, kwargs=None, *, reason=None, stacklevel=6
):
    """
    Fallback a method call

    After resolving attribute, call it with arguments.
    """
    options = fireducks.core.get_fireducks_options()
    return ff.fallback_call(
        fallbacker,
        method,
        args,
        kwargs,
        reason=reason,
        stacklevel=stacklevel,
        wrap_func=_wrap,
        unwrap_func=_unwrap,
        log_lineno=options.fallback_lineno,
        warn_fallback=options.warn_fallback,
    )


# TODO: Experimental
# Current implementation returns bool when value is defined by logical binop on
# vector.
def _infer_dtype(value: fire.Value):
    # GT: 4138#issuecomment-116988
    # definition is no longer available once value is evaluated
    if value.is_available():
        return None

    opcode = value.get_def().opcode
    logger.debug("_infer_dtype: opcode=%s", opcode.name)
    logicals = [
        f"fireducks.{op}.vector"
        for op in COMPARISON_BINOPS
        + LOGICAL_BINOPS
        + REV_LOGICAL_BINOPS
        + INPLACE_LOGICAL_BINOPS
    ] + [
        "fireducks.between",
        "fireducks.isin",
        "fireducks.isnull",
        "fireducks.str_contains",
        "fireducks.str_endswith",
        "fireducks.str_startswith",
        "fireducks.str_unary_bool_returning_method",
    ]
    for op in logicals:
        if op in opcode.name:
            return np.dtype(bool)

    # TODO: and,or,xor also should infer with inputs
    if opcode.name == "fireducks.invert":
        return _infer_dtype(value.get_def().ins[0])

    return None  # unknown


def _deduce_dtype(key):
    assert isinstance(key, fireducks.pandas.Series)

    dtype = _infer_dtype(key._value)  # infer from OPCODE
    logger.debug("inferred dtype: %s", dtype)

    return key.dtype if dtype is None else dtype


def is_filter_like(key):
    ignore_index = False
    if (
        isinstance(key, np.ndarray)
        and key.dtype == np.bool_
        and (key.ndim == 1 or (key.ndim == 2 and key.shape[1] == 1))
    ):
        ignore_index = True
        key = fireducks.pandas.Series(key.ravel())

    if isinstance(key, list) and is_bool_indexer(key):
        ignore_index = True
        key = fireducks.pandas.Series(key)

    if isinstance(key, fireducks.pandas.Series):
        dtype = _deduce_dtype(key)
        return dtype is not None and dtype == bool, key, ignore_index

    return False, key, ignore_index


def is_supported_unary_method_name(ufunc_name: str):
    supported_unary_methods = ["absolute"]
    if is_enterprise:
        for m in ["sin", "cos", "tan"]:
            supported_unary_methods += [m, f"arc{m}", f"{m}h", f"arc{m}h"]
    return ufunc_name in supported_unary_methods


#
# Type utils
#


def _is_list_like_of(obj, types):
    return pandas.api.types.is_list_like(obj) and all(
        [isinstance(x, types) for x in obj]
    )


def _is_fireducks_class(cls):
    return cls is fireducks.pandas.DataFrame or cls is fireducks.pandas.Series


def _hasattr(obj, name):
    """Check if obj has name without calling obj.__getattr__

    Builtin function `hasattr` calls obj.__getattr__ when obj does not have
    name. In fireducks it may fallback to pandas. This method can be used when
    you just want to know if obj has name.
    """
    try:
        object.__getattribute__(obj, name)
        return True
    except AttributeError:
        pass
    return False


__pandas_to_fireducks_dict = None


def _fireducks_class(pandas_class):
    global __pandas_to_fireducks_dict
    if __pandas_to_fireducks_dict is None:
        __pandas_to_fireducks_dict = {
            # fireducks.pandas classes
            "Categorical": fireducks.pandas.Categorical,
            "CategoricalIndex": fireducks.pandas.CategoricalIndex,
            "DataFrame": fireducks.pandas.DataFrame,
            "DatetimeIndex": fireducks.pandas.DatetimeIndex,
            "GroupByNthSelector": PandasCallableWrapper,
            "Index": fireducks.pandas.Index,
            "IntervalIndex": fireducks.pandas.IntervalIndex,
            "MultiIndex": fireducks.pandas.MultiIndex,
            "PeriodIndex": fireducks.pandas.PeriodIndex,
            "RangeIndex": fireducks.pandas.RangeIndex,
            "Series": fireducks.pandas.Series,
            "TimedeltaIndex": fireducks.pandas.TimedeltaIndex,
            # fireducks.PandasWrapper
            "BaseGrouper": PandasWrapper,
            "CategoricalAccessor": PandasWrapper,
            "DataFrameGroupBy": PandasWrapper,
            "DatetimeIndexResampler": PandasWrapper,
            "DatetimeIndexResamplerGroupby": PandasWrapper,
            "PeriodIndexResampler": PandasWrapper,
            "PeriodIndexResamplerGroupby": PandasWrapper,
            "TimedeltaIndexResampler": PandasWrapper,
            "TimedeltaIndexResamplerGroupby": PandasWrapper,
            "DatetimeProperties": PandasWrapper,
            "Grouping": PandasWrapper,
            "PrettyDict": PandasWrapper,
        }
        if _pd_version_under2:
            # The following classes do not exist in pandas2.2.
            __pandas_to_fireducks_dict.update(
                NumericIndex=fireducks.pandas.NumericIndex,
                Int64Index=fireducks.pandas.Int64Index,
                UInt64Index=fireducks.pandas.UInt64Index,
                Float64Index=fireducks.pandas.Float64Index,
            )

    module_name = pandas_class.__module__
    if module_name == "builtins":
        if pandas_class.__name__ == "generator":
            return PandasGeneratorWrapper
    elif module_name == "pandas" or module_name.startswith("pandas."):
        if pandas_class.__name__ in __pandas_to_fireducks_dict:
            return __pandas_to_fireducks_dict[pandas_class.__name__]
    elif module_name.startswith("xarray.") and pandas_class.__name__ in [
        "DataArray",
        "Dataset",
    ]:
        return PandasWrapper

    return pandas_class


def _pandas_class(fireducks_class):
    if fireducks_class is fireducks.pandas.DataFrame:
        return pandas.DataFrame
    elif fireducks_class is fireducks.pandas.Series:
        return pandas.Series
    raise RuntimeError(f"Unknown fireducks class: {fireducks_class}")


#
# Utils
#


def _is_default(default, given):
    """
    This function is designed to check whether the given arguments in
    DecodedArgs match their default values.

    GT #2526: Index objects may return Series when compared with ==,
    which can cause issues in if statements. This function ensures robust
    comparison for default argument detection.
    """
    if default is None and given is None:
        return True

    # Check if one is Iterable and the other is not
    # Note: strings and bytes are Iterable but treated as non-Iterable here
    left_is_iterable = isinstance(default, Iterable) and not isinstance(
        default, (str, bytes)
    )
    right_is_iterable = isinstance(given, Iterable) and not isinstance(
        given, (str, bytes)
    )

    if left_is_iterable != right_is_iterable:
        return False

    # Special handling for list/tuple comparison: [1,2,3] == (1,2,3) is False in Python
    # but for our purposes we want it to be True if their elements are equal
    if (
        left_is_iterable
        and right_is_iterable
        and type(default) != type(given)
        and isinstance(default, (list, tuple))
        and isinstance(given, (list, tuple))
    ):
        if len(default) != len(given):
            return False
        return all(_is_default(l, r) for l, r in zip(default, given))

    eq = default == given
    return np.all(eq) if isinstance(eq, Iterable) else eq


class DecodedArgs:
    def __init__(self, defaults, arguments):
        self._defaults = defaults
        for k, v in arguments.items():
            if k != "self":
                setattr(self, k, v)

    def is_not_default(self, check_list=[], exclude=[]):
        if not check_list:
            exclude += ["self"]
            check_list = set(self._defaults.keys()) - set(exclude)

        for arg in check_list:
            if arg in self._defaults:
                default = self._defaults[arg]
                arg_val = getattr(self, arg)
                if _is_default(default, arg_val):
                    continue
                return f"{arg} is not {default}"
            else:
                return f"{arg} is not in kwargs"
        return None


# decode_args() cache
_decode_args_cache = {}


def decode_args(fargs, fkwargs, pandas_func):
    """Decode real arguments to formal arguments via signature

    This function decodes args according to the signature of pandas_func.

    Parameters
    ----------
    fargs: args to decode
    fkwargs: kwargs to decode
    pandas_func: pandas function to get signature
    """

    global _decode_args_cache
    pandas_sig = _decode_args_cache.get(pandas_func, None)
    if pandas_sig is None:
        # Follow __wrappped__ attribute created by functools.wraps
        wrapped = inspect_unwrap(pandas_func)
        pandas_sig = inspect_signature(wrapped)
        _decode_args_cache[pandas_func] = pandas_sig

    if "self" in pandas_sig.parameters:
        # bind self to None
        bound = pandas_sig.bind(None, *fargs, **fkwargs)
    else:
        bound = pandas_sig.bind(*fargs, **fkwargs)

    bound.apply_defaults()
    defaults = {}
    for k, v in pandas_sig.parameters.items():
        if v.kind == InspectParameter.VAR_POSITIONAL and v.default is v.empty:
            defaults[k] = ()
        elif v.kind == InspectParameter.VAR_KEYWORD and v.default is v.empty:
            defaults[k] = {}
        else:
            defaults[k] = v.default

    return DecodedArgs(defaults, bound.arguments)


#
# Utils for fallback
#


def _setup_PandasWrapper(cls):
    def wrap_method(method_name: str):
        @functools.wraps(method_name)
        def wrapped_method(self, *args, **kwargs):
            attr = getattr(self._pandas_obj, method_name)
            ret = attr(*_unwrap(args), **_unwrap(kwargs))
            return _wrap(ret)

        return wrapped_method

    methods = [
        # operator
        "__add__",
        "__and__",
        "__contains__",
        "__div__",
        "__divmod__",
        "__eq__",
        "__floordiv__",
        "__ge__",
        "__gt__",
        "__iadd__",
        "__iand__",
        "__idiv__",
        "__idivmod__",
        "__ifloordiv__",
        "__ilshift__",
        "__imod__",
        "__imul__",
        "__invert__",
        "__ior__",
        "__ipow__",
        "__irshift__",
        "__isub__",
        "__itruediv__",
        "__ixor__",
        "__le__",
        "__lshift__",
        "__lt__",
        "__mod__",
        "__mul__",
        "__ne__",
        "__neg__",
        "__or__",
        "__pow__",
        "__radd__",
        "__rand__",
        "__rdiv__",
        "__rdivmod__",
        "__rfloorfiv__",
        "__rlshift__",
        "__rmod__",
        "__rmul__",
        "__ror__",
        "__rpow__",
        "__rrshift__",
        "__rshift__",
        "__rsub__",
        "__rtruediv__",
        "__rxor__",
        "__sub__",
        "__truediv__",
        "__xor__",
        # others
        "__dir__",
        "__iter__",
        "__repr__",
    ]  # yapf: disable

    for method_name in methods:
        wrapped = wrap_method(method_name)
        type.__setattr__(cls, method_name, wrapped)
    return cls


@_setup_PandasWrapper
class PandasWrapper:
    """PandasWrapper wraps a pandas object.

    All attribute access are redirect to the wrapped pandas object, and
    returned value is wrapped to a fireducks object.
    """

    def __init__(self, _pandas_obj=None, class_=None):
        assert _pandas_obj is not None
        object.__setattr__(self, "_pandas_obj", _pandas_obj)

        class_ = class_ or type(_pandas_obj)
        object.__setattr__(self, "_wrapped_class", class_)

        # Add wrapper object reference to pandas object
        try:
            object.__setattr__(
                _pandas_obj, "_fireducks_wrapper", weakref.ref(self)
            )
        except AttributeError:
            # Returns AttributeError if _pandas_obj has __slots__.
            pass

    @property
    def __class__(self):
        return self._wrapped_class

    def __bool__(self):
        return bool(self._pandas_obj)

    def __getattr__(self, name):
        reason = (
            f"{type(self._pandas_obj).__name__}.__getattr__ for {name}"
            " is called"
        )
        return fallback_attr(self._unwrap, name, reason=reason)

    def __setattr__(self, name, value):
        setattr(self._pandas_obj, name, value)

    def __getitem__(self, key):
        return _wrap(self._pandas_obj[key])

    def __setitem__(self, key, value):
        self._pandas_obj[key] = _unwrap(value)

    def __len__(self):
        return len(self._pandas_obj)

    def _unwrap(self, reason=None):
        return self._pandas_obj


class PandasCallableWrapper(PandasWrapper):
    def __call__(self, *args, **kwargs):
        return _wrap(self._pandas_obj(*args, **kwargs))


class PandasClassWrapperMetaclass(type):
    def __getattr__(cls, name):
        def _unwrap(reason=None):
            return cls._pandas_cls

        reason = f"{cls._pandas_cls.__name__}.__getattr__ for {name} is called"
        return fallback_attr(_unwrap, name, reason=reason)


class PandasClassWrapper(PandasWrapper, metaclass=PandasClassWrapperMetaclass):
    def __init__(self, *args, _pandas_obj=None, **kwargs):
        if _pandas_obj is None:
            _pandas_obj = self._pandas_cls(*_unwrap(args), **_unwrap(kwargs))
        super().__init__(_pandas_obj=_pandas_obj)

    @property
    def __class__(self):
        return self._pandas_cls


class PandasGeneratorWrapper:
    def __init__(self, _pandas_obj=None):
        assert _pandas_obj is not None
        object.__setattr__(self, "_pandas_obj", _pandas_obj)

    def __iter__(self):
        self._pandas_obj = iter(self._pandas_obj)
        return self

    def __next__(self):
        return _wrap(next(self._pandas_obj))

    def _unwrap(self, reason=None):
        raise NotImplementedError()


def install_wrapper(cls, name, wrapper, parent_class=None, override=False):
    """
    Set `cls`'s attribute `name` to `wrapper` as it looks like `name` of
    `parent_class`
    """

    if not override and _hasattr(cls, name):
        logger.debug(
            "install_wrapper: skip %s.%s to prevent override",
            cls.__name__,
            name,
        )
        return

    if parent_class is not None:
        # At the moment, we support only wrapper of FunctionType
        assert isinstance(wrapper, types.FunctionType)

        wrapped = getattr(parent_class, name)
        logger.debug(
            "install_wrapper: %s.%s.%s (wrapped: %s)",
            cls.__module__,
            cls.__name__,
            name,
            wrapped,
        )
        if isinstance(wrapped, types.FunctionType):
            functools.update_wrapper(wrapper, wrapped)
        elif isinstance(wrapped, property):
            # Expect that wrapped.fget returns callable
            wrapper.__name__ = name
            wrapper.__qualname__ = f"{parent_class.__name__}.{name}"

    type.__setattr__(cls, name, wrapper)


def install_fallback(cls, name, parent=None, override=False):
    """
    Install fallback to `cls` on name.
    """

    def wrapper(self, *args, **kwargs):
        reason = (
            "Installed fallback wrapper"
            f" for {cls.__name__}.{name} is called"
        )
        assert hasattr(self, "_unwrap")
        return fallback_call(
            self._unwrap,
            name,
            args,
            kwargs,
            reason=reason,
            stacklevel=6,
        )

    install_wrapper(cls, name, wrapper, parent, override)


def install_fallbacks(cls, names, parent=None, override=False):
    for name in names:
        install_fallback(cls, name, parent, override)


def _unwrap(obj, *, reason=None, recursive=True):
    if isinstance(obj, (type, bool, int, float, str, type(None))):
        return obj

    if hasattr(obj, "_unwrap"):
        return obj._unwrap(reason=reason)

    if not recursive:
        return obj

    if isinstance(obj, list):
        return [_unwrap(x, reason=reason) for x in obj]

    # Do not unwrap NamedAgg to prevent it from converting to tuple. GT #843
    if isinstance(obj, NamedAgg):
        return obj

    if isinstance(obj, tuple):
        if is_named_tuple(obj) and hasattr(obj, "_make"):
            # namedtuple
            return obj._make([_unwrap(x, reason=reason) for x in obj])
        else:
            # tuple
            return tuple(_unwrap(x, reason=reason) for x in obj)

    if isinstance(obj, Mapping):
        dic = {_unwrap(k): _unwrap(v, reason=reason) for k, v in obj.items()}
        if hasattr(obj, "default_factory"):
            return defaultdict(obj.default_factory, dic)
        return dic

    return obj


class ReadOnlyAccessor:
    """ReadOnlyAccessor wraps an accessor of pandas.

    In pandas, an accessor is created from DataFrame or Series. An accessor may
    have methods or attributes to return a subset of the DataFrame/Series from
    which it is created. It may also have methods to update the
    DataFrame/Series. Examples are _LocIndexer create by DataFrame.loc,
    StringMethods created from Series.str.

    ReadOnlyAccessor wraps such pandas's accessor to wrap pandas's
    DataFrame/Series returned from it to fireducks's one. ReadOnlyAccessor
    supports pandas's accessor which has only read access. That means it does
    not support update of the dataframe/series through an accessor.

    Be careful to add methods such as `__setattr__` and `__setitem__`. It may
    update the original object In that case, simple fallback does not work. See
    `DataFrame._fallback_mutating_method`.
    """

    def _unwrap(self, reason):
        raise NotImplementedError()

    def __getattr__(self, name):
        reason = "ReadOnlyAccessor.__getattr__ is called"
        return fallback_attr(self._unwrap, name, reason)


def _wrap(obj):
    from fireducks.pandas.api import from_pandas

    obj_type = type(obj)
    logger.debug("_wrap: %s", obj_type)
    if isinstance(obj, pandas.DataFrame) or isinstance(obj, pandas.Series):
        return from_pandas(obj)

    assert not isinstance(obj, PandasWrapper)

    if hasattr(obj, "_fireducks_wrapper"):
        # Return wrapper if this pandas object has a valid wrapper reference.
        # Make sure the reference is not NONE, because the reference is a
        # weakref.
        wrapper_obj = obj._fireducks_wrapper()
        if wrapper_obj is not None:
            return wrapper_obj

    wrapper_class = _fireducks_class(obj_type)
    if wrapper_class is not obj_type:
        return wrapper_class(_pandas_obj=obj)

    if isinstance(obj, list):
        # Call the constructor so that classes that inherit from list can also
        # be supported.  - e.g. DataFrame.index.names returns
        # pandas.core.indexes.frozen.FrozenList which inherits from list.
        return obj_type(_wrap(x) for x in obj)
    if isinstance(obj, tuple):
        return tuple(_wrap(x) for x in obj)

    if isinstance(obj, dict):
        return {k: _wrap(v) for k, v in obj.items()}

    if isinstance(obj, type):
        return obj

    return obj


def _get_pandas_module(reason=None):
    return pandas


def is_int_or_none_slice(s: slice) -> bool:
    return all(
        [(isinstance(x, int) or x is None) for x in [s.start, s.stop, s.step]]
    )


# used from cudf_backend.cc
def get_drop_targets(c1, c2, prefix_sep="_"):
    """
    c1: ["A", "B", "C", "D"]
    when columns C and D would be encoded as follows

    c2: ["A", "B", "C_1", "C_2", "C_3", "D_x", "D_y"]

    For drop_first=True, we need c2 as: ["A", "B", "C_2", "C_3", "D_y"]
    this method returns target columns to be dropped, i.e., ["C_1", "D_x"]
    """
    encoded_col = [c for c in c1 if c not in c2]
    targets = []
    for e in encoded_col:
        for c in c2:
            if c.startswith(e + prefix_sep):
                targets.append(c)
                break
    return targets


def wrap_module_function(funcname, *args, **kwargs):
    """
    funcname is function name as string of cudf or pandas module.
    Mostly same as _fast_slow_function_call of cuDF.
    Since we are not under module_accelerator, manually set fast/slow func
    We assume that the result is DataFrame or Series
    """
    import cudf
    import pandas
    from cudf.pandas.fast_slow_proxy import _fast_arg, _slow_arg
    import cudf.pandas._wrappers.pandas

    fastfunc = getattr(cudf, funcname)
    slowfunc = getattr(pandas, funcname)
    try:
        fast_args, fast_kwargs = _fast_arg(args), _fast_arg(kwargs)
        result = fastfunc(*fast_args, **fast_kwargs)
        if result is NotImplemented:
            # try slow path
            raise Exception()
    except Exception:
        slow_args, slow_kwargs = _slow_arg(args), _slow_arg(kwargs)
        result = slowfunc(*slow_args, **slow_kwargs)
    if isinstance(result, pandas.DataFrame) or isinstance(
        result, cudf.DataFrame
    ):
        ret = cudf.pandas._wrappers.pandas.DataFrame._fsproxy_wrap(
            result, None
        )
    elif isinstance(result, pandas.Series) or isinstance(result, cudf.Series):
        ret = cudf.pandas._wrappers.pandas.Series._fsproxy_wrap(result, None)
    else:
        raise RuntimeError("Neither DataFrame nor Series is created")
    return ret


def wrap_module_function_for_pandas(funcname, *args, **kwargs):
    """
    pandas backend version of wrap_module_function.
    This is needed in get/set_pd_function_caller_provider in kernels.cc
    """
    import pandas

    func = getattr(pandas, funcname)
    return func(*args, **kwargs)


def wrap_module_function_for_cudf(funcname, *args, **kwargs):
    """
    raw cudf backend version of wrap_module_function.
    This is needed in get/set_pd_function_caller_provider in kernels.cc
    """
    import cudf

    func = getattr(cudf, funcname)
    return func(*args, **kwargs)


# mostly same as create_metadata in frame.py; modified for cudf backend
def create_metadata_cudf(df, is_wrapped):
    import pandas
    import cudf
    import cudf.pandas._wrappers.pandas
    from datetime import datetime
    from fireducks.fireducks_ext import (
        Metadata,
        ColumnMetadata,
        Scalar,
        ColumnName,
    )

    def my_isinstance(obj, type, has_cudf):
        if isinstance(obj, getattr(pandas, type)) or (
            has_cudf and isinstance(obj, getattr(cudf, type))
        ):
            return True
        elif is_wrapped and isinstance(
            obj, getattr(cudf.pandas._wrappers.pandas, type)
        ):
            return True
        else:
            return False

    def is_wrapped_instance(obj, type):
        if is_wrapped and isinstance(
            obj, getattr(cudf.pandas._wrappers.pandas, type)
        ):
            return True
        else:
            return False

    def make_scalar(name):
        if isinstance(name, datetime):
            return Scalar.from_datetime(name)
        elif my_isinstance(name, "Timestamp", False):
            if is_wrapped_instance(name, "Timestamp"):
                return Scalar.from_timestamp(name._fsproxy_fast_to_slow())
            else:
                return Scalar.from_timestamp(name)
        elif my_isinstance(name, "Timedelta", False):
            if is_wrapped_instance(name, "Timedelta"):
                return Scalar.from_timedelta(name._fsproxy_fast_to_slow())
            else:
                return Scalar.from_timedelta(name)
        else:
            return Scalar(name)

    def to_column_name(name, isMulti):
        if isinstance(name, (frozenset, tuple)):
            scalars = [make_scalar(e) for e in name]
            return (
                ColumnName.MultiFromScalars(scalars)
                if isMulti
                else ColumnName.SingleFromScalars(scalars)
            )

        return ColumnName.Single(make_scalar(name))

    def to_column_index_name(index, isMulti):
        if isMulti:
            return ColumnName.MultiFromScalars(
                [make_scalar(e) for e in index.names]
            )
        else:
            return ColumnName.Single(make_scalar(index.name))

    if my_isinstance(df, "DataFrame", True):
        index = df.columns
    elif my_isinstance(df, "Series", True):
        columns = [ColumnMetadata(to_column_name(df.name, False))]
        column_index_names = ColumnName.Single(make_scalar(None))
        return Metadata(columns, column_index_names, False)
    else:
        return None

    isMulti = my_isinstance(index, "MultiIndex", True)
    column_names = [to_column_name(name, isMulti) for name in index]
    columns = [ColumnMetadata(name) for name in column_names]
    column_index_names = to_column_index_name(index, isMulti)
    return Metadata(
        columns,
        column_index_names,
        my_isinstance(df.index, "MultiIndex", True),
    )


def get_unique_column_name(column_names, validate=True):
    """
    DESC: return a unique column name which is possibly not
          a part of input "column_names"
    PARAMS: column_names:  an array-like containing the existing names of columns
            validate: whether to check the generated name belongs to the existing names.
                      if False "column_names" will be ignored.
    RETURN: String containing the resultant unique name
    """
    n = 0
    prefix = "__fireducks_tmp_col__"
    name = prefix + str(n)
    if validate:
        column_set = set(column_names)
        while name in column_set:
            n += 1
            name = prefix + str(n)
    return name
