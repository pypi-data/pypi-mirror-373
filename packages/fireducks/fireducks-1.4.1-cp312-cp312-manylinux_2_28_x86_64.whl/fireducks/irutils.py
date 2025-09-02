# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

# IR Utilities

import logging

import datetime
import pandas
import numpy as np

from fireducks import ir
from collections.abc import Iterable

logger = logging.getLogger(__name__)


def _is_irable_scalar_arraylike(obj):
    # for ndarray, checking only for first element should be fine
    if isinstance(obj, np.ndarray) and obj.ndim == 1:
        return True if len(obj) == 0 else irable_scalar(obj[0])
    return isinstance(obj, (list, tuple)) and all(
        [irable_scalar(x) for x in obj]
    )


# TODO: move to pandas/utils.py
def _is_str_list(obj):
    return _is_list_of(obj, (str))


def _is_list_of(obj, types):
    return isinstance(obj, list) and all([isinstance(x, types) for x in obj])


def _is_list_or_tuple_of(obj, types):
    return isinstance(obj, (list, tuple)) and all(
        [isinstance(x, types) for x in obj]
    )


def _is_scalar_or_list_of(obj, types):
    return isinstance(obj, types) or _is_list_of(obj, types)


def _is_scalar_or_list_or_tuple_of(obj, types):
    return isinstance(obj, types) or _is_list_or_tuple_of(obj, types)


def check_uniform_typed_list_or_tuple(obj):
    # empty list/tuple will also return True
    return (
        isinstance(obj, (list, tuple)) and len(set(type(x) for x in obj)) <= 1
    )


# TODO: add Timedelta, Timestamp etc.
def irable_scalar(obj):
    if (
        isinstance(
            obj,
            (
                str,
                bool,
                np.bool_,
                int,
                np.int32,
                np.int64,
                float,
                np.float64,
                np.float32,
                bytes,
            ),
        )
        or obj is None
        or obj is pandas.NaT
    ):
        return True
    return False


def make_scalar(obj):
    if obj is None:
        return ir.make_null_scalar_null()
    elif obj is pandas.NaT:
        return ir.make_null_scalar_timestamp_ns()
    elif isinstance(obj, str):
        return ir.make_scalar_str(obj)
    elif isinstance(obj, bytes):
        return ir.make_scalar_binary(obj.decode())
    elif isinstance(obj, (bool, np.bool_)):
        return ir.make_scalar_i1(bool(obj))
    elif isinstance(obj, (int, np.int64)):
        return ir.make_scalar_i64(int(obj))
    elif isinstance(obj, np.uint64):
        return ir.make_scalar_ui64(int(obj))
    elif isinstance(obj, (float, np.float64)):
        if np.isnan(obj):
            return ir.make_null_scalar_f64()
        else:
            return ir.make_scalar_f64(obj)
    elif isinstance(obj, np.int32):
        return ir.make_scalar_i32(int(obj))
    elif isinstance(obj, np.float32):
        return ir.make_scalar_f32(float(obj))
    elif isinstance(obj, datetime.time):
        ts = int(
            (obj.hour * 3600 + obj.minute * 60 + obj.second) * 10**6
            + obj.microsecond
        )
        return ir.make_scalar_time64_us(ts)
    elif isinstance(obj, datetime.date):
        ts = int(pandas.Timestamp(obj).value)
        return ir.make_scalar_timestamp_ns(ts)
    elif isinstance(obj, np.datetime64):
        ts = int(obj.astype("datetime64[ns]").astype("int64"))
        return ir.make_scalar_timestamp_ns(ts)
    elif isinstance(obj, pandas.Timestamp):
        ts = int(obj.value)
        return ir.make_scalar_timestamp_ns(ts)
    elif isinstance(obj, pandas.Timedelta):
        ts = int(obj.value)
        return ir.make_scalar_duration_ns(ts)
    raise RuntimeError(f"make_scalar: unknown type: {type(obj)}")


def make_column_name_element(args):
    # logger.debug("make_column_name_element: args=%s", args)
    if irable_scalar(args):
        scalar = make_scalar(args)
        return ir.make_column_name_element_scalar(scalar)
    elif isinstance(args, tuple):
        scalars = [make_scalar(a) for a in args]
        return ir.make_column_name_element_vector(scalars)
    raise RuntimeError(f"make_scalar: unknown type: {type(args)}")


def make_column_name(args):
    # logger.debug("make_column_name: args=%s", args)
    if isinstance(args, tuple) or irable_scalar(args):
        scalar = make_column_name_element(args)
        return ir.make_column_name_scalar(scalar)

    assert isinstance(args, (list, range, np.ndarray))
    args = [make_column_name_element(a) for a in args]
    return ir.make_column_name_vector(args)


def make_tuple_of_column_names(args):
    # logger.debug("make_tuple_of_column_name: args=%s", args)
    args = [make_column_name(v) for v in args]
    return ir.make_tuple_column_name(args)


def is_column_name(x):
    """Return true if x can be passed to make_column_name" """

    if irable_scalar(x):
        return True
    if isinstance(x, tuple):
        return all([irable_scalar(y) for y in x])
    return False


def is_column_names(lst):
    if isinstance(lst, Iterable):
        return all([is_column_name(x) for x in lst])
    return False


def is_column_name_or_column_names(scalar_or_list):
    return is_column_name(scalar_or_list) or is_column_names(scalar_or_list)


# deprecated in future. Try to use make_column_name
def make_tuple_of_scalars(args):
    if isinstance(args, (list, tuple, range, np.ndarray)):
        args = [make_scalar(a) for a in args]
    else:
        args = [make_scalar(args)]
    return ir.make_tuple_scalar(args)


def make_tuple_of_tables(args):
    return ir.make_tuple_table([x._value for x in args])


def make_tuple_of_vector_or_scalar_of_str(args):
    args = [make_vector_or_scalar_of_str(a) for a in args]
    return ir.make_tuple_of_vector_or_scalar_of_str(args)


def _make_vector_or_scalar_of(args, from_scalar, from_vector, to_value):
    if isinstance(args, list):
        return from_vector([to_value(x) for x in args])
    return from_scalar(to_value(args))


def make_vector_or_scalar_of_column_name(args):
    return _make_vector_or_scalar_of(
        args,
        ir.make_vector_or_scalar_of_column_name_from_scalar,
        ir.make_vector_or_scalar_of_column_name_from_vector,
        make_column_name,
    )


def make_vector_or_scalar_of_scalar(args):
    return _make_vector_or_scalar_of(
        args,
        ir.make_vector_or_scalar_of_scalar_from_scalar,
        ir.make_vector_or_scalar_of_scalar_from_vector,
        make_scalar,
    )


def make_vector_or_scalar_of_str(args):
    if isinstance(args, str):  # "a"
        return ir.make_vector_or_scalar_from_scalar_str(args)
    if _is_list_of(args, str):  # ["a"], ["a", "b"]
        return ir.make_vector_or_scalar_from_vector_str(args)
    raise TypeError("make_vector_or_scalar_of_str: unexpected type")


def make_optional_string(value):
    if value is None:
        return ir.make_nullopt_string()
    return ir.make_optional_string(value)


def make_optional_table(tbl):
    if tbl is None:
        return ir.make_nullopt_table()
    return ir.make_optional_table(tbl._value)
