# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from typing import List

from fireducks import ir, irutils
from fireducks.pandas import DataFrame, Series
import fireducks.pandas.utils as utils

import numpy as np


def aggregation(
    input_df,
    group_key: str,
    group_values: List[str],
    agg_methods: List[str],
):
    """Aggregate values after grouping table rows by a given key.

    This function is carefully implemented to minimize computation cost and
    amount of intermediate data. As the result, it is about 17x faster than
    straightforward implementation in our evaluation.

    Parameters
    ----------
    input_df: DataFrame
        Input dataframe.

    group_key: string
        Group key

    group_values: List[str]
        Column names to be aggregated.

    agg_methods: List[str]
        Function names of aggeragation.

    Returns
    -------
    DataFrame: Input dataframe with aggregated columns.
    List[str]: List of new column names.

    Examples
    --------

    >>> df
       a   b    c
    0  0  10  1.0
    1  0  20  2.0
    2  1  30  3.0
    3  1  40  4.0
    >>> g, cols = pd.aggregation(df, 'a', ['b', 'c'], ['max', 'mean'])
    >>> g
       a   b    c  agg_max_b_grpby_a  agg_max_c_grpby_a  agg_mean_b_grpby_a  agg_mean_c_grpby_a
    0  0  10  1.0                 20                2.0                15.0                 1.5
    1  0  20  2.0                 20                2.0                15.0                 1.5
    2  1  30  3.0                 40                4.0                35.0                 3.5
    3  1  40  4.0                 40                4.0                35.0                 3.5

    Note
    ----
    This function is compatible with aggregation in `xfeat
    <https://github.com/pfnet-research/xfeat>`_.
    """  # noqa

    df = (
        input_df[[group_key] + list(group_values)]
        .groupby(group_key)
        .agg(agg_methods)
    )

    # Rename columns as xfeate.aggregation
    columns = [
        f"agg_{agg_method}_{col}_grpby_{group_key}"
        for col in group_values
        for agg_method in agg_methods
    ]
    df.columns = columns

    # Reorder columns as xfeat.aggregation
    new_cols = [
        f"agg_{agg_method}_{col}_grpby_{group_key}"
        for agg_method in agg_methods
        for col in group_values
    ]
    df = df[new_cols]

    new_df = input_df.merge(
        df, how="left", right_index=True, left_on=group_key
    )

    return new_df, new_cols


def merge_with_mask(
    left,
    right,
    left_mask=None,
    right_mask=None,
    how="inner",
    on=None,
    left_on=None,
    right_on=None,
    left_index=False,
    right_index=False,
    suffixes=("_x", "_y"),
):
    if left_mask is None and right_mask is None:
        return left.merge(
            right,
            how=how,
            on=on,
            left_on=left_on,
            right_on=right_on,
            left_index=left_index,
            right_index=right_index,
        )

    def to_list(x):
        # None can not be used as column name in merge
        if x is None:
            return []
        return x if isinstance(x, list) else [x]

    on = irutils.make_tuple_of_column_names(to_list(on))
    left_on = irutils.make_tuple_of_column_names(to_list(left_on))
    right_on = irutils.make_tuple_of_column_names(to_list(right_on))

    def setup_mask(mask):
        if mask is None:
            return ir.make_nullopt_table(), False
        elif isinstance(mask, Series):
            dtype = utils._deduce_dtype(mask)
            if dtype is not None and dtype == bool:
                return ir.make_optional_table(mask._value), False
        elif (
            isinstance(mask, np.ndarray)
            and mask.ndim == 1
            and mask.dtype == np.bool_
        ):
            mask = Series(mask)
            return ir.make_optional_table(mask._value), True
        else:
            raise ValueError(
                f"merge_with_mask : unsupported mask type: {type(mask)}"
            )

    left_mask, left_no_align = setup_mask(left_mask)
    right_mask, right_no_align = setup_mask(right_mask)

    left_suffix = irutils.make_optional_string(suffixes[0])
    right_suffix = irutils.make_optional_string(suffixes[1])

    return DataFrame._create(
        ir.join_with_mask(
            left._value,
            right._value,
            left_mask,
            right_mask,
            how,
            on,
            left_on,
            left_index,
            right_on,
            right_index,
            left_suffix,
            right_suffix,
            left_no_align=left_no_align,
            right_no_align=right_no_align,
        )
    )


def multi_target_encoding(
    input_df,
    group_keys: List[List[str]],
    target_value: str,
    agg_method: str,
):
    """Target encoding with multiple combinations of key columns.

    This function is carefully implemented to minimize computation cost. As
    the result, it is about 5x faster than straightforward implementation
    in our evaluation.

    Parameters
    ----------
    input_df: DataFrame
        Input dataframe.

    group_key: List[List[str]]
        Column names of keys.

    group_values: List[str]
        Column names of target value.

    agg_methods: List[str]
        Function names of encoding.

    Returns
    -------
    DataFrame: Input dataframe with encoded columns.
    List[str]: List of new column names.

    Examples
    --------

    >>> df
    a  b  c    x
    0  0  0  1  1.0
    1  1  0  1  2.0
    2  0  0  0  3.0
    3  1  1  0  4.0
    4  0  1  1  5.0
    5  1  0  1  6.0
    6  0  0  0  7.0
    7  1  0  0  8.0
    >>> g, cols = pd.multi_target_encoding(df, [['a','b'],['b','c'],['a','b','c']], 'x', 'mean')
    >>> g
       a  b  c    x  a-b-mean  b-c-mean  a-b-c-mean
    0  0  0  1  1.0  3.666667       3.0         1.0
    1  1  0  1  2.0  5.333333       3.0         4.0
    2  0  0  0  3.0  3.666667       6.0         5.0
    3  1  1  0  4.0  4.000000       4.0         4.0
    4  0  1  1  5.0  5.000000       5.0         5.0
    5  1  0  1  6.0  5.333333       3.0         4.0
    6  0  0  0  7.0  3.666667       6.0         5.0
    7  1  0  0  8.0  5.333333       6.0         8.0

    """  # noqa

    def _get_max_inclusion(group_keys: List[str]):
        nkeys = len(group_keys)

        if nkeys <= 1:
            return []

        max_set = []
        for i in range(nkeys):
            lst = []
            key0 = set(group_keys[i])
            for j in range(nkeys):
                if set(key0) >= set(group_keys[j]):
                    lst.append(j)
            if len(lst) > len(max_set):
                max_set = lst

        if len(max_set) == 1:
            return []

        return max_set

    def _multi_transform(
        input_df,
        group_keys,
        target_value,
        agg_method,
    ):
        all_keys = set()
        for key in group_keys:
            all_keys |= set(key)
        all_keys = list(all_keys)

        if agg_method == "mean":
            first_agg = ["sum", "count"]
            second_agg = "sum"
        elif agg_method in ["size", "count"]:
            first_agg = [agg_method]
            second_agg = "sum"
        else:
            first_agg = [agg_method]
            second_agg = agg_method

        grp = input_df.groupby(all_keys)
        df0 = grp[target_value].agg(first_agg)

        agg_cols = []
        for key in group_keys:
            colnm = "-".join(key) + "-" + agg_method
            df = df0.groupby(key)[first_agg].transform(second_agg)
            if agg_method == "mean":
                df0[colnm] = df["sum"] / df["count"]
            else:
                df0[colnm] = df
            agg_cols.append(colnm)

        index = grp.grouper.group_info[0]
        return df0[agg_cols].take(index)

    inclusion_ids = _get_max_inclusion(group_keys)

    if len(inclusion_ids) > 0:
        keys = [group_keys[i] for i in inclusion_ids]
        df0 = _multi_transform(input_df, keys, target_value, agg_method)

    output_df = input_df.copy()

    new_cols = []
    for i in range(len(group_keys)):
        key = group_keys[i]
        colnm = "-".join(key) + "-" + agg_method

        if i in inclusion_ids:
            output_df[colnm] = df0[colnm].values
        else:
            output_df[colnm] = input_df.groupby(key)[target_value].transform(
                agg_method
            )

        new_cols.append(colnm)

    return output_df, new_cols
