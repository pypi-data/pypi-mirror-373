# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import logging
import numpy as np

import fireducks.core
import fireducks.pandas.utils as utils
from fireducks import ir, irutils
from typing import Union
from pandas.api.types import is_integer
from pandas.core.common import is_bool_indexer

logger = logging.getLogger(__name__)


def getitem_fallbacker(target, key, reason):
    return utils.fallback_call(
        target._unwrap, "__getitem__", args=[key], reason=reason
    )


# df.take() doesn't support selecting a single column (i.e., df.take(0, axis=1))
# or mask-based column projection (i.e., df.take([True, False], axis=1)),
# but the IR supports the same. Hence creating a wrapper for the IR.
def _take_col(df: "DataFrame", col_idx: "IntegerOrArrayLikes"):
    from fireducks.pandas import Series, DataFrame

    if is_integer(col_idx):  # only one column is to be taken
        ret_cls = Series
        idx = Series([col_idx])
        is_scalar = True
    else:  # multiple columns are to be taken
        ret_cls = DataFrame
        idx = Series(col_idx) if not isinstance(col_idx, Series) else col_idx
        is_scalar = False
    return ret_cls._create(
        ir.take(
            df._value,
            idx._value,
            axis=1,
            check_boundary=True,
            check_negative=True,
            ignore_index=False,
            is_scalar=is_scalar,
        )
    )


class _Indexer:
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name

    def _unwrap(self, reason=None):
        return getattr(self.obj._unwrap(reason=reason), self.name)

    def __getitem__(self, key):
        reason = "fallback _Indexer(" + self.name + ").__getitem__"
        return getitem_fallbacker(self, key, reason)

    def __setitem__(self, key, value):
        reason = "fallback _Indexer(" + self.name + ").__setitem__"
        self.obj._fallback_mutating_method(
            self.name + ".__setitem__",
            args=[key, value],
            reason=reason,
        )


def is_column_locator(obj):
    if isinstance(obj, str):
        return True
    if irutils._is_str_list(obj):
        return True
    return False


def is_full_slice(slobj):
    return (
        isinstance(slobj, slice)
        and slobj.start is None
        and slobj.stop is None
        and slobj.step is None
    )


def series_loc_setitem_with_scalar(
    s: "Series", key: "ArrayLikes", val: "scalar"
):
    from fireducks.pandas import Series

    from_non_indexed_arraylike = not isinstance(key, Series)
    index_or_mask = Series(key) if from_non_indexed_arraylike else key
    res_value = ir.loc_setter_with_scalar(
        s._value,
        index_or_mask._value,
        irutils.make_scalar(val),
        irutils.make_column_name(None),
        from_non_indexed_arraylike,
        is_series=True,
    )
    return s._rebind(res_value, invalidate_cache=True)


def frame_loc_setitem_with_scalar(
    df: "DataFrame", row: "ArrayLikes", col: "ColumnName", val: "scalar"
):
    from fireducks.pandas import Series

    from_non_indexed_arraylike = not isinstance(row, Series)
    index_or_mask = Series(row) if from_non_indexed_arraylike else row
    # TODO: support list of columns names
    res_value = ir.loc_setter_with_scalar(
        df._value,
        index_or_mask._value,
        irutils.make_scalar(val),
        irutils.make_column_name(col),
        from_non_indexed_arraylike,
        is_series=False,
    )
    return df._rebind(res_value, invalidate_cache=True)


#
# xxx_loc_setitem_with_vector(): Due to immutable nature of FireDucks backend,
# current implementation logic is as follows:
#   - convert the vector to Series with required indices for placing new values
#   - perform s.mask(cond, val)
#
# s = pd.Series([1,2,3,4])
# s.loc[[False, True, False, True] = [20, 40]
# print(s) # [1, 20, 3, 40]
#
# data  cond   other  ->  if_else(~cond, data, other)
#   1   False  NaN    ->   1
#   2   True   20     ->  20
#   3   False  NaN    ->   3
#   4   True   40     ->  40
#
# TODO: When values are too less and the input data size (len(s)) is too big,
# it can introduce petrformance overhead. Implement it properly at the backend.
#
def series_loc_setitem_with_vector(
    s: "Series", mask: "Series", val: Union[list, tuple, np.ndarray, "Series"]
):
    from fireducks.pandas import Series

    # names: not applicable for Series
    names = irutils.make_vector_or_scalar_of_column_name([])

    if isinstance(val, Series):
        target = val
        OP = ir.if_else_assignment_with_vector
    else:  # true_mask_assignment
        target = Series(np.array(val))
        OP = ir.mask_assignment_with_vector

    res_value = OP(
        s._value,
        mask._value,
        target._value,
        names,
    )
    return s._rebind(res_value, invalidate_cache=True)


def frame_loc_setitem_with_vector(
    df: "DataFrame",
    mask: "Series",
    col: "ColumnName(s)",
    val: Union[list, tuple, np.ndarray, "Series"],
):
    from fireducks.pandas import Series

    names = irutils.make_vector_or_scalar_of_column_name(col)

    if isinstance(val, Series):
        target = val
        OP = ir.if_else_assignment_with_vector
    else:  # true_mask_assignment
        target = Series(np.array(val))
        OP = ir.mask_assignment_with_vector

    res_value = OP(
        df._value,
        mask._value,
        target._value,
        names,
    )
    return df._rebind(res_value, invalidate_cache=True)


class _LocIndexer(_Indexer):
    def __init__(self, obj):
        super().__init__(obj, "loc")

    def __getitem__(self, key):
        t_cls = self.obj.__class__
        reason = None
        m_name = f"fallback _LocIndexer({self.name}).__getitem__  "

        # TODO: support index selection: df.loc[[1,3,5]]
        if is_full_slice(key):  # df.loc[:], df.loc[::]
            return self.obj

        to_filter, mask, ignore_index = utils.is_filter_like(key)
        if to_filter:
            return t_cls._create(
                ir.filter(self.obj._value, mask._value, no_align=ignore_index)
            )

        if isinstance(key, tuple) and len(key) == 2:
            r, c = key
            # get single element
            # if isinstance(r, int) and isinstance(c, str):
            if irutils.irable_scalar(r) and irutils.irable_scalar(c):
                # df.loc[1, "a"] <- row(1), col("a")
                # df.loc[(2, 3)] <- row((2, 3)), col(:)
                # df.loc[(2, 3), "a"] <- row((2, 3)), col("a")
                if (
                    fireducks.core.get_fireducks_options().fast_fallback
                    and self.obj._fireducks_meta.is_cached("pandas_object")
                ):
                    cache = self.obj._fireducks_meta.get_cache("pandas_object")
                    return utils._wrap(cache.loc[key])
                else:
                    reason = m_name + "with tuple(scalar, scalar)"

            elif isinstance(r, tuple):
                # when row-indicator is of tuple type, projection-optimization
                # produces different result. Hence falling back at this moment.
                # For example, below two produces different result
                #   1. df.loc[pd.IndexSlice[:, :, 1], :] - keeps last index
                #   2. df.loc[pd.IndexSlice[:, :, 1]] - drops last index
                # REF: test_arithmetic.py::TestFrameArithmeticUnsorted::test_binary_ops_align
                reason = m_name + "with row-indicator of tuple"

            if not reason:
                if is_full_slice(c):
                    projected = self.obj
                elif is_column_locator(c):
                    projected = self.obj[c]
                elif is_bool_indexer(c):  # e.g, iloc[:, [True,False,True]]
                    projected = _take_col(self.obj, c)
                elif isinstance(c, slice):
                    st_loc = (
                        c.start
                        if c.start is None
                        else self.obj.columns.get_loc(c.start)
                    )
                    end_loc = (
                        c.stop
                        if c.stop is None
                        else self.obj.columns.get_loc(c.stop)
                    )
                    if (st_loc is None or isinstance(st_loc, int)) and (
                        end_loc is None or isinstance(end_loc, int)
                    ):
                        end_loc = (
                            end_loc + 1
                            if isinstance(end_loc, int)
                            else end_loc
                        )
                        projected = self.obj._take(
                            slice(st_loc, end_loc, c.step), axis=1
                        )
                else:
                    reason = m_name + "with unsupported column-indicator"

                if not reason:
                    # if further fallback happens due to unsupported 'r',
                    # it will take place on projected part of data
                    if callable(r):
                        mask_or_idx = self.obj.pipe(r)
                        return _LocIndexer(projected)[mask_or_idx]
                    return _LocIndexer(projected)[r]

        return getitem_fallbacker(self, key, reason or m_name)

    def __setitem__(self, key, val):
        from fireducks.pandas import Series

        def is_mask_vector_assignment(key, val):
            is_mask = (
                isinstance(key, Series) and utils._deduce_dtype(key) == bool
            )
            is_vec_assignment = isinstance(val, (list, range, Series)) or (
                isinstance(val, np.ndarray) and val.ndim == 1
            )
            return is_mask and is_vec_assignment

        # pandas treats single-element-vector as a scalar
        setval = (
            val[0]
            if isinstance(val, (list, range, np.ndarray)) and len(val) == 1
            else val
        )

        if isinstance(self.obj, Series):
            if (
                isinstance(key, Series) or utils._is_index_like(key)
            ) and irutils.irable_scalar(setval):
                return series_loc_setitem_with_scalar(self.obj, key, setval)

            if is_mask_vector_assignment(key, setval):
                return series_loc_setitem_with_vector(self.obj, key, setval)

        elif isinstance(key, tuple) and len(key) == 2:
            assert self.obj.ndim == 2  # must be a DataFrame
            row, col = key
            if isinstance(col, str):  # TODO: support list-of-column-names
                if (
                    isinstance(row, Series) or utils._is_index_like(row)
                ) and irutils.irable_scalar(setval):
                    return frame_loc_setitem_with_scalar(
                        self.obj, row, col, setval
                    )

            if irutils.is_column_name_or_column_names(col):
                if is_mask_vector_assignment(row, setval):
                    return frame_loc_setitem_with_vector(
                        self.obj, row, col, setval
                    )

        reason = f"_LocIndexer({self.name}).__setitem__ with unsupported key"
        self.obj._fallback_mutating_method(
            self.name + ".__setitem__",
            args=[key, val],
            reason=reason,
        )


class _IlocIndexer(_Indexer):
    def __init__(self, obj):
        super().__init__(obj, "iloc")

    def __getitem__(self, key):
        from fireducks.pandas import Series, Index
        from fireducks.pandas.generic import _Scalar

        reason = "fallback _ILocIndexer(" + self.name + ").__getitem__"

        # slice rows of input frame/series: iloc[range(2)]
        if isinstance(key, range):
            key = slice(key.start, key.stop, key.step)

        # slice rows of input frame/series: iloc[:2]
        if isinstance(key, slice):
            return self.obj._slice(key)

        # filter rows of input frame/series based on given indices...
        if isinstance(key, (list, Series, Index, np.ndarray)):  # iloc[[0,3]]
            return self.obj._take(key, axis=0)

        if isinstance(self.obj, Series):
            if isinstance(key, int):
                # get single element
                if (
                    fireducks.core.get_fireducks_options().fast_fallback
                    and self.obj._fireducks_meta.is_cached("pandas_object")
                ):  # read from cache
                    cache = self.obj._fireducks_meta.get_cache("pandas_object")
                    return cache.iloc[key]
                else:
                    value = ir.iloc_scalar(self.obj._value, key)
                    return _Scalar(value)._unwrap()

            return getitem_fallbacker(self, key, reason)

        # if not Series, self.obj must be a DataFrame
        if isinstance(key, int):  # e.g., df.iloc[0]
            # slice specified row of the dataframe, and fallback
            start = key if key >= 0 else key + len(self.obj)
            if start < 0:
                raise IndexError("single positional indexer is out-of-bounds")
            target = self.obj._slice(slice(start, start + 1))
            reason += f" on {key}th row-slice"
            return getitem_fallbacker(_IlocIndexer(target), 0, reason)

        if isinstance(key, tuple) and len(key) == 2:
            r, c = key
            # get single element
            if isinstance(r, int) and isinstance(c, int):
                if (
                    fireducks.core.get_fireducks_options().fast_fallback
                    and self.obj._fireducks_meta.is_cached("pandas_object")
                ):  # read from cache
                    cache = self.obj._fireducks_meta.get_cache("pandas_object")
                    return cache.iloc[key]
                else:
                    projected = _take_col(self.obj, c)
                    value = ir.iloc_scalar(projected._value, r)
                    return _Scalar(value)._unwrap()

            is_supported_colp = isinstance(
                c, (int, range, slice, list, tuple, Series, Index, np.ndarray)
            )

            if is_supported_colp:
                # let's project target columns first
                if is_full_slice(c):  # e.g, iloc[:, :]
                    projected = self.obj
                elif isinstance(c, int) or is_bool_indexer(c):
                    # e.g, iloc[:, 0], iloc[:, [True,False,True]]:
                    projected = _take_col(self.obj, c)
                else:  # e.g., iloc[:, :2], iloc[:, [0,3]]
                    projected = self.obj._take(c, axis=1)

                # let's perform slice/filter rows on projected columns
                if is_full_slice(r):
                    # projected-columns, all-rows
                    return projected
                elif isinstance(r, range):
                    # projected-columns, sliced-rows
                    r = slice(r.start, r.stop, r.step)
                    return projected._slice(r)
                elif isinstance(r, slice):
                    # projected-columns, sliced-rows
                    return projected._slice(r)
                elif isinstance(r, (list, Series, Index, np.ndarray)):
                    # projected-columns, filter-rows as per given row-indices
                    return projected._take(r, axis=0)
                elif callable(r):
                    row_idx = self.obj.pipe(r)
                    return _IlocIndexer(projected)[row_idx]
                elif isinstance(r, int):  # e.g., df.iloc[0, :]
                    # slice specified row from projected-columns, and fallback
                    start = r if r >= 0 else r + len(self.obj)
                    if start < 0:
                        raise IndexError(
                            "single positional indexer is out-of-bounds"
                        )
                    target = projected._slice(slice(start, start + 1))
                    reason += f" on {r}th row-slice of projected columns"
                    return getitem_fallbacker(_IlocIndexer(target), 0, reason)
                else:
                    reason += " on projected columns"
                    return getitem_fallbacker(
                        _IlocIndexer(projected), r, reason
                    )

        return getitem_fallbacker(self, key, reason)
