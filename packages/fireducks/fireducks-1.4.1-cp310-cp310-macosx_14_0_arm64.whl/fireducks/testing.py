# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import re

import fireducks.pandas as pd
import pandas


def assert_range_index_equal(left, right):
    assert left.start == right.start
    assert left.stop == right.stop
    assert left.step == right.step


def assert_index_equal(left, right, exact=True):
    assert left.equals(right)
    if exact:
        assert type(left) == type(right)

    # left.equal(right) return true when both range indexes are empty with
    # different start/stop/step. Ex:
    #   - RangeIndex(6, 6, 1)
    #   - RangeIndex(3, 0, 5)
    # To check pandas compatibility, we check more strictly.
    #
    # To use this assert for pandas, allow pandas.RangeIndex. It does not mean
    # that we want to test fireducks's index with pandas's index.
    if isinstance(left, pd.wrappers.RangeIndex) or isinstance(
        left, pandas.RangeIndex
    ):
        assert_range_index_equal(left, right)

    assert left.names == right.names


def assert_frame_equal(
    left, right, *, check_index_type=True, sort=False, ignore_index=False
):
    """
    FireDucks version of pandas.testing.assert_frame_equal.

    Parameters
    ----------
    sort : bool, default False
        Since FireDucks is not compatible with pandas in a row order of
        merge/join result, this asserter compares two frames after sorting.
    ignore_index : bool, default False
        This option is used only sort=True. Depending on parameters of merge,
        index of the result is reset to default index, i.e. 0, 1, 2.... In that
        case, since two frames may have different index by sort, index should
        be ignored in comparison by calling this method with ignore_index=True.
    """

    if sort:
        if not ignore_index:
            left = left.reset_index()
            right = right.reset_index()

        # If the same column name exists, rename the column for sorting.
        same_cols_name = False
        if right.columns.duplicated().any():
            same_cols_name = True
            left_cols = left.columns
            right_cols = right.columns
            left.columns = [str(i) for i in range(len(left.columns))]
            right.columns = [str(i) for i in range(len(right.columns))]

        # Sort for comparison.
        left = left.sort_values(by=left.columns.to_list(), ignore_index=True)
        right = right.sort_values(
            by=right.columns.to_list(), ignore_index=True
        )

        # Revert changed column names.
        if same_cols_name:
            left.columns = left_cols
            right.columns = right_cols

    assert left.equals(right)
    assert left.columns.names == right.columns.names
    assert_index_equal(left.index, right.index, exact=check_index_type)


def assert_series_equal(left, right, check_index_type=True):
    assert left.equals(right)
    assert left.name == right.name
    assert_index_equal(left.index, right.index, check_index_type)


def assert_ops_order(ir, expected):
    def find_index(ops, pattern):
        for i, op in enumerate(ops):
            m = re.search(pattern, op)
            if m:
                return i
        return -1

    ops = ir.splitlines()
    # for i, op in enumerate(ops):
    #     print(f"{i:2d} {op}")

    pos = 0
    for i, pattern in enumerate(expected):
        idx = find_index(ops[pos:], pattern)
        if idx < 0:
            msg = f"{pattern=} not found"
            if i > 0:
                msg = msg + f" after {expected[i-1]}"
            assert False, msg
        # print(f"{pattern=} found at {pos+idx}")
        pos += idx + 1


def assert_num_ops(ir, op: str, num: int):
    ops = ir.splitlines()
    count = sum(1 for line in ops if op in line)
    assert count == num, f"{op} count: {count}"
