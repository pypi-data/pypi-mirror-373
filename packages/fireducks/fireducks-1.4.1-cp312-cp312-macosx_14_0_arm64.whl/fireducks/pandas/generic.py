# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import os
import numpy as np
import pandas
import pandas.api.extensions as pandas_extensions
from pandas.core.dtypes.common import is_dict_like
from pandas.compat.numpy import function as nv
from pandas.util._validators import validate_bool_kwarg
from pandas.util._decorators import deprecate_nonkeyword_arguments
import pandas._libs.lib as pandas_lib
from pandas.core.dtypes.common import is_float

from fireducks import ir, irutils

from fireducks.pandas.indexing import _LocIndexer, _IlocIndexer
from fireducks.pandas.binop import is_inplace_binop
from fireducks.pandas.wrappers import Index, MultiIndex, DatetimeIndex
import fireducks.core
import fireducks.pandas
import fireducks.pandas.utils as utils
from fireducks.pandas.metadata import IRMetadataWrapper
import firefw as fire

from typing import Union
import functools
import logging
import operator
import types
import warnings

# import warnings

logger = logging.getLogger(__name__)


class FireDucksPandasCompatMetaclass(type):
    def __getattr__(cls, name):
        logger.debug(
            "FireDucksPandasCompatMetaclass.__getattr__: name=%s", name
        )

        def unwrap(reason):
            return utils._pandas_class(cls)

        return utils.fallback_attr(unwrap, name)

    # __setattr__ is not defined here because we have no attribute which should
    # be set to pandas class. As far as we know, class attributes which are set
    # by a user is "_metadata" and "__finalize__", but those are set to
    # fireducks class.


class FireDucksObject:
    def __init__(self, value: fire.Value):
        self._value = value
        value.bind(self)

    def _rebind(self, value):
        """Rebind self to value."""
        value.bind(self._value.unbind())
        self._value = value

        if fireducks.core.get_fireducks_options().benchmark_mode:
            self._evaluate()

    # fireducks method

    def _evaluate(self, options=None, _logger=None):
        logger.debug("FireDucksObject._evaluate")
        fireducks.core.evaluate([self._value], options, _logger)
        return self


class FireDucksMetadata:
    """Metadata."""

    def __init__(self, *, hint=None):
        self.hint = hint
        self._cache = {
            "pandas_object": None,
            "index": None,
            "shape": None,
            "dtypes": None,
            "values": None,
            "ir_metadata_wrapper": None,
        }
        self._internal_referrers = []

    def add_internal_referrer(self, referrer):
        """Be careful that adding referrer to internal referrer also increases
        refcount of the referrer!"""
        logger.debug("add_extra_internal_referrer")
        self._internal_referrers.append(referrer)

    def get_internal_referrers(self):
        return self._internal_referrers

    def invalidate_cache(self):
        logger.debug("invalidate_cache")
        self._cache = {
            "pandas_object": None,
            "index": None,
            "shape": None,
            "dtypes": None,
            "values": None,
            "ir_metadata_wrapper": None,
        }

    def invalidate_hint(self):
        self.hint = None

    def get_cache(self, attr):
        return self._cache[attr]

    def set_cache(self, attr, value):
        assert attr in self._cache.keys()
        if attr == "pandas_object":
            # when a pandas_object is cached, any inplace modification in the
            # cached pandas_object caused by fallback_mutating_method() etc.
            # needs to be reflected in the cached shape, index etc. as well.
            # Therefore, invalidating other attributes for this case.
            self.invalidate_cache()
        else:
            # DataFrame attributes (shape, index, etc.) should be cached,
            # only when 'pandas_object' is not cached.
            assert not self.is_cached("pandas_object")
        logger.debug(f"set_cache_for_{attr}: %x", id(value))
        self._cache[attr] = value

    def is_cached(self, attr):
        return self.get_cache(attr) is not None


def _install_fallback_mutating_method(cls, name):
    def wrapper(self, *args, **kwargs):
        reason = f"{name} (mutating method) is not yet implemented"
        return self._fallback_mutating_method(
            name, args, kwargs, reason=reason
        )

    type.__setattr__(cls, name, wrapper)


def _make_aggregate_wrapper(pandas_func, name):
    @functools.wraps(pandas_func)
    def wrapper(self, *args, **kwargs):
        return self._agg_func(name, args, kwargs)

    return wrapper


def _install_aggregators(cls, pandas_cls):
    aggs = [
        # methods
        "all",
        "any",
        "max",
        "min",
        "mean",
        "var",
        "std",
        "sum",
        "skew",
        "kurt",
        "count",
        "median",
        "nunique",
    ]

    for name in aggs:
        pandas_func = getattr(pandas_cls, name)
        type.__setattr__(cls, name, _make_aggregate_wrapper(pandas_func, name))

    type.__setattr__(cls, "kurtosis", getattr(cls, "kurt"))


def _make_binop_wrapper(pandas_cls, op):
    pandas_func = getattr(pandas_cls, op)
    realop = op.replace("_", "")

    @functools.wraps(pandas_func)
    def wrapper(self, other, *args, **kwargs):
        # As pandas we do not allow __op__ takes additional arguments
        if op.startswith("__") and args:
            raise TypeError("takes 2 positional arguments but 3 were given")

        # FireDucks IR does not have inplace binops. It will be implemented
        # as out-of-place binop and rebind
        inplace = is_inplace_binop(realop)
        op_for_ir = realop[1:] if inplace else realop

        return self._build_binop(
            other, op_for_ir, op, args, kwargs, inplace=inplace
        )

    return wrapper


def _install_binops(cls, pandas_cls):
    """
    Install binary operator methods (like __add__, __sub__, etc.) on the class,
    wrapping the corresponding pandas methods for docstring and signature.
    """

    binops = [
        # methods
        "add",
        "floordiv",
        "mod",
        "mul",
        "pow",
        "sub",
        "truediv",
        "radd",
        "rfloordiv",
        "rmod",
        "rmul",
        "rpow",
        "rsub",
        "rtruediv",
        # operators
        "__add__",
        "__floordiv__",
        "__mod__",
        "__mul__",
        "__pow__",
        "__sub__",
        "__truediv__",
        "__iadd__",
        "__ifloordiv__",
        "__imod__",
        "__imul__",
        "__ipow__",
        "__isub__",
        "__itruediv__",
        "__radd__",
        "__rfloordiv__",
        "__rmod__",
        "__rmul__",
        "__rpow__",
        "__rsub__",
        "__rtruediv__",
        # Comparison
        # TODO: Pandas has difference among comparison functions and operators
        # such as `eq` and `==` (`__eq__`). But we do not know much of this
        # difference, our IR supports only operators at the moment.
        # 'eq', 'ge', 'gt', 'le', 'lt', 'ne',
        "__eq__",
        "__ge__",
        "__gt__",
        "__le__",
        "__lt__",
        "__ne__",
        # logical
        "__and__",
        "__or__",
        "__xor__",
        "__iand__",
        "__ior__",
        "__ixor__",
        "__rand__",
        "__ror__",
        "__rxor__",
    ]  # yapf: disable

    for op in binops:
        type.__setattr__(cls, op, _make_binop_wrapper(pandas_cls, op))

    type.__setattr__(cls, "div", getattr(cls, "truediv"))
    type.__setattr__(cls, "rdiv", getattr(cls, "rtruediv"))
    type.__setattr__(cls, "__div__", getattr(cls, "truediv"))
    type.__setattr__(cls, "__idiv__", getattr(cls, "__itruediv__"))


def _install_unary_op_fallbacks(cls, parent):
    # Explicit fallbacks are required since __getattr__ does not hook special
    # methods
    methods = [
        # unary ops
        "__bool__",
        "__iter__",
        "__pos__",
    ]
    utils.install_fallbacks(cls, methods, parent)


def _get_inplace(pos, default, args, kwargs):
    """
    Return true if `inplace` argument in `args` or `kwargs` is true. If inplace
    is only in kswargs, `pos` should be -1.
    """
    if pos >= 0 and len(args) > pos:
        return args[pos]
    return kwargs.get("inplace", default)


def _from_pandas_to_value(obj):
    if isinstance(obj, pandas.DataFrame):
        from fireducks.pandas.frame import _from_pandas_frame

        return _from_pandas_frame(obj)
    elif isinstance(obj, pandas.Series):
        from fireducks.pandas.series import _from_pandas_series

        return _from_pandas_series(obj)
    raise RuntimeError(
        "fireducks._from_pandas_to_value: unknown object is given: "
        f"{type(obj)}"
    )


def _setup_FireDucksPandsCompat(cls):
    fallback_methods = [
        # Explicit fallbacks are required since __getattr__ does not hook
        # special methods
        # These methods have to be defined in a super class of DataFrame
        # because those might be called explicitly like `super(DataFrame,
        # df).rename_axis` as some test cases in pandas.tests do.
        "rename_axis",
        "drop",
        "interpolate",
        "_where",
        "mask",
        "__delitem__",
        "__matmul__",
        "__rmatmul__",
    ]
    utils.install_fallbacks(cls, fallback_methods)

    return cls


def _make_pandas_doc_wrapper(fireducks_func, pandas_func):
    """
    Create a wrapper function that delegates to the given FireDucks method,
    but copies the docstring and signature from the corresponding pandas method.

    Args:
        fireducks_func: The FireDucks superclass method to delegate to.
        pandas_func: The pandas method whose docstring and signature should be used.

    Returns:
        A function that calls `fireducks_func` with the same arguments, but appears
        (to help IDEs and documentation tools) as the pandas method.
    """

    @functools.wraps(pandas_func)
    def wrapper(self, *args, **kwargs):
        # Call the original FireDucks method with all arguments.
        return fireducks_func(self, *args, **kwargs)

    return wrapper


def _wrap_pandas(cls, pandas_cls):
    """
    Attach pandas method docstrings and signatures to FireDucks classes.

    - For each method defined in `cls` (excluding private methods), if a method
      with the same name exists in `pandas_cls`, update the FireDucks method's
      metadata (docstring, name, etc.) using functools.update_wrapper.
    - For each method defined in the superclass of `cls` that is not already
      overridden in `cls`, if a method with the same name exists in `pandas_cls`,
      add a wrapper to `cls` that delegates to the superclass method, but with
      the docstring and signature of the pandas method.

    This enables FireDucks classes to provide pandas-compatible API documentation
    and better IDE support, while maintaining their own implementation.
    """
    inherited_methods = set()
    for attr_name, attr_value in vars(cls).items():
        if not attr_name.startswith("_") and isinstance(
            attr_value, types.FunctionType
        ):
            pandas_func = getattr(pandas_cls, attr_name, None)
            inherited_methods.add(attr_name)
            if pandas_func:
                # Update FireDucks method with pandas method's docstring, etc.
                functools.update_wrapper(attr_value, pandas_func)

    # Add superclass methods to cls with pandas docstrings if not overridden
    super_cls = cls.__bases__[0]
    for attr_name, attr_value in vars(super_cls).items():
        if (
            not attr_name.startswith("_")
            and attr_name not in inherited_methods
            and isinstance(attr_value, types.FunctionType)
        ):
            pandas_func = getattr(pandas_cls, attr_name, None)
            if pandas_func:
                # Add a wrapper to cls that delegates to the superclass method,
                # but uses the pandas method's docstring and signature.
                type.__setattr__(
                    cls,
                    attr_name,
                    _make_pandas_doc_wrapper(attr_value, pandas_func),
                )


def _is_object_to_object_cast(
    obj: Union["DataFrame", "Series"], to_dtype
) -> bool:
    from fireducks.pandas import DataFrame

    # Check if `to_dtype` is all "object"
    # FYI: `np.dtype("object") == "object"` is True
    if isinstance(to_dtype, dict):
        if any([t != "object" for t in to_dtype.values()]):
            return False
    elif to_dtype != "object":
        return False

    if isinstance(obj, DataFrame):
        # TODO: DataFrame.dtypes returns PandasWrapper. But it will be changed to
        # Series. Support DataFrame after it is changed.
        return False

    # NOTE: `obj.dtypes` is the evaluation point.
    return obj.dtypes == "object"


@_setup_FireDucksPandsCompat
class FireDucksPandasCompat(
    FireDucksObject, metaclass=FireDucksPandasCompatMetaclass
):
    """
    Super class of fireducks.pandas.DataFrame and Series to share
    implementation.

    This class does not intend to be compatible with
    pandas.core.generic.NDFrame.
    """

    # DataFrame is not hashable as pandas. Because we define __eq__,
    # we have to set None explicitly. See GT #1229
    __hash__ = None

    def __init__(self, value, *, pandas_object=None, hint=None):
        logger.debug("FireDucksPandasCompat.__init__: hint=%s", hint)
        super().__init__(value)
        metadata = FireDucksMetadata(hint=hint)
        metadata.set_cache("pandas_object", pandas_object)
        object.__setattr__(self, "_fireducks_meta", metadata)

    @property
    def _fireducks_hint(self):
        """
        Return hint if available, otherwise None

        Return
        ======
        :class:`fireducks.pandas.hinting.hint.TableHint` or None
        """
        return self._fireducks_meta.hint

    def __finalize__(self, other, method=None):
        return self

    def __array_ufunc__(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        decoded_args = utils.decode_args(
            args, kwargs, pandas_cls.__array_ufunc__
        )

        reason = None
        method = decoded_args.method
        ufunc = decoded_args.ufunc
        inputs = decoded_args.inputs

        if method != "__call__":
            reason = f"Unsupported {method=}"
        if decoded_args.kwargs:
            reason = f"{ufunc=} is called with kwargs"
        if len(inputs) != 1:
            reason = f"Unsupported non-unary {ufunc=}"
        if not utils.is_supported_unary_method_name(ufunc.__name__):
            reason = f"Unsupported {ufunc=}"

        if reason:
            return self._fallback_call(
                "__array_ufunc__",
                args,
                kwargs,
                reason=reason,
            )

        fname = "abs" if ufunc.__name__ == "absolute" else ufunc.__name__
        return self.__class__._create(ir.unary_op(self._value, fname))

    def _rebind(self, value, *, invalidate_cache=False):
        super()._rebind(value)
        if invalidate_cache:
            self._fireducks_meta.invalidate_cache()
            self._fireducks_meta.invalidate_hint()

    def _unwrap(self, reason=None):
        return self.to_pandas(reason=f"unwrap ({reason})")

    def _get_fallback(self, inplace):
        if inplace:
            return self._fallback_mutating_method
        return self._fallback_call

    def _get_metadata(self):
        assert fireducks.core.get_ir_prop().has_metadata
        if not self._fireducks_meta.is_cached("ir_metadata_wrapper"):
            value = ir.get_metadata(self._value)
            metadata = fireducks.core.evaluate([value])[0]
            self._fireducks_meta.set_cache(
                "ir_metadata_wrapper", IRMetadataWrapper(metadata)
            )
        return self._fireducks_meta.get_cache("ir_metadata_wrapper")

    # Deprecated. Use _fallback_call
    # DataFrame.eval and queriy use this method
    def _fallback_call_unpacked(self, __fireducks_method, *args, **kwargs):
        reason = kwargs.pop("__fireducks_reason", None)
        return utils.fallback_call(
            self._unwrap, __fireducks_method, args, kwargs, reason=reason
        )

    def _fallback_call(
        self, method, args=None, kwargs=None, *, reason=None, stacklevel=7
    ):
        return utils.fallback_call(
            self._unwrap,
            method,
            args,
            kwargs,
            reason=reason,
            stacklevel=stacklevel,
        )

    def _fallback_may_inplace(
        self,
        method,
        args,
        kwargs,
        *,
        pos=-1,
        default=False,
        reason=None,
        stacklevel=9,
    ):
        logger.debug(
            "_fallback_may_inplace: method=%s inplace=%s",
            method,
            _get_inplace(pos, default, args, kwargs),
        )
        fallback = self._get_fallback(_get_inplace(pos, default, args, kwargs))
        return fallback(
            method, args, kwargs, reason=reason, stacklevel=stacklevel
        )

    def _rebind_to_cache(self):
        """Rebind self to cached object"""
        assert self._fireducks_meta.is_cached(
            "pandas_object"
        )  # fallback sets cache
        obj = self._fireducks_meta.get_cache("pandas_object")
        value = _from_pandas_to_value(obj)
        self._rebind(value)
        self._fireducks_meta.invalidate_hint()

    # A mutating method changes itself. We have to rebuild self._value because
    # it holds the value before this mutating method.
    def _fallback_mutating_method(
        self, method, args=None, kwargs=None, *, reason=None, stacklevel=7
    ):
        logger.debug("_fallback_mutating_method: %s", method)
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs

        # dfkl backend does not need this evaluation because tables in the dfkl
        # backend are immutable and depending ops can be executed safely after
        # executing this mutating method. But because tables in a pandas
        # backend are not immutable, we will evaluate depending ops here.
        fireducks.core.evaluate_ops_depending_on_defs_of([self._value])

        # At the moment, we allow `from_pandas` to do zero-copy as dfkl
        # backend. It means that a table managed by a backend might share
        # actual data buffer with pandas and such pandas object might be cached
        # at frontend. To prevent a pandas's mutating method from updating such
        # a shared buffer, the cache will be invalidated here. Without a cache,
        # unwrap during fallback creates copy of the buffer.  See GT #2693
        self._fireducks_meta.invalidate_cache()

        ret = self._fallback_call(
            method, args, kwargs, reason=reason, stacklevel=stacklevel
        )
        self._rebind_to_cache()
        return ret

    # In-place binop returns self.
    def _fallback_inplace_binop(self, __fireducks_method, *args, **kwargs):
        self._fallback_mutating_method(__fireducks_method, args, kwargs)
        return self

    def __getattr__(self, name):
        """Fallback of missing attribute"""
        reason = f"{type(self).__name__}.__getattr__ for {name} is called"
        return utils.fallback_attr(self._unwrap, name, reason)

    def __getstate__(self):
        logger.debug("DataFrame.__getstate__")
        return self.to_pandas().__getstate__()

    def _invalidate_cache(self):
        self._fireducks_meta.invalidate_cache()
        return self

    def _set_index_names(self, names):  # inplace: self.index.names = names
        logger.debug("%s._set_index_names", self.__class__.__name__)
        names = irutils.make_tuple_of_scalars(names)
        value = ir.set_index_names(self._value, names)
        self._rebind(value, invalidate_cache=True)

    def _slice(self, slobj, axis=0):
        assert isinstance(slobj, slice), type(slobj)
        reason = None
        if axis != 0:
            reason = f"unsupported axis: {axis} for slicing"

        step = slobj.step or 1
        if step != 1:
            reason = f"unsupported step: {step} for slicing"

        if reason:
            return self._fallback_call("_slice", args=[slobj], reason=reason)
        start = slobj.start or 0
        stop = irutils.make_scalar(slobj.stop)
        return self.__class__._create(ir.slice(self._value, start, stop, step))

    def _sort_index(
        self,
        args,
        kwargs,
        *,
        decoded_args,
        is_series,
    ):
        known_kinds = ("quicksort", "mergesort", "heapsort", "stable")
        known_unstable_sort = ("quicksort", "heapsort")
        known_na_position = ("first", "last")

        if decoded_args.kind is None:
            decoded_args.kind = "quicksort"  # default kind

        if decoded_args.axis != 0 and decoded_args.axis != "index":
            reason = "axis is not 0"
        elif not isinstance(decoded_args.ignore_index, bool):
            reason = "ignore_index is not bool"
        elif not isinstance(decoded_args.inplace, bool):
            reason = "inplace is not bool"
        elif decoded_args.kind not in known_kinds:
            reason = f"kind is not in [{', '.join(known_kinds)}]"
        elif decoded_args.na_position not in known_na_position:
            reason = f"na_position is not in [{', '.join(known_na_position)}]"
        else:
            reason = decoded_args.is_not_default(
                exclude=[
                    "axis",
                    "ascending",
                    "ignore_index",
                    "inplace",
                    "kind",
                    "na_position",
                ]
            )

        if reason:
            if callable(decoded_args.level):

                def wrapper(*args, **kwargs):
                    return utils._unwrap(decoded_args.level(*args, **kwargs))

                kwargs["level"] = wrapper

            return self._fallback_may_inplace(
                "sort_index", args, kwargs, pos=3, reason=reason
            )

        if irutils.irable_scalar(decoded_args.ascending):
            ascending = bool(decoded_args.ascending)
        else:
            ascending = [bool(e) for e in decoded_args.ascending]
        orders = irutils.make_vector_or_scalar_of_scalar(ascending)
        na_pos = decoded_args.na_position != "first"
        stable = decoded_args.kind not in known_unstable_sort

        value = ir.sort_index(
            self._value,
            orders,
            ignore_index=decoded_args.ignore_index,
            is_series=is_series,
            na_pos=na_pos,
            stable=stable,
        )
        return self._create_or_inplace(value, decoded_args.inplace)

    def _sort_values(
        self,
        args,
        kwargs,
        *,
        decoded_args,
        by,
        ascending,
        is_series,
    ):
        known_kinds = ("quicksort", "mergesort", "heapsort", "stable")
        known_unstable_sort = ("quicksort", "heapsort")
        known_na_position = ("first", "last")

        if decoded_args.kind is None:
            decoded_args.kind = "quicksort"  # default kind

        if decoded_args.axis != 0 and decoded_args.axis != "index":
            reason = "axis is not 0"
        elif not isinstance(decoded_args.ignore_index, bool):
            reason = "ignore_index is not bool"
        elif not isinstance(decoded_args.inplace, bool):
            reason = "inplace is not bool"
        elif decoded_args.kind not in known_kinds:
            reason = f"kind is not in [{', '.join(known_kinds)}]"
        elif decoded_args.na_position not in known_na_position:
            reason = f"na_position is not in [{', '.join(known_na_position)}]"
        else:
            reason = decoded_args.is_not_default(
                exclude=[
                    "axis",
                    "ascending",
                    "by",
                    "ignore_index",
                    "inplace",
                    "kind",
                    "na_position",
                ]
            )

        if reason:
            if callable(decoded_args.key):

                def wrapper(*args, **kwargs):
                    return utils._unwrap(decoded_args.key(*args, **kwargs))

                kwargs["key"] = wrapper

            return self._fallback_may_inplace(
                "sort_values", args, kwargs, pos=3, reason=reason
            )

        keys = irutils.make_tuple_of_column_names(by)
        orders = ir.make_tuple_i1([bool(a) for a in ascending])
        na_pos = decoded_args.na_position != "first"
        stable = decoded_args.kind not in known_unstable_sort

        value = ir.sort_values(
            self._value,
            keys,
            orders,
            ignore_index=decoded_args.ignore_index,
            is_series=is_series,
            na_pos=na_pos,
            stable=stable,
        )
        return self._create_or_inplace(value, decoded_args.inplace)

    def __get_trunc_repr_method_result__(self, method="__repr__"):
        if self._fireducks_meta.is_cached("pandas_object"):
            return (
                utils._wrap(
                    getattr(
                        self._fireducks_meta.get_cache("pandas_object"), method
                    )()
                ),
                False,
            )

        n = len(self)
        minr, maxr = (
            pandas.get_option("display.min_rows"),
            pandas.get_option("display.max_rows"),
        )
        need_truncation = maxr is not None and n > maxr
        if need_truncation:
            minr = maxr if minr is None or minr > maxr else minr
            n = minr // 2 + 1  # +1 for truncated view
            tmp = fireducks.pandas.concat([self.head(n), self.tail(n)])
            pandas.set_option("display.max_rows", minr)
            ret = tmp._fallback_call(method, reason="with truncated data")
            pandas.set_option("display.max_rows", maxr)
        else:
            ret = self._fallback_call(
                method, reason=f"with full data of size: {n}"
            )
        return ret, need_truncation

    def __str__(self):
        return repr(self)

    def _where_base_checker(self, *args, **kwargs):
        from fireducks.pandas import Series, DataFrame

        def _check_fallback_for_where(decoded_args, accept_classes):
            if utils._pd_version_under2:
                reason = decoded_args.is_not_default(
                    ["level", "errors", "try_cast"]
                )
            else:
                # pandas2.2 removed 'errors' and 'try_cast' arguments.
                reason = decoded_args.is_not_default(["level"])
            if reason is not None:
                return reason

            # check for 'inplace' parameter
            decoded_args.inplace = validate_bool_kwarg(
                decoded_args.inplace, "inplace"
            )

            # check for 'cond' parameter
            if callable(decoded_args.cond):
                decoded_args.cond = decoded_args.cond(self)

            cond = decoded_args.cond
            if not isinstance(cond, accept_classes):
                return f"Unsupported 'cond' of type: {type(cond).__name__}"

            # check for 'other' parameter
            other = decoded_args.other
            if not (
                other is pandas_extensions.no_default
                or irutils.irable_scalar(other)
                or isinstance(other, _Scalar)
                or isinstance(other, accept_classes)
            ):
                return f"Unsupported 'other' of type: {type(other).__name__}"

            # check for 'axis' parameter
            if isinstance(self, Series) and decoded_args.axis is None:
                decoded_args.axis = 0

            axis = decoded_args.axis
            if axis is None:
                if isinstance(other, Series):
                    raise ValueError(
                        "Must specify axis=0 or 1, when axis=None"
                    )
            else:
                decoded_args.axis = self._get_axis_number(axis)
                if decoded_args.axis == 1:
                    return "axis=1 is not supported"

            return None

        pandas_cls = utils._pandas_class(self.__class__)
        decoded_args = utils.decode_args(args, kwargs, pandas_cls.where)
        accept_classes = (
            (Series, DataFrame) if isinstance(self, DataFrame) else (Series)
        )
        reason = _check_fallback_for_where(decoded_args, accept_classes)
        return reason, decoded_args, accept_classes

    def _where_impl(self, cond, other, axis, accept_classes) -> fire.Value:
        assert irutils.irable_scalar(axis)
        axis = irutils.make_scalar(axis)

        condIsSeries = cond.__class__.__name__ == "Series"
        cond = cond._value

        if other is pandas_extensions.no_default or other is np.nan:
            other = ir.make_null_scalar_null()
            othertype = "scalar"
        elif irutils.irable_scalar(other):
            other = irutils.make_scalar(other)
            othertype = "scalar"
        elif isinstance(other, _Scalar):
            other = other._value
            othertype = "scalar"
        else:
            assert isinstance(other, accept_classes)
            other = other._value
            othertype = "table"

        OP = ir.where_scalar if othertype == "scalar" else ir.where_table
        return OP(self._value, cond, other, axis, condIsSeries)

    def where(self, *args, **kwargs):
        reason, decoded_args, accept_classes = self._where_base_checker(
            *args, **kwargs
        )
        if reason is not None:
            return self._fallback_may_inplace(
                "where", args, kwargs, pos=2, reason=reason
            )

        return self._create_or_inplace(
            self._where_impl(
                decoded_args.cond,
                decoded_args.other,
                decoded_args.axis,
                accept_classes,
            ),
            decoded_args.inplace,
        )

    def _mask_impl(self, cond, other, axis, accept_classes) -> fire.Value:
        return self._where_impl(~cond, other, axis, accept_classes)

    def mask(self, *args, **kwargs):
        reason, decoded_args, accept_classes = self._where_base_checker(
            *args, **kwargs
        )
        if reason is not None:
            return self._fallback_may_inplace(
                "mask", args, kwargs, pos=2, reason=reason
            )

        return self._create_or_inplace(
            self._mask_impl(
                decoded_args.cond,
                decoded_args.other,
                decoded_args.axis,
                accept_classes,
            ),
            decoded_args.inplace,
        )

    #
    # Pandas API
    #

    def apply(self, func, *args, **kwargs):
        white_list_funcs = (len,)
        if callable(func) and func not in white_list_funcs:

            def wrapper(*args, **kwargs):
                # Because func will be called by pandas, args and kwargs might
                # be pandas's object. func might use fireducks's data or func
                # itself is fireducks's function, args and kwargs should be
                # converted to ducks's one.
                args = utils._wrap(args)
                kwargs = utils._wrap(kwargs)
                return utils._unwrap(func(*args, **kwargs))

            args = (wrapper,) + args
            return self._fallback_call("apply", args, kwargs, stacklevel=8)
        else:
            args = (func,) + args
            return self._fallback_call("apply", args, kwargs, stacklevel=8)

    def astype(self, dtype, copy=True, errors="raise"):
        from fireducks.pandas import Series

        dtype = dtype.to_dict() if isinstance(dtype, Series) else dtype

        def is_supported_dtype_or_dict(dtype):
            if is_dict_like(dtype):
                return irutils.is_column_names(
                    dtype.keys()
                ) and utils.is_supported_dtypes(dtype.values())
            return utils.is_supported_dtype(dtype)

        # `astype(copy=False)` might not work as expected.
        if not copy:
            warnings.warn(
                "astype(copy=False) might not work, when changes made in the "
                "data values of the DataFrame is expected to be reflected in "
                "the original DataFrame.",
                UserWarning,
                stacklevel=3,
            )

        reason = None
        if not is_supported_dtype_or_dict(dtype):
            # To avoid fallback for `df["a"].astype("object")` where
            # `df["a"].dtype` is "object"
            if _is_object_to_object_cast(self, dtype):
                return self.copy()

            reason = f"unsupported dtype: {dtype}"
        elif errors != "raise":
            reason = "errors is not raise"

        if reason:
            return self._fallback_call(
                "astype", args=[dtype, copy, errors], reason=reason
            )

        if is_dict_like(dtype):
            keys = irutils.make_tuple_of_column_names(dtype.keys())
            dtypes = ir.make_tuple_str(
                [utils.to_supported_dtype(t) for t in dtype.values()]
            )
        else:
            keys = irutils.make_tuple_of_column_names([])
            dtypes = ir.make_tuple_str([utils.to_supported_dtype(dtype)])
        return self.__class__._create(ir.cast(self._value, keys, dtypes))

    def copy(self, deep: bool = True):
        # Pandas 1.3.3 _libs/reduction.pyx calls copy with deep='all'
        # https://github.com/pandas-dev/pandas/issues/31441
        if not isinstance(deep, bool):
            result = self._fallback_call("copy", args=[deep])
        else:
            if not deep:
                warnings.warn(
                    "df2 = df1.copy(deep=False) might not work, when changes "
                    "made in the data values of 'df2' is expected to be "
                    "reflected in 'df1'. REF: https://fireducks-dev.github.io"
                    "/docs/user-guide/04-compatibility/#copydeep--false",
                    UserWarning,
                )
            result = self.__class__._create(
                ir.copy(self._value, deep), hint=self._fireducks_hint
            )
        return result.__finalize__(self)

    def clip(self, *args, **kwargs):
        from fireducks.pandas import Series, DataFrame

        def check_fallback_for_clip(decoded):
            decoded.axis = nv.validate_clip_with_axis(
                decoded.axis, (), decoded.kwargs
            )
            reason = decoded.is_not_default(
                exclude=["lower", "upper", "axis", "inplace", "kwargs"]
            )
            if reason is not None:
                return reason

            def supported_clipper(val, name):
                if (
                    val is None
                    or irutils.irable_scalar(val)
                    or isinstance(val, _Scalar)
                ):
                    return None
                else:
                    return (
                        f"Unsupported '{name}' of type: '{type(val).__name__}'",
                    )

            lower = decoded.lower
            reason = supported_clipper(lower, "lower")
            if reason is not None:
                return reason

            upper = decoded.upper
            reason = supported_clipper(upper, "upper")
            if reason is not None:
                return reason

            if lower is not None and upper is not None:
                # swap if scalar and adjustable
                if irutils.irable_scalar(lower) and irutils.irable_scalar(
                    upper
                ):
                    decoded.lower, decoded.upper = (
                        min(lower, upper),
                        max(lower, upper),
                    )

            # currently only scalars are supported as for lower/upper bounds
            # hence axis=0/1 will have same behavior
            if decoded.axis is not None:
                self._get_axis_number(decoded.axis)  # validates given axis

            decoded.inplace = validate_bool_kwarg(decoded.inplace, "inplace")
            return None

        pandas_cls = utils._pandas_class(self.__class__)
        decoded = utils.decode_args(args, kwargs, pandas_cls.clip)
        reason = check_fallback_for_clip(decoded)

        if reason is not None:
            return self._fallback_may_inplace(
                "clip", args, kwargs, pos=3, reason=reason
            )

        lower = decoded.lower
        upper = decoded.upper
        inplace = decoded.inplace

        if lower is None and upper is None:
            return None if inplace else self

        axis = 0
        accept_classes = (
            (Series, DataFrame) if isinstance(self, DataFrame) else (Series)
        )
        if lower is not None and upper is None:
            ret_value = self._mask_impl(
                self < lower, lower, axis, accept_classes
            )
        elif lower is None and upper is not None:
            ret_value = self._mask_impl(
                self > upper, upper, axis, accept_classes
            )
        else:
            tmp = self.mask(self < lower, lower, axis=axis)
            ret_value = tmp._mask_impl(
                tmp > upper, upper, axis, accept_classes
            )

        return self._create_or_inplace(ret_value, inplace)

    def describe(self, *args, **kwargs):
        from fireducks.pandas import Series

        cls = self.__class__

        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.describe)
        reason = None
        if arg.percentiles is not None:
            reason = "percentiles is not None"
        if arg.include is not None:
            reason = "include is not None"
        if arg.exclude is not None:
            reason = "exclude is not None"
        if utils._pd_version_under2:
            if arg.datetime_is_numeric:
                reason = "datetime_is_numeric is True"

        if not reason:
            if fireducks.core.get_ir_prop().has_metadata:
                target_types = [
                    np.int8,
                    np.int16,
                    np.int32,
                    np.int64,
                    np.uint8,
                    np.uint16,
                    np.uint32,
                    np.uint64,
                    np.float32,
                    np.float64,
                ]
                col_dtypes = (
                    [self.dtype] if cls == Series else list(self.dtypes)
                )
                is_numeric = len(col_dtypes) > 0 and np.any(
                    [i in target_types for i in col_dtypes]
                )
                # fallback in case no numeric column exists
                if not is_numeric:
                    reason = "describe with non-numeric column"

        if reason is not None:
            return self._fallback_call("describe", args, kwargs, reason=reason)
        return cls._create(ir.describe(self._value))

    def diff(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.diff)

        periods = arg.periods
        if not pandas_lib.is_integer(periods):
            if not (is_float(periods) and periods.is_integer()):
                raise ValueError("periods must be an integer")
            periods = int(periods)
        elif isinstance(periods, np.integer):
            periods = int(periods)

        assert isinstance(periods, int)

        reason = None
        # Series.diff does not have axis
        if hasattr(arg, "axis") and (arg.axis == 1 or arg.axis == "columns"):
            reason = "axis is not 0"

        if reason:
            return self._fallback_call("diff", args, kwargs, reason=reason)

        return self.__class__._create(ir.diff(self._value, periods))

    @deprecate_nonkeyword_arguments(
        version=None, allowed_args=["self", "labels"]
    )
    def drop(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.drop)
        arg.inplace = validate_bool_kwarg(arg.inplace, "inplace")
        arg.axis = self._get_axis_number(
            arg.axis
        )  # error if 1/columns for Series

        if arg.labels is not None:
            if arg.index is not None or arg.columns is not None:
                raise ValueError(
                    "Cannot specify both 'labels' and 'index'/'columns'"
                )
            if arg.axis == 1:
                arg.columns = arg.labels
            else:
                arg.index = arg.labels
        elif arg.index is None and arg.columns is None:
            raise ValueError(
                "Need to specify at least one of "
                "'labels', 'index' or 'columns'"
            )

        reason = arg.is_not_default(["errors"])

        if reason is None:
            if arg.columns is not None:
                if arg.level not in [None, 0]:
                    reason = f"Unsupported level: `{arg.level}` with axis: 1"

            if arg.index is not None:
                if arg.level is not None:
                    reason = f"Unsupported level: `{arg.level}` with axis: 0"

        output = None
        if reason is None:
            if arg.columns is not None:
                if self.ndim != 1:
                    if isinstance(arg.columns, Index):
                        arg.columns = list(arg.columns)
                    if irutils.is_column_name_or_column_names(arg.columns):
                        arg.columns = (
                            irutils.make_vector_or_scalar_of_column_name(
                                arg.columns
                            )
                        )
                        value = ir.drop_columns(
                            self._value,
                            arg.columns,
                            -1 if arg.level is None else arg.level,
                        )
                        output = self._create_or_inplace(value, arg.inplace)
                    else:
                        reason = (
                            "Unsupported `columns` of type: "
                            f"{type(arg.columns).__name__}"
                        )
                else:
                    output = self  # no change for Series

        if reason is None:
            if arg.index is not None:
                if irutils.irable_scalar(arg.index):
                    arg.index = Index([arg.index])
                if isinstance(arg.index, list):
                    if np.all([irutils.irable_scalar(i) for i in arg.index]):
                        arg.index = Index(arg.index)
                    elif np.all([isinstance(i, tuple) for i in arg.index]):
                        arg.index = MultiIndex.from_tuples(arg.index)
                if isinstance(arg.index, (Index, MultiIndex)):
                    indices = fireducks.pandas.DataFrame(index=arg.index)
                    # output is not None: for drop_rows followed by drop_columns
                    tbl = self if output is None else output
                    output = tbl._create_or_inplace(
                        ir.drop_rows(tbl._value, indices._value), arg.inplace
                    )
                else:
                    reason = "index is not a scalar, list or Index "

        if reason is None:
            return output

        return self._fallback_may_inplace(
            "drop", args, kwargs, pos=5, reason=reason
        )

    @property
    def empty(self):
        return any(a == 0 for a in self.shape)

    @property
    def _typ(self):
        return "series" if self.ndim == 1 else "dataframe"

    def fillna(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.fillna)
        # raises error for invalid axis
        axis = self._get_axis_number(arg.axis or 0)
        fillv = arg.value

        if fillv is None and arg.method is None:
            raise ValueError("Must specify a fill 'value' or 'method'.")

        reason = arg.is_not_default(["method", "limit", "downcast"])
        if not reason and axis != 0:
            reason = (
                f"{self.__class__.__name__}.fillna on "
                f"unsupported axis: {arg.axis}"
            )

        if not reason:
            if fillv is not None and irutils.irable_scalar(fillv):
                # TODO: add implicit casting support to avoid error
                # when filling nulls of string column with non-string scalar
                keys = irutils.make_tuple_of_column_names([])
                dtypes = ir.make_tuple_str([])
                fillv = irutils.make_scalar(fillv)
                return self._create_or_inplace(
                    ir.fillna_scalar(self._value, fillv, keys, dtypes),
                    arg.inplace,
                )

            elif isinstance(self, fireducks.pandas.DataFrame) and is_dict_like(
                fillv
            ):
                cols, vals, reason = utils.get_key_value_tuples(fillv)
                if not reason:
                    return self._create_or_inplace(
                        ir.column_wise_apply(
                            self._value, "fillna", cols, vals
                        ),
                        arg.inplace,
                    )
            else:
                reason = (
                    f"{self.__class__.__name__}.fillna with unsupported "
                    f"'value' of type: {type(fillv).__name__}"
                )

        return self._fallback_may_inplace(
            "fillna", args, kwargs, pos=3, reason=reason
        )

    def head(self, n=5):
        stop = irutils.make_scalar(n)
        return self.__class__._create(ir.slice(self._value, 0, stop, 1))

    @property
    def iloc(self):
        return _IlocIndexer(self)

    def _get_shape(self):
        if self._fireducks_meta.is_cached("pandas_object"):
            return self._fireducks_meta.get_cache("pandas_object").shape

        if not self._fireducks_meta.is_cached("shape"):
            value = ir.get_shape(self._value)
            shape = fireducks.core.evaluate([value])[0]
            self._fireducks_meta.set_cache("shape", (shape.y, shape.x))
        return self._fireducks_meta.get_cache("shape")

    def _get_index(self):
        if self._fireducks_meta.is_cached("pandas_object"):
            index = utils._wrap(
                self._fireducks_meta.get_cache("pandas_object").index
            )
            index._set_fireducks_frame(self, "index")
            return index

        if not self._fireducks_meta.is_cached("index"):
            # trick: just extract only index part to reduce
            # fallback overhead of data columns
            target = (
                self.to_frame()
                if isinstance(self, fireducks.pandas.Series)
                else self
            )
            index_columns = target[[]]

            # TODO: wrap IndexColumns with _value
            index = utils.fallback_attr(
                index_columns._unwrap,
                "index",
                reason=f"{self.__class__.__name__}.index",
            )
            index._set_fireducks_frame(self, "index")
            self._fireducks_meta.set_cache("index", index)
        return self._fireducks_meta.get_cache("index")

    @property
    def index(self):
        """The index (row labels) of the DataFrame/Series"""
        logger.debug("%s.index", self.__class__.__name__)
        return self._get_index()

    @index.setter
    def index(self, value):
        logger.debug("%s.index: type=%s", self.__class__.__name__, type(value))
        if value is None:
            raise TypeError(
                "Index(...) must be called with a collection of some kind"
                ", None was passed"
            )
        return self._set_axis(value, axis=0, _inplace_index_setter=True)

    def _fallback_set_axis(
        self, args, kwargs, arg, class_name, _inplace_index_setter
    ):
        # If `_inplace_index_setter` is true, this method is called from
        # the property setter of fireducks.Frame.index.

        if utils._pd_version_under2:
            if arg.inplace is True and arg.copy is True:
                raise ValueError(
                    "Cannot specify both inplace=True and copy=True"
                )
            if arg.inplace is pandas_extensions.no_default:
                arg.inplace = False

        reason = None
        if arg.is_not_default(["copy"]) and not arg.copy:
            reason = f"unsupported copy: {arg.copy}"

        if not reason:
            if arg.axis in ("columns", 1) and class_name == "DataFrame":
                if not irutils._is_irable_scalar_arraylike(arg.labels):
                    reason = (
                        f"unsupported value of type: '{type(arg.labels)}'"
                        "for axis=1"
                    )
            elif arg.axis in ("index", 0):
                from fireducks.pandas import Series

                if isinstance(arg.labels, list):
                    if type(arg.labels) is not list:  # FrozenList etc.
                        arg.labels = list(arg.labels)
                    if len(arg.labels) and pandas_lib.is_all_arraylike(
                        arg.labels
                    ):
                        arg.labels = MultiIndex.from_arrays(arg.labels)

                if not isinstance(
                    arg.labels, (Series, Index, MultiIndex, range)
                ) and not irutils._is_irable_scalar_arraylike(arg.labels):
                    reason = (
                        "labels is neither an index-like nor a list of "
                        "irable-scalars or index-like"
                    )

                if isinstance(arg.labels, np.ndarray) and arg.labels.ndim > 1:
                    raise ValueError("Index data must be 1-dimensional")
            else:
                raise ValueError(
                    f"No axis named {arg.axis} for object type {class_name}"
                )

        if not reason and isinstance(arg.labels, DatetimeIndex):
            # FIXME: frequency information is lost when converting
            # Index -> Series, hence falling back when frequency
            # information is available...
            if arg.labels.freq is not None:
                reason = f"labels is a DatetimeIndex of frequency: {arg.labels.freq}"

        if reason is not None:
            if _inplace_index_setter:
                result = self._fallback_mutating_method(
                    "__setattr__", args=["index", arg.labels], reason=reason
                )
            else:
                result = self._fallback_may_inplace(
                    "set_axis", args, kwargs, pos=2, reason=reason
                )
            return (reason, result)
        else:
            return (reason, None)

    @property
    def loc(self):
        return _LocIndexer(self)

    def pipe(self, func, *args, **kwargs):
        import pandas.core.common as com

        return com.pipe(self, func, *args, **kwargs)

    def replace(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.replace)

        reason = None
        if arg.to_replace is None or not irutils.irable_scalar(arg.to_replace):
            reason = "unsupported to_replace argument"
        elif (
            arg.value is pandas_extensions.no_default
            or not irutils.irable_scalar(arg.value)
        ):
            reason = "unsupported value argument"
        else:
            reason = arg.is_not_default(["inplace", "limit", "method"])

        if not isinstance(arg.regex, bool):
            reason = (
                f"unsupported 'regex' of type '{type(arg.regex).__name__}'"
            )

        if reason:
            return self._fallback_may_inplace(
                "replace", args, kwargs, reason=reason
            )

        arg.to_replace = irutils.make_scalar(arg.to_replace)
        arg.value = irutils.make_scalar(arg.value)
        return self.__class__._create(
            ir.replace_scalar(
                self._value, arg.to_replace, arg.value, arg.regex
            )
        )

    def sample(self, *args, **kwargs):
        from pandas.core import common, sample

        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.sample)

        n, frac, replace, weights, random_state, axis, ignore_index = (
            arg.n,
            arg.frac,
            arg.replace,
            arg.weights,
            arg.random_state,
            arg.axis,
            arg.ignore_index,
        )

        reason = None
        if weights is not None:
            reason = "weight is not None"

        if reason:
            return self._fallback_call("sample", args, kwargs, reason=reason)

        if axis is None:
            axis = 0
        # raises error if axis is 1 or columns when self is Series
        axis = self._get_axis_number(axis)
        obj_len = self.shape[axis]

        # Process random_state argument
        rs = common.random_state(random_state)

        size = sample.process_sampling_size(n, frac, replace)
        if size is None:
            assert frac is not None
            size = round(frac * obj_len)
        sampled_indices = sample.sample(obj_len, size, replace, weights, rs)
        return self._take(
            sampled_indices,
            axis=axis,
            ignore_index=ignore_index,
            check_boundary=False,
            check_negative=False,
        )

    def shift(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.shift)

        reason = arg.is_not_default(["freq", "fill_value"])

        if not reason:
            if arg.axis in (0, "index"):
                if not isinstance(arg.periods, int):
                    reason = f"periods, '{arg.periods}' is not int"
                else:
                    return self.__class__._create(
                        ir.shift(self._value, arg.periods)
                    )
            else:
                reason = f"unsupported axis: '{arg.axis}'"

        return self._fallback_call("shift", args, kwargs, reason=reason)

    def squeeze(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.squeeze)
        if arg.axis is None:
            # by default all N-1 axes are squeezed
            if self.ndim == 1:  # Series
                nrows = self.shape[0]
                return self.iloc[0] if nrows == 1 else self
            else:
                nrows, ncols = self.shape
                if nrows == 1:
                    return self.iloc[0, 0] if ncols == 1 else self.iloc[0]
                else:
                    return self.iloc[:, 0] if ncols == 1 else self
        else:
            # raises error if axis is 1 or columns when self is Series
            axis = self._get_axis_number(arg.axis)
            if self.ndim == 1:  # Series (axis parameter is unused)
                nrows = self.shape[0]
                return self.iloc[0] if nrows == 1 else self
            else:
                nrows, ncols = self.shape
                if nrows == 1:
                    if axis == 0:
                        return self.iloc[0, :]
                    else:
                        return self.iloc[:, 0] if ncols == 1 else self
                else:
                    if ncols == 1:
                        return self.iloc[:, 0] if axis == 1 else self
                    else:
                        return self

    def tail(self, n=5):
        if n == 0:
            stop = irutils.make_scalar(0)
        else:
            stop = irutils.make_scalar(None)
        return self.__class__._create(ir.slice(self._value, -n, stop, 1))

    def _take(
        self,
        indices,
        axis=0,
        ignore_index=False,
        check_boundary=True,
        check_negative=True,
    ):
        from fireducks.pandas import Series, Index

        input_indices = None
        if isinstance(indices, range):
            indices = slice(indices.start, indices.stop, indices.step)
        if axis == 0:
            if isinstance(indices, slice):
                return self._slice(indices)

            if isinstance(indices, Series):
                input_indices = indices.astype(int)
            elif utils._is_numeric_index_like(indices):
                input_indices = Series(indices).astype(int)
        else:
            # TODO: improve column slicing (ideally number
            # of columns are not very high though...)
            if isinstance(indices, slice):
                nrow, ncol = self.shape  # should not be called for Series
                if (
                    indices.start is None
                    and indices.stop is None
                    and indices.step == -1
                ):
                    indices = np.arange(ncol - 1, -1, -1)
                else:
                    st = indices.start or 0
                    stop = indices.stop or ncol
                    step = indices.step or 1
                    st = ncol + st if st < 0 else st
                    if stop > ncol:
                        stop = ncol
                    elif stop < 0:
                        stop += ncol
                    indices = np.arange(st, stop, step)
            if isinstance(indices, Series):
                input_indices = indices
            elif isinstance(
                indices, (Index, np.ndarray)
            ) or irutils._is_list_or_tuple_of(indices, int):
                input_indices = Series(indices).astype(int)

        if input_indices is None:
            reason = (
                f"axis: {axis} take with unsupported indices of "
                f"type: {type(indices).__name__}"
            )
            return self._fallback_call(
                "take", args=[indices, axis], reason=reason
            )
        input_indices = input_indices._value
        ignore_index = validate_bool_kwarg(ignore_index, "ignore_index")
        check_boundary = validate_bool_kwarg(check_boundary, "check_boundary")
        check_negative = validate_bool_kwarg(check_negative, "check_negative")
        is_scalar = (
            False  # pandas doesn't accept scalar value as for 'indices'
        )
        return self.__class__._create(
            ir.take(
                self._value,
                input_indices,
                axis,
                check_boundary,
                check_negative,
                ignore_index,
                is_scalar,
            )
        )

    def take(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        arg = utils.decode_args(args, kwargs, pandas_cls.take)

        if utils._pd_version_under2 and arg.is_copy is not None:
            warnings.warn(
                "is_copy is deprecated and will be removed in a future version. "
                "'take' always returns a copy, so there is no need to specify this.",
                FutureWarning,
            )

        nv.validate_take((), arg.kwargs)

        indices = arg.indices
        axis = self._get_axis_number(arg.axis)
        return self._take(indices, axis=axis)

    # fireducks method
    def to_pandas(self, options=None, reason=None):
        logger.debug("%s.to_pandas: reason: %s", type(self).__name__, reason)
        if self._fireducks_meta.is_cached("pandas_object"):
            logger.debug(
                "to_pandas: reuse _fireducks_meta.pandas_object_cache %x",
                id(self._fireducks_meta.get_cache("pandas_object")),
            )
        else:
            logger.debug("to_pandas: need to _evaluate")
            self._fireducks_meta.set_cache(
                "pandas_object", self._to_pandas(options=options)
            )

        return self._fireducks_meta.get_cache("pandas_object")

    def to_csv(self, *args, **kwargs):
        pandas_cls = utils._pandas_class(self.__class__)
        decoded = utils.decode_args(args, kwargs, pandas_cls.to_csv)

        sep = decoded.sep
        columns = decoded.columns
        na_rep = decoded.na_rep
        quoting = 0 if decoded.quoting is None else decoded.quoting
        path_or_buf = decoded.path_or_buf

        # NOTE: pandas seems to allow non bool type variable
        index = bool(decoded.index)

        # Workaround: `header` can not be checked by `decoded.is_not_default`
        # because header might be Index or so which can not be compared with
        # default value by `==` operator used in `is_not_default`
        header = False if decoded.header is None else decoded.header
        supp_header = (
            isinstance(header, bool)
            or irutils.is_column_name(header)
            or (
                isinstance(header, list)
                and all([irutils.is_column_name(x) for x in header])
            )
        )

        supp_columns = (
            columns is None
            or irutils.is_column_name(columns)
            or (
                isinstance(columns, list)
                and all([irutils.is_column_name(x) for x in columns])
            )
        )

        if sep is None:
            raise TypeError('"delimiter" must be string, not NoneType')

        reason = None
        if not (
            isinstance(path_or_buf, (str, os.PathLike)) or path_or_buf is None
        ):
            reason = "path_or_buf is not str or None"
        elif decoded.encoding not in (None, "utf-8", "utf8", "UTF-8", "UTF8"):
            reason = f"unsupported encoding: '{decoded.encoding}'"
        elif not supp_header:
            reason = f"unsupported header of type: '{type(header)}'"
        elif not supp_columns:
            reason = f"unsupported columns of type '{type(columns)}'"
        elif not isinstance(sep, str) or len(sep) != 1:
            reason = f"unsupported separator: '{sep}'"
        elif not isinstance(na_rep, str):
            reason = f"unsupported na_rep: '{na_rep}'"
        elif quoting not in [0, 2, 3, 4]:
            # 1: QUOTE_ALL (including NULL) is not supported by arrow
            reason = f"unsupported quoting: '{quoting}'"
        else:
            reason = decoded.is_not_default(
                exclude=[
                    "encoding",
                    "path_or_buf",
                    "index",
                    "header",
                    "columns",
                    "sep",
                    "na_rep",
                    "quoting",
                ]
            )

        if reason is not None:
            return self._fallback_call("to_csv", args, kwargs, reason=reason)

        target = self
        if columns is not None:
            target = target[columns]
        is_series = isinstance(target, fireducks.pandas.Series)
        renamed = False

        if not isinstance(header, list):
            header = bool(header)
        if not isinstance(header, bool):
            if is_series:
                if isinstance(header, list):  # no-op otherwise
                    if len(header) > 1:
                        raise ValueError(
                            f"Writing 1 cols but got {len(header)} aliases"
                        )
                    target = target.copy()
                    target.name = header[0]
                    header = True
                    renamed = True
            else:  # must be DataFrame
                target = target.copy()
                # when len(target.columns) != len(header), error
                # will be raised by columns setter
                target.columns = header
                header = True
                renamed = True

        if header and is_series and not renamed:
            # to rename unnamed column as 0
            target = target.to_frame()

        ir_kwargs = {
            "table": target._value,
            "sep": sep,
            "na_rep": na_rep,
            "header": header,
            "index": index,
            "quoting_style": quoting,
        }
        if path_or_buf is None:
            # no filename, returns string output
            ir_func = ir.to_csv
        else:
            ir_func = ir.write_csv
            ir_kwargs["filename"] = (
                path_or_buf.__fspath__()
                if isinstance(path_or_buf, os.PathLike)
                else path_or_buf
            )

        result = ir_func(**ir_kwargs)
        try:
            ret = fireducks.core.evaluate([result])
        except Exception as e:  # RuntimeError etc. at backend
            reason = f"{type(e).__name__}: {e}. Falling back to pandas."
            return self._fallback_call("to_csv", args, kwargs, reason=reason)

        return ret[0]  # either string or None


def setup_Scalar(cls):
    ops = [
        "all",
        "__str__",
        "__bool__",
        "__repr__",
        # unary ops
        "__abs__",
        "__neg__",
    ]  # yapf: disable

    utils.install_fallbacks(cls, ops, override=True)

    bin_ops = [
        "__add__",
        "__floordiv__",
        "__mod__",
        "__mul__",
        "__pow__",
        "__sub__",
        "__truediv__",
        "__radd__",
        "__rfloordiv__",
        "__rmod__",
        "__rmul__",
        "__rpow__",
        "__rsub__",
        "__rtruediv__",
        "__eq__",
        "__ge__",
        "__gt__",
        "__le__",
        "__lt__",
        "__ne__",
        "__and__",
        "__or__",
        "__xor__",
    ]  # yapf: disable

    def get_wrapper(method_name, operator_func, reason):
        @functools.wraps(method_name)
        def wrapper(self, rhs):
            if isinstance(
                rhs, (fireducks.pandas.DataFrame, fireducks.pandas.Series)
            ):
                # Do not evaluate and generate IR if rhs is DataFrame or
                # Series.  e.g. _Scalar.__add__(DataFrame) calls
                # DataFrame.__radd__(_Scalar)
                return NotImplemented
            return operator_func(self._unwrap(reason), rhs)

        return wrapper

    def get_reverse_wrapper(method_name, operator_func, reason):
        @functools.wraps(method_name)
        def wrapper(self, rhs):
            return operator_func(rhs, self._unwrap(reason))

        return wrapper

    for op in bin_ops:
        reason = f"Scalar.{op} is called"

        if op.startswith("__r"):
            # Convert the attribute name from __rand__ to __and__ since operator module does not have __rand__.
            operator_func = getattr(operator, "__" + op[3:])
            wrapper = get_reverse_wrapper(op, operator_func, reason)
        else:
            operator_func = getattr(operator, op)
            wrapper = get_wrapper(op, operator_func, reason)

        utils.install_wrapper(cls, op, wrapper, None, True)

    return cls


@setup_Scalar
class _Scalar(FireDucksObject):
    def _unwrap(self, reason=None):
        from fireducks.fireducks_ext import Scalar

        logger.debug("_Scalar._unwrap: reason=%s", reason)
        val = fireducks.core.evaluate([self._value])[0]
        if isinstance(val, Scalar):
            val = val.to_pandas()
        return np.array(val)[()]  # make numpy scalar

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if method == "__call__":
            reason = "Scalar.__array_func__ is called"
            # unwrap because self is included in inputs.
            return ufunc(*utils._unwrap(inputs, reason=reason), **kwargs)
        else:
            # TODO: What to do when method is not "__call__"?
            return NotImplemented
