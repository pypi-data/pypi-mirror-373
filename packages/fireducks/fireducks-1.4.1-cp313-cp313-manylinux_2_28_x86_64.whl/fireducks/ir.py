# Copyright (c) 2023 NEC Corporation. All Rights Reserved.
"""
This file will be automatically generated from opdefs
"""

import fireducks.core
import firefw as fire

# old style
Ty_pyobj = fire.Type("!fireducks.pyobj")
Ty_scalar = fire.Type("!fireducks.scalar")

# new style
ColumnNameElementType = fire.Type("!fireducks.column_name_element")
ColumnNameType = fire.Type("!fireducks.column_name")
MetadataType = fire.Type("!fireducks.metadata")
OptionalStringType = fire.Type("!fireducks.optional<!tfrt.string>")
OptionalTableType = fire.Type("!fireducks.optional<!fireducks.table>")
ShapeType = fire.Type("!fireducks.shape")
TableType = fire.Type("!fireducks.table", is_mutable=True)
VectorOrScalarOfColumnNameType = fire.Type(
    "!fireducks.vector_or_scalar_of_column_name"
)
VectorOrScalarOfScalarType = fire.Type("!fireducks.vector_or_scalar_of_scalar")
VectorOrScalarOfStrType = fire.Type("!fireducks.vector_or_scalar_of_str")

ReadCSVOptionsType = fire.Type("!fireducks.read_csv_options")
AggregateOptionsType = fire.Type("!fireducks.aggregate_options")
WriteParquetOptionsType = fire.Type("!fireducks.write_parquet_options")

I1Type = fire.Type("i1")
I32Type = fire.Type("i32")
U32Type = fire.Type("ui32")
U64Type = fire.Type("ui64")
F32Type = fire.Type("f32")
StringType = fire.Type("!tfrt.string")

Op_make_column_name_element_scalar = fire.Opcode(
    "fireducks.make_column_name_element.from_scalar"
)
Op_make_column_name_element_vector = fire.Opcode(
    "fireducks.make_column_name_element.from_vector"
)
Op_make_column_name_scalar = fire.Opcode(
    "fireducks.make_column_name.from_scalar"
)
Op_make_column_name_vector = fire.Opcode(
    "fireducks.make_column_name.from_vector"
)
Op_make_scalar_f32 = fire.Opcode("fireducks.make_scalar.f32")
Op_make_scalar_f64 = fire.Opcode("fireducks.make_scalar.f64")
Op_make_scalar_i1 = fire.Opcode("fireducks.make_scalar.i1")
Op_make_scalar_i32 = fire.Opcode("fireducks.make_scalar.i32")
Op_make_scalar_i64 = fire.Opcode("fireducks.make_scalar.i64")
Op_make_scalar_ui64 = fire.Opcode("fireducks.make_scalar.ui64")
Op_make_scalar_str = fire.Opcode("fireducks.make_scalar.str")
Op_make_scalar_time64_us = fire.Opcode("fireducks.make_scalar.time64_us")
Op_make_scalar_timestamp_ns = fire.Opcode("fireducks.make_scalar.timestamp_ns")
Op_make_scalar_binary = fire.Opcode("fireducks.make_scalar.binary")
Op_make_scalar_duration_ns = fire.Opcode("fireducks.make_scalar.duration_ns")

Op_make_null_scalar_null = fire.Opcode("fireducks.make_null_scalar.null")
Op_make_null_scalar_f32 = fire.Opcode("fireducks.make_null_scalar.f32")
Op_make_null_scalar_f64 = fire.Opcode("fireducks.make_null_scalar.f64")
Op_make_null_scalar_timestamp_ns = fire.Opcode(
    "fireducks.make_null_scalar.timestamp_ns"
)
Op_make_null_scalar_duration_ns = fire.Opcode(
    "fireducks.make_null_scalar.duration_ns"
)

Op_make_tuple_column_name = fire.Opcode("fireducks.make_tuple.column_name")
Op_make_tuple_i1 = fire.Opcode("fireducks.make_tuple.i1")
Op_make_tuple_str = fire.Opcode("fireducks.make_tuple.str")
Op_make_tuple_scalar = fire.Opcode("fireducks.make_tuple.scalar")
Op_make_tuple_table = fire.Opcode("fireducks.make_tuple.table")
Op_make_tuple_vector_or_scalar_of_str = fire.Opcode(
    "fireducks.make_tuple.vector_or_scalar_of_str"
)

Op_make_vector_or_scalar_of_column_name_from_scalar = fire.Opcode(
    "fireducks.make_vector_or_scalar_of_column_name.from_scalar"
)
Op_make_vector_or_scalar_of_column_name_from_vector = fire.Opcode(
    "fireducks.make_vector_or_scalar_of_column_name.from_vector"
)

Op_make_vector_or_scalar_of_scalar_from_scalar = fire.Opcode(
    "fireducks.make_vector_or_scalar_of_scalar.from_scalar"
)
Op_make_vector_or_scalar_of_scalar_from_vector = fire.Opcode(
    "fireducks.make_vector_or_scalar_of_scalar.from_vector"
)

Op_make_vector_or_scalar_from_scalar_str = fire.Opcode(
    "fireducks.make_vector_or_scalar_of_str.from_scalar"
)
Op_make_vector_or_scalar_from_vector_str = fire.Opcode(
    "fireducks.make_vector_or_scalar_of_str.from_vector"
)

Op_assign_scalar = fire.Opcode("fireducks.assign.scalar")
Op_aggregate = fire.Opcode("fireducks.aggregate")
Op_aggregate_specified = fire.Opcode("fireducks.aggregate_specified")
Op_aggregate_column_scalar = fire.Opcode("fireducks.aggregate_column.scalar")
Op_apply_row = fire.Opcode("fireducks.apply_row")
Op_between = fire.Opcode("fireducks.between")
Op_cat_categories = fire.Opcode("fireducks.cat_categories")
Op_cast = fire.Opcode("fireducks.cast")
Op_concat = fire.Opcode("fireducks.concat")
Op_copy = fire.Opcode("fireducks.copy")
Op_colDictMap = fire.Opcode("fireducks.column_dict_map")
Op_column_wise_apply = fire.Opcode("fireducks.column_wise_apply")
Op_table_corr = fire.Opcode("fireducks.table_corr")
Op_series_corr = fire.Opcode("fireducks.series_corr")
Op_create_table_from_columns = fire.Opcode(
    "fireducks.create_table.from_columns"
)
Op_datetime_extract = fire.Opcode("fireducks.datetime_extract")
Op_datetime_total_seconds = fire.Opcode("fireducks.datetime_total_seconds")
Op_describe = fire.Opcode("fireducks.describe")
Op_diff = fire.Opcode("fireducks.diff")
Op_drop_columns = fire.Opcode("fireducks.drop_columns")
Op_drop_rows = fire.Opcode("fireducks.drop_rows")
Op_drop_duplicates = fire.Opcode("fireducks.drop_duplicates")
Op_dropna = fire.Opcode("fireducks.dropna")
Op_duplicated = fire.Opcode("fireducks.duplicated")
Op_explode = fire.Opcode("fireducks.explode")
Op_filter = fire.Opcode("fireducks.filter")
Op_fillna_scalar = fire.Opcode("fireducks.fillna_scalar")
Op_get_column_memory_usage = fire.Opcode("fireducks.get_column_memory_usage")
Op_get_table_memory_usage = fire.Opcode("fireducks.get_table_memory_usage")
Op_get_dummies = fire.Opcode("fireducks.get_dummies")
Op_get_metadata = fire.Opcode("fireducks.get_metadata")
Op_get_shape = fire.Opcode("fireducks.get_shape")
Op_groupby_agg = fire.Opcode("fireducks.groupby_agg")
Op_groupby_corrwith = fire.Opcode("fireducks.groupby_corrwith")
Op_groupby_head = fire.Opcode("fireducks.groupby_head")
Op_groupby_rank = fire.Opcode("fireducks.groupby_rank")
Op_groupby_select_rank = fire.Opcode("fireducks.groupby_select_rank")
Op_groupby_shift = fire.Opcode("fireducks.groupby_shift")
Op_groupby_tail = fire.Opcode("fireducks.groupby_tail")
Op_groupby_select_agg = fire.Opcode("fireducks.groupby_select_agg")
Op_groupby_transform = fire.Opcode("fireducks.groupby_transform")
Op_groupby_select_transform = fire.Opcode("fireducks.groupby_select_transform")
Op_invert = fire.Opcode("fireducks.invert")
Op_isin = fire.Opcode("fireducks.isin")
Op_isin_vector = fire.Opcode("fireducks.isin.vector")
Op_isnull = fire.Opcode("fireducks.isnull")
Op_iloc_scalar = fire.Opcode("fireducks.iloc_scalar")
Op_join = fire.Opcode("fireducks.join")
Op_join_with_mask = fire.Opcode("fireducks.join_with_mask")
Op_loc_setter_with_scalar = fire.Opcode("fireducks.loc_setter_with_scalar")
Op_if_else_assignment_with_vector = fire.Opcode(
    "fireducks.if_else_assignment_with_vector"
)
Op_mask_assignment_with_vector = fire.Opcode(
    "fireducks.mask_assignment_with_vector"
)
Op_melt = fire.Opcode("fireducks.melt")
Op_project = fire.Opcode("fireducks.project")
Op_quantile = fire.Opcode("fireducks.quantile")
Op_quantile_scalar = fire.Opcode("fireducks.quantile_scalar")
Op_read_csv = fire.Opcode("fireducks.read_csv")
Op_read_csv_metadata = fire.Opcode("fireducks.read_csv_metadata")
Op_read_csv_with_metadata = fire.Opcode("fireducks.read_csv_with_metadata")
Op_read_feather = fire.Opcode("fireducks.read_feather")
Op_read_feather_metadata = fire.Opcode("fireducks.read_feather_metadata")
Op_read_feather_with_metadata = fire.Opcode(
    "fireducks.read_feather_with_metadata"
)
Op_read_json = fire.Opcode("fireducks.read_json")
Op_read_parquet = fire.Opcode("fireducks.read_parquet")
Op_read_parquet_metadata = fire.Opcode("fireducks.read_parquet_metadata")
Op_read_parquet_with_metadata = fire.Opcode(
    "fireducks.read_parquet_with_metadata"
)
Op_rename = fire.Opcode("fireducks.rename")
Op_rename_specified = fire.Opcode("fireducks.rename_specified")
Op_repeat = fire.Opcode("fireducks.repeat")
Op_repeat_vector = fire.Opcode("fireducks.repeat.vector")
Op_rolling_aggregate = fire.Opcode("fireducks.rolling_aggregate")
Op_set_column_index_names = fire.Opcode("fireducks.set_column_index_names")
Op_set_index = fire.Opcode("fireducks.set_index")
Op_set_index_names = fire.Opcode("fireducks.set_index_names")
Op_slice = fire.Opcode("fireducks.slice")
Op_replace_scalar = fire.Opcode("fireducks.replace.scalar")
Op_reset_index = fire.Opcode("fireducks.reset_index")
Op_setitem = fire.Opcode("fireducks.setitem")
Op_shift = fire.Opcode("fireducks.shift")
Op_sort_index = fire.Opcode("fireducks.sort_index")
Op_sort_values = fire.Opcode("fireducks.sort_values")
Op_strftime = fire.Opcode("fireducks.strftime")
Op_str_contains = fire.Opcode("fireducks.str_contains")
Op_str_concat = fire.Opcode("fireducks.str_concat")
Op_str_endswith = fire.Opcode("fireducks.str_endswith")
Op_str_replace = fire.Opcode("fireducks.str_replace")
Op_str_slice = fire.Opcode("fireducks.str_slice")
Op_str_split = fire.Opcode("fireducks.str_split")
Op_str_startswith = fire.Opcode("fireducks.str_startswith")
Op_str_pad = fire.Opcode("fireducks.str_pad")
Op_str_trim = fire.Opcode("fireducks.str_trim")
Op_str_trim_wsp = fire.Opcode("fireducks.str_trim_wsp")
Op_str_unary_method = fire.Opcode("fireducks.str_unary_method")
Op_str_unary_bool_returning_method = fire.Opcode(
    "fireducks.str_unary_bool_returning_method"
)
Op_take_rows = fire.Opcode("fireducks.take_rows")
Op_take_cols = fire.Opcode("fireducks.take_cols")
Op_to_csv = fire.Opcode("fireducks.to_csv")
Op_value_counts = fire.Opcode("fireducks.value_counts")
Op_where_scalar = fire.Opcode("fireducks.where.scalar")
Op_where_table = fire.Opcode("fireducks.where.table")
Op_write_csv = fire.Opcode("fireducks.write_csv")
Op_write_parquet = fire.Opcode("fireducks.write_parquet")
Op_abs = fire.Opcode("fireducks.abs")
Op_negate = fire.Opcode("fireducks.negate")
Op_unary_op = fire.Opcode("fireducks.unary_op")
Op_round = fire.Opcode("fireducks.round")

Op_print_table = fire.Opcode("fireducks.print.table")
Op_from_pandas_frame_metadata = fire.Opcode(
    "fireducks.from_pandas.frame.metadata"
)
Op_to_pandas_frame_metadata = fire.Opcode("fireducks.to_pandas.frame.metadata")

Op_make_nullopt_string = fire.Opcode("fireducks.make_nullopt.string")
Op_make_optional_string = fire.Opcode("fireducks.make_optional.string")
Op_make_nullopt_table = fire.Opcode("fireducks.make_nullopt.table")
Op_make_optional_table = fire.Opcode("fireducks.make_optional.table")

# Pandas
Op_from_pandas_dataframe = fire.Opcode("fireducks.from_pandas.dataframe")
Op_from_pandas_series = fire.Opcode("fireducks.from_pandas.series")
Op_to_pandas = fire.Opcode("fireducks.to_pandas.dataframe")
Op_to_pandas_series = fire.Opcode("fireducks.to_pandas.series")
Op_to_numpy = fire.Opcode("fireducks.to_numpy")
Op_to_datetime = fire.Opcode("fireducks.to_datetime")
Op_to_frame = fire.Opcode("fireducks.to_frame")
Op_unique = fire.Opcode("fireducks.unique")


def _build_op(*args, **kwargs):
    return fireducks.core.build_op(*args, **kwargs)


def create_i1_attr(name, value):
    return fireducks.core.make_attr(I1Type, name, 1 if value else 0)


def create_i32_attr(name, value):
    return fireducks.core.make_attr(I32Type, name, value)


def create_u32_attr(name, value):
    return fireducks.core.make_attr(U32Type, name, value)


#
# Ops
#


def assign_scalar(table, key, value):
    return _build_op(
        Op_assign_scalar, [TableType], [table, key, value], chaining=True
    ).outs[0]


def aggregate(table, func, axis, options):
    options = fireducks.core.make_available_value(
        options, AggregateOptionsType
    )
    return _build_op(
        Op_aggregate,
        [TableType],
        [table, func, options, create_i32_attr("axis", axis)],
        chaining=True,
    ).outs[0]


def aggregate_specified(table, funcs, columns, relabels, axis):
    return _build_op(
        Op_aggregate_specified,
        [TableType],
        [table, funcs, columns, relabels, create_i32_attr("axis", axis)],
        chaining=True,
    ).outs[0]


def aggregate_column_scalar(table, func: str, options):
    options = fireducks.core.make_available_value(
        options, AggregateOptionsType
    )

    # TODO: support chaining only on input
    return _build_op(
        Op_aggregate_column_scalar, [Ty_scalar], [table, func, options]
    ).outs[0]


def apply_row(table, func):
    return _build_op(
        Op_apply_row, [TableType], [table, func], chaining=True
    ).outs[0]


def between(table, left, right, inclusive):
    return _build_op(
        Op_between, [TableType], [table, left, right, inclusive], chaining=True
    ).outs[0]


def cast(table, keys, dtypes):
    return _build_op(
        Op_cast, [TableType], [table, keys, dtypes], chaining=True
    ).outs[0]


def concat(tables, *, ignore_index, no_align):
    return _build_op(
        Op_concat,
        [TableType],
        [
            tables,
            create_i1_attr("ignore_index", ignore_index),
            create_i1_attr("no_align", no_align),
        ],
        chaining=True,
    ).outs[0]


def copy(table, deep):
    return _build_op(Op_copy, [TableType], [table, deep], chaining=True).outs[
        0
    ]


def column_dict_map(table, dict_map, map_as_take):
    return _build_op(
        Op_colDictMap,
        [TableType],
        [table, dict_map, create_i1_attr("map_as_take", map_as_take)],
        chaining=True,
    ).outs[0]


def table_corr(table, method, min_periods: int, numeric_only):
    return _build_op(
        Op_table_corr,
        [TableType],
        [
            table,
            method,
            create_u32_attr("min_periods", min_periods),
            create_i1_attr("numeric_only", numeric_only),
        ],
        chaining=True,
    ).outs[0]


def series_corr(left, right, method, min_periods: int):
    # TODO: support chaining only on input
    return _build_op(
        Op_series_corr,
        [Ty_scalar],
        [left, right, method, create_u32_attr("min_periods", min_periods)],
    ).outs[0]


def create_table_from_columns(columns, column_names):
    return _build_op(
        Op_create_table_from_columns,
        [TableType],
        [columns, column_names],
        chaining=True,
    ).outs[0]


def column_wise_apply(table, method_name, cols, vals):
    return _build_op(
        Op_column_wise_apply,
        [TableType],
        [table, method_name, cols, vals],
        chaining=True,
    ).outs[0]


def datetime_extract(table, field):
    return _build_op(
        Op_datetime_extract, [TableType], [table, field], chaining=True
    ).outs[0]


def datetime_total_seconds(table):
    return _build_op(
        Op_datetime_total_seconds, [TableType], [table], chaining=True
    ).outs[0]


def strftime(table, str_format):
    return _build_op(
        Op_strftime, [TableType], [table, str_format], chaining=True
    ).outs[0]


def describe(table):
    return _build_op(Op_describe, [TableType], [table], chaining=True).outs[0]


def diff(table, periods):
    return _build_op(
        Op_diff, [TableType], [table, periods], chaining=True
    ).outs[0]


def drop_columns(table, columns, level):
    return _build_op(
        Op_drop_columns,
        [TableType],
        [table, columns, create_i32_attr("level", level)],
        chaining=True,
    ).outs[0]


def drop_rows(table, index):
    return _build_op(
        Op_drop_rows, [TableType], [table, index], chaining=True
    ).outs[0]


def drop_duplicates(
    table, subset, keep, ignore_index, keep_org_index_when_no_dup
):
    return _build_op(
        Op_drop_duplicates,
        [TableType],
        [
            table,
            subset,
            keep,
            create_i1_attr("ignore_index", ignore_index),
            create_i1_attr(
                "keep_org_index_when_no_dup", keep_org_index_when_no_dup
            ),
        ],
        chaining=True,
    ).outs[0]


def dropna(table, subset, axis, ignore_index, is_any, thresh):
    return _build_op(
        Op_dropna,
        [TableType],
        [
            table,
            subset,
            axis,
            create_i1_attr("ignore_index", ignore_index),
            create_i1_attr("is_any", is_any),
            create_i32_attr("thresh", thresh),
        ],
        chaining=True,
    ).outs[0]


def duplicated(table, subset, keep):
    return _build_op(
        Op_duplicated,
        [TableType],
        [table, subset, keep],
        chaining=True,
    ).outs[0]


def explode(table, names, ignore_index):
    return _build_op(
        Op_explode,
        [TableType],
        [table, names, create_i1_attr("ignore_index", ignore_index)],
        chaining=True,
    ).outs[0]


def filter(table, array, no_align=False):
    return _build_op(
        Op_filter,
        [TableType],
        [table, array, create_i1_attr("no_align", no_align)],
        chaining=True,
    ).outs[0]


def from_pandas_dataframe(dataFrame):
    return _build_op(Op_from_pandas_dataframe, [TableType], [dataFrame]).outs[
        0
    ]


def from_pandas_series(dataFrame):
    return _build_op(Op_from_pandas_series, [TableType], [dataFrame]).outs[0]


def fillna_scalar(table, fill_value, keys, dtypes):
    return _build_op(
        Op_fillna_scalar,
        [TableType],
        [table, fill_value, keys, dtypes],
        chaining=True,
    ).outs[0]


def get_dummies(data, columns, prefix, prefix_sep, dtype, drop_first):
    return _build_op(
        Op_get_dummies,
        [TableType],
        [
            data,
            columns,
            prefix,
            prefix_sep,
            dtype,
            create_i1_attr("drop_first", drop_first),
        ],
        chaining=True,
    ).outs[0]


def get_column_memory_usage(table, deep, include_index):
    return _build_op(
        Op_get_column_memory_usage,
        [Ty_scalar],
        [
            table,
            create_i1_attr("deep", deep),
            create_i1_attr("include_index", include_index),
        ],
    ).outs[0]


def get_table_memory_usage(table, deep, include_index):
    return _build_op(
        Op_get_table_memory_usage,
        [TableType],
        [
            table,
            create_i1_attr("deep", deep),
            create_i1_attr("include_index", include_index),
        ],
        chaining=True,
    ).outs[0]


def get_metadata(table):
    return _build_op(
        Op_get_metadata, [MetadataType], [table], chaining=True
    ).outs[0]


def get_shape(table):
    return _build_op(Op_get_shape, [ShapeType], [table], chaining=True).outs[0]


def groupby_agg(
    table, groupkeys, funcs, columns, relabels, as_index, dropna, sort
):
    return _build_op(
        Op_groupby_agg,
        [TableType],
        [
            table,
            groupkeys,
            funcs,
            columns,
            relabels,
            create_i1_attr("as_index", as_index),
            create_i1_attr("dropna", dropna),
            create_i1_attr("sort", sort),
        ],
        chaining=True,
    ).outs[0]


def groupby_select_agg(
    table,
    groupkeys,
    funcs,
    columns,
    relabels,
    selector,
    as_index,
    dropna,
    sort,
):
    return _build_op(
        Op_groupby_select_agg,
        [TableType],
        [
            table,
            groupkeys,
            funcs,
            columns,
            relabels,
            selector,
            create_i1_attr("as_index", as_index),
            create_i1_attr("dropna", dropna),
            create_i1_attr("sort", sort),
        ],
        chaining=True,
    ).outs[0]


def groupby_corrwith(
    table, groupkeys, selector, other, as_index, dropna, sort, with_selector
):
    return _build_op(
        Op_groupby_corrwith,
        [TableType],
        [
            table,
            groupkeys,
            selector,
            other,
            create_i1_attr("as_index", as_index),
            create_i1_attr("dropna", dropna),
            create_i1_attr("sort", sort),
            create_i1_attr("with_selector", with_selector),
        ],
        chaining=True,
    ).outs[0]


def groupby_rank(
    table,
    groupkeys,
    method,
    na_option,
    ascending,
    dropna,
):
    return _build_op(
        Op_groupby_rank,
        [TableType],
        [
            table,
            groupkeys,
            method,
            na_option,
            create_i1_attr("ascending", ascending),
            create_i1_attr("dropna", dropna),
        ],
        chaining=True,
    ).outs[0]


def groupby_select_rank(
    table,
    groupkeys,
    selector,
    method,
    na_option,
    ascending,
    dropna,
):
    return _build_op(
        Op_groupby_select_rank,
        [TableType],
        [
            table,
            groupkeys,
            selector,
            method,
            na_option,
            create_i1_attr("ascending", ascending),
            create_i1_attr("dropna", dropna),
        ],
        chaining=True,
    ).outs[0]


def groupby_shift(table, groupkeys, selector, with_selector, periods, dropna):
    return _build_op(
        Op_groupby_shift,
        [TableType],
        [
            table,
            groupkeys,
            selector,
            periods,
            create_i1_attr("dropna", dropna),
            create_i1_attr("with_selector", with_selector),
        ],
        chaining=True,
    ).outs[0]


def groupby_head_or_tail(
    table, groupkeys, selector, with_selector, n, dropna, is_head
):
    if is_head:
        return _build_op(
            Op_groupby_head,
            [TableType],
            [
                table,
                groupkeys,
                selector,
                n,
                create_i1_attr("dropna", dropna),
                create_i1_attr("with_selector", with_selector),
            ],
            chaining=True,
        ).outs[0]
    else:
        return _build_op(
            Op_groupby_tail,
            [TableType],
            [
                table,
                groupkeys,
                selector,
                n,
                create_i1_attr("dropna", dropna),
                create_i1_attr("with_selector", with_selector),
            ],
            chaining=True,
        ).outs[0]


def groupby_transform(table, groupkey, funcs, columns, relabels):
    return _build_op(
        Op_groupby_transform,
        [TableType],
        [table, groupkey, funcs, columns, relabels],
        chaining=True,
    ).outs[0]


def groupby_select_transform(
    table, groupkey, funcs, columns, relabels, selector
):
    return _build_op(
        Op_groupby_select_transform,
        [TableType],
        [table, groupkey, funcs, columns, relabels, selector],
        chaining=True,
    ).outs[0]


def invert(table):
    return _build_op(Op_invert, [TableType], [table], chaining=True).outs[0]


def isin(table, values):
    return _build_op(
        Op_isin, [TableType], [table, values], chaining=True
    ).outs[0]


def isin_vector(table, values):
    return _build_op(
        Op_isin_vector, [TableType], [table, values], chaining=True
    ).outs[0]


def isnull(table):
    return _build_op(Op_isnull, [TableType], [table], chaining=True).outs[0]


def iloc_scalar(table, index):
    # TODO: support chaining only on input
    return _build_op(Op_iloc_scalar, [Ty_scalar], [table, index]).outs[0]


def join(
    left_tbl,
    right_tbl,
    how,
    on,
    left_on,
    left_index,
    right_on,
    right_index,
    left_suffix,
    right_suffix,
):
    return _build_op(
        Op_join,
        [TableType],
        [
            left_tbl,
            right_tbl,
            how,
            on,
            left_on,
            right_on,
            left_suffix,
            right_suffix,
            create_i1_attr("leftIndex", left_index),
            create_i1_attr("rightIndex", right_index),
        ],
        chaining=True,
    ).outs[0]


def join_with_mask(
    left_tbl,
    right_tbl,
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
    left_no_align=False,
    right_no_align=False,
):
    return _build_op(
        Op_join_with_mask,
        [TableType],
        [
            left_tbl,
            right_tbl,
            how,
            on,
            left_on,
            right_on,
            left_suffix,
            right_suffix,
            left_mask,
            right_mask,
            create_i1_attr("leftIndex", left_index),
            create_i1_attr("leftNoAlign", left_no_align),
            create_i1_attr("rightIndex", right_index),
            create_i1_attr("rightNoAlign", right_no_align),
        ],
        chaining=True,
    ).outs[0]


def loc_setter_with_scalar(
    table, index_or_mask, value, cname, from_non_indexed_arraylike, is_series
):
    return _build_op(
        Op_loc_setter_with_scalar,
        [TableType],
        [
            table,
            index_or_mask,
            value,
            cname,
            create_i1_attr(
                "from_non_indexed_arraylike", from_non_indexed_arraylike
            ),
            create_i1_attr("is_series", is_series),
        ],
        chaining=True,
    ).outs[0]


def if_else_assignment_with_vector(table, mask, value, names):
    return _build_op(
        Op_if_else_assignment_with_vector,
        [TableType],
        [table, mask, value, names],
        chaining=True,
    ).outs[0]


def mask_assignment_with_vector(table, mask, value, names):
    return _build_op(
        Op_mask_assignment_with_vector,
        [TableType],
        [table, mask, value, names],
        chaining=True,
    ).outs[0]


def melt(table, id_vars, value_vars, var_name, value_name, ignore_index):
    return _build_op(
        Op_melt,
        [TableType],
        [
            table,
            id_vars,
            value_vars,
            var_name,
            value_name,
            create_i1_attr("ignore_index", ignore_index),
        ],
        chaining=True,
    ).outs[0]


def project(table, indexer):
    return _build_op(
        Op_project, [TableType], [table, indexer], chaining=True
    ).outs[0]


def quantile(table, q, interpolation):
    return _build_op(
        Op_quantile, [TableType], [table, q, interpolation], chaining=True
    ).outs[0]


def quantile_scalar(table, q, interpolation):
    # TODO: support chaining only on input
    return _build_op(
        Op_quantile_scalar, [Ty_scalar], [table, q, interpolation]
    ).outs[0]


def read_csv(filename, options):
    return _build_op(Op_read_csv, [TableType], [filename, options]).outs[0]


def read_csv_metadata(filename, options):
    return _build_op(
        Op_read_csv_metadata, [MetadataType], [filename, options]
    ).outs[0]


def read_csv_with_metadata(filename, options, metadata):
    return _build_op(
        Op_read_csv_with_metadata, [TableType], [filename, options, metadata]
    ).outs[0]


def read_feather(filename, columns):
    return _build_op(Op_read_feather, [TableType], [filename, columns]).outs[0]


def read_feather_metadata(filename, columns):
    return _build_op(
        Op_read_feather_metadata, [MetadataType], [filename, columns]
    ).outs[0]


def read_feather_with_metadata(filename, columns, metadata):
    return _build_op(
        Op_read_feather_with_metadata,
        [TableType],
        [filename, columns, metadata],
    ).outs[0]


def read_json(filename):
    return _build_op(Op_read_json, [TableType], [filename]).outs[0]


def read_parquet(filename, columns):
    return _build_op(Op_read_parquet, [TableType], [filename, columns]).outs[0]


def read_parquet_metadata(filename, columns):
    return _build_op(
        Op_read_parquet_metadata, [MetadataType], [filename, columns]
    ).outs[0]


def read_parquet_with_metadata(filename, columns, metadata):
    return _build_op(
        Op_read_parquet_with_metadata,
        [TableType],
        [filename, columns, metadata],
    ).outs[0]


def rename(table, cols):
    return _build_op(
        Op_rename,
        [TableType],
        [table, cols],
        implicit_defs=[table],
        chaining=True,
    ).outs[0]


def rename_specified(table, cols, newcols):
    return _build_op(
        Op_rename_specified, [TableType], [table, cols, newcols], chaining=True
    ).outs[0]


def repeat(table, repeats):
    return _build_op(
        Op_repeat, [TableType], [table, repeats], chaining=True
    ).outs[0]


def repeat_vector(table, repeats):
    return _build_op(
        Op_repeat_vector, [TableType], [table, repeats], chaining=True
    ).outs[0]


def set_column_index_names(table, names):
    return _build_op(
        Op_set_column_index_names, [TableType], [table, names], chaining=True
    ).outs[0]


def set_index_names(table, names):
    return _build_op(
        Op_set_index_names, [TableType], [table, names], chaining=True
    ).outs[0]


def set_index(
    table,
    key,
    new_index_column,
    new_index_column_names,
    as_axis,
    as_new,
    drop,
    to_append,
    verify_integrity,
):
    return _build_op(
        Op_set_index,
        [TableType],
        [
            table,
            key,
            new_index_column,
            new_index_column_names,
            create_i1_attr("as_axis", as_axis),
            create_i1_attr("as_new", as_new),
            create_i1_attr("drop", drop),
            create_i1_attr("to_append", to_append),
            create_i1_attr("verify_integrity", verify_integrity),
        ],
        chaining=True,
    ).outs[0]


def shift(table, periods):
    return _build_op(
        Op_shift, [TableType], [table, periods], chaining=True
    ).outs[0]


def slice(table, start, stop, step):
    return _build_op(
        Op_slice, [TableType], [table, start, stop, step], chaining=True
    ).outs[0]


def replace_scalar(table, to_replace, value, regex):
    return _build_op(
        Op_replace_scalar,
        [TableType],
        [table, to_replace, value, create_i1_attr("regex", regex)],
        chaining=True,
    ).outs[0]


def reset_index(table, allow_duplicates, drop, is_series):
    return _build_op(
        Op_reset_index,
        [TableType],
        [
            table,
            create_i1_attr("allow_duplicates", allow_duplicates),
            create_i1_attr("drop", drop),
            create_i1_attr("is_series", is_series),
        ],
        chaining=True,
    ).outs[0]


def rolling_aggregate(table, window, min_periods, funcs):
    return _build_op(
        Op_rolling_aggregate,
        [TableType],
        [
            table,
            window,
            min_periods,
            funcs,
        ],
        chaining=True,
    ).outs[0]


def setitem(table, cols, rhs, ignore_index):
    return _build_op(
        Op_setitem,
        [TableType],
        [
            table,
            cols,
            rhs,
            create_i1_attr("ignore_index", ignore_index),
        ],
        implicit_defs=[table],
        chaining=True,
    ).outs[0]


def sort_index(table, orders, ignore_index, is_series, na_pos, stable):
    return _build_op(
        Op_sort_index,
        [TableType],
        [
            table,
            orders,
            create_i1_attr("ignore_index", ignore_index),
            create_i1_attr("is_series", is_series),
            create_i1_attr("na_pos", na_pos),
            create_i1_attr("stable", stable),
        ],
        chaining=True,
    ).outs[0]


def sort_values(table, keys, orders, ignore_index, is_series, na_pos, stable):
    return _build_op(
        Op_sort_values,
        [TableType],
        [
            table,
            keys,
            orders,
            create_i1_attr("ignore_index", ignore_index),
            create_i1_attr("is_series", is_series),
            create_i1_attr("na_pos", na_pos),
            create_i1_attr("stable", stable),
        ],
        chaining=True,
    ).outs[0]


# CategoricalAccessor


def cat_categories(table):
    return _build_op(
        Op_cat_categories,
        [TableType],
        [table],
        chaining=True,
    ).outs[0]


# String


def str_contains(table, contains, ignore_case, na, regex):
    return _build_op(
        Op_str_contains,
        [TableType],
        [
            table,
            contains,
            create_i1_attr("ignore_case", ignore_case),
            create_i32_attr("na", na),
            create_i1_attr("regex", regex),
        ],
        chaining=True,
    ).outs[0]


def str_concat(left, right, sep):
    return _build_op(
        Op_str_concat, [TableType], [left, right, sep], chaining=True
    ).outs[0]


def str_replace(table, pat, repl, n, regex):
    return _build_op(
        Op_str_replace,
        [TableType],
        [
            table,
            pat,
            repl,
            n,
            create_i1_attr("regex", regex),
        ],
        chaining=True,
    ).outs[0]


def str_endswith(table, pat, na):
    return _build_op(
        Op_str_endswith,
        [TableType],
        [table, pat, create_i32_attr("na", na)],
        chaining=True,
    ).outs[0]


def str_slice(table, start, stop, end, as_element):
    return _build_op(
        Op_str_slice,
        [TableType],
        [table, start, stop, end, create_i1_attr("as_element", as_element)],
        chaining=True,
    ).outs[0]


def str_split(table, pat, n, expand, regex, reverse):
    return _build_op(
        Op_str_split,
        [TableType],
        [
            table,
            pat,
            n,
            create_i1_attr("expand", expand),
            create_i1_attr("regex", regex),
            create_i1_attr("reverse", reverse),
        ],
        chaining=True,
    ).outs[0]


def str_startswith(table, pat, na):
    return _build_op(
        Op_str_startswith,
        [TableType],
        [table, pat, create_i32_attr("na", na)],
        chaining=True,
    ).outs[0]


def str_pad(table, width, side, fillchar):
    return _build_op(
        Op_str_pad, [TableType], [table, width, side, fillchar], chaining=True
    ).outs[0]


def str_trim(table, to_strip, side):
    return _build_op(
        Op_str_trim, [TableType], [table, to_strip, side], chaining=True
    ).outs[0]


def str_trim_wsp(table, side):
    return _build_op(
        Op_str_trim_wsp, [TableType], [table, side], chaining=True
    ).outs[0]


def str_unary_method(table, method):
    return _build_op(
        Op_str_unary_method, [TableType], [table, method], chaining=True
    ).outs[0]


def str_unary_bool_returning_method(table, method):
    return _build_op(
        Op_str_unary_bool_returning_method,
        [TableType],
        [table, method],
        chaining=True,
    ).outs[0]


def take(
    table,
    indices,
    axis,
    check_boundary,
    check_negative,
    ignore_index,
    is_scalar,
):
    op = Op_take_rows if axis == 0 else Op_take_cols
    return _build_op(
        op,
        [TableType],
        [
            table,
            indices,
            create_i1_attr("check_boundary", check_boundary),
            create_i1_attr("check_negative", check_negative),
            create_i1_attr("ignore_index", ignore_index),
            create_i1_attr("is_scalar", is_scalar),
        ],
        chaining=True,
    ).outs[0]


def to_csv(
    table,
    sep,
    na_rep,
    header,
    index,
    quoting_style,
):
    return _build_op(
        Op_to_csv,
        [StringType],
        [
            table,
            sep,
            na_rep,
            create_i1_attr("header", header),
            create_i1_attr("index", index),
            create_i32_attr("quoting_style", quoting_style),
        ],
        chaining=True,
    ).outs[0]


def value_counts(table, sort, ascending, dropna, normalize, is_series):
    return _build_op(
        Op_value_counts,
        [TableType],
        [
            table,
            # NOTE: all attributes should be ordered alphabetically
            create_i1_attr("ascending", ascending),
            create_i1_attr("dropna", dropna),
            create_i1_attr("is_series", is_series),
            create_i1_attr("normalize", normalize),
            create_i1_attr("sort", sort),
        ],
        chaining=True,
    ).outs[0]


def where_scalar(table, cond, other, axis, condIsSeries):
    return _build_op(
        Op_where_scalar,
        [TableType],
        [
            table,
            cond,
            other,
            axis,
            create_i1_attr("cond_is_series", condIsSeries),
        ],
        chaining=True,
    ).outs[0]


def where_table(table, cond, other, axis, condIsSeries):
    return _build_op(
        Op_where_table,
        [TableType],
        [
            table,
            cond,
            other,
            axis,
            create_i1_attr("cond_is_series", condIsSeries),
        ],
        chaining=True,
    ).outs[0]


def write_csv(
    table,
    filename,
    sep,
    na_rep,
    header,
    index,
    quoting_style,
):
    return _build_op(
        Op_write_csv,
        [],
        [
            table,
            filename,
            sep,
            na_rep,
            create_i1_attr("header", header),
            create_i1_attr("index", index),
            create_i32_attr("quoting_style", quoting_style),
        ],
        chaining=True,
    ).outs[0]


def write_parquet(table, filename, options):
    return _build_op(
        Op_write_parquet,
        [],
        [table, filename, options],
        chaining=True,
    ).outs[0]


def abs(table):
    return _build_op(Op_abs, [TableType], [table], chaining=True).outs[0]


def negate(table):
    return _build_op(Op_negate, [TableType], [table], chaining=True).outs[0]


def unary_op(table, func):
    return _build_op(
        Op_unary_op, [TableType], [table, func], chaining=True
    ).outs[0]


def round(table, ndigits):
    return _build_op(
        Op_round, [TableType], [table, ndigits], chaining=True
    ).outs[0]


# Utils


def make_column_name_element_scalar(arg):
    return _build_op(
        Op_make_column_name_element_scalar, [ColumnNameElementType], [arg]
    ).outs[0]


def make_column_name_element_vector(args):
    return _build_op(
        Op_make_column_name_element_vector, [ColumnNameElementType], args
    ).outs[0]


def make_column_name_scalar(arg):
    return _build_op(Op_make_column_name_scalar, [ColumnNameType], [arg]).outs[
        0
    ]


def make_column_name_vector(args):
    return _build_op(Op_make_column_name_vector, [ColumnNameType], args).outs[
        0
    ]


def make_null_scalar_null():
    return _build_op(Op_make_null_scalar_null, [Ty_scalar], []).outs[0]


def make_scalar_f32(src: float):
    src = fireducks.core.make_available_value(src, F32Type)
    return _build_op(Op_make_scalar_f32, [Ty_scalar], [src]).outs[0]


def make_scalar_f64(src: float):
    return _build_op(Op_make_scalar_f64, [Ty_scalar], [src]).outs[0]


def make_scalar_i1(src: bool):
    return _build_op(Op_make_scalar_i1, [Ty_scalar], [src]).outs[0]


def make_scalar_i32(src: int):
    src = fireducks.core.make_available_value(src, I32Type)
    return _build_op(Op_make_scalar_i32, [Ty_scalar], [src]).outs[0]


def make_scalar_i64(src: int):
    return _build_op(Op_make_scalar_i64, [Ty_scalar], [src]).outs[0]


def make_scalar_ui64(src: int):
    src = fireducks.core.make_available_value(src, U64Type)
    return _build_op(Op_make_scalar_ui64, [Ty_scalar], [src]).outs[0]


def make_scalar_str(src: str):
    return _build_op(Op_make_scalar_str, [Ty_scalar], [src]).outs[0]


def make_scalar_time64_us(src: int):
    return _build_op(Op_make_scalar_time64_us, [Ty_scalar], [src]).outs[0]


def make_scalar_timestamp_ns(src: int):
    return _build_op(Op_make_scalar_timestamp_ns, [Ty_scalar], [src]).outs[0]


def make_scalar_binary(src: str):
    return _build_op(Op_make_scalar_binary, [Ty_scalar], [src]).outs[0]


def make_scalar_duration_ns(src: int):
    return _build_op(Op_make_scalar_duration_ns, [Ty_scalar], [src]).outs[0]


def make_null_scalar_f32():
    return _build_op(Op_make_null_scalar_f32, [Ty_scalar], []).outs[0]


def make_null_scalar_f64():
    return _build_op(Op_make_null_scalar_f64, [Ty_scalar], []).outs[0]


def make_null_scalar_timestamp_ns():
    return _build_op(Op_make_null_scalar_timestamp_ns, [Ty_scalar], []).outs[0]


def make_null_scalar_duration_ns():
    return _build_op(Op_make_null_scalar_duration_ns, [Ty_scalar], []).outs[0]


def make_tuple_column_name(args):
    tmp = ", ".join([ColumnNameType.mlir_type for _ in args])
    ty = fire.Type(f"tuple<{tmp}>")
    return _build_op(Op_make_tuple_column_name, [ty], args).outs[0]


def make_tuple_i1(args):
    tmp = ", ".join(["i1"] * len(args))
    ty = fire.Type(f"tuple<{tmp}>")
    return _build_op(Op_make_tuple_i1, [ty], args).outs[0]


def make_tuple_scalar(args):
    tmp = ", ".join(["!fireducks.scalar" for _ in args])
    ty = fire.Type(f"tuple<{tmp}>")
    return _build_op(Op_make_tuple_scalar, [ty], args).outs[0]


def make_tuple_table(args):
    tmp = ", ".join(["!fireducks.table" for _ in args])
    ty = fire.Type(f"tuple<{tmp}>")
    return _build_op(Op_make_tuple_table, [ty], args).outs[0]


def make_tuple_str(args):
    tmp = ", ".join(["!tfrt.string" for _ in args])
    ty = fire.Type(f"tuple<{tmp}>")
    return _build_op(Op_make_tuple_str, [ty], args).outs[0]


def make_tuple_of_vector_or_scalar_of_str(args):
    tmp = ", ".join(["!fireducks.vector_or_scalar_of_str" for _ in args])
    ty = fire.Type(f"tuple<{tmp}>")
    return _build_op(Op_make_tuple_vector_or_scalar_of_str, [ty], args).outs[0]


def make_vector_or_scalar_of_column_name_from_scalar(arg):
    return _build_op(
        Op_make_vector_or_scalar_of_column_name_from_scalar,
        [VectorOrScalarOfColumnNameType],
        [arg],
    ).outs[0]


def make_vector_or_scalar_of_column_name_from_vector(arg):
    return _build_op(
        Op_make_vector_or_scalar_of_column_name_from_vector,
        [VectorOrScalarOfColumnNameType],
        arg,
    ).outs[0]


def make_vector_or_scalar_of_scalar_from_scalar(arg):
    return _build_op(
        Op_make_vector_or_scalar_of_scalar_from_scalar,
        [VectorOrScalarOfScalarType],
        [arg],
    ).outs[0]


def make_vector_or_scalar_of_scalar_from_vector(arg):
    return _build_op(
        Op_make_vector_or_scalar_of_scalar_from_vector,
        [VectorOrScalarOfScalarType],
        arg,
    ).outs[0]


def make_vector_or_scalar_from_scalar_str(arg: str):
    return _build_op(
        Op_make_vector_or_scalar_from_scalar_str,
        [VectorOrScalarOfStrType],
        [arg],
    ).outs[0]


def make_vector_or_scalar_from_vector_str(arg):
    return _build_op(
        Op_make_vector_or_scalar_from_vector_str,
        [VectorOrScalarOfStrType],
        arg,
    ).outs[0]


def make_nullopt_string():
    return _build_op(Op_make_nullopt_string, [OptionalStringType], []).outs[0]


def make_optional_string(value):
    return _build_op(
        Op_make_optional_string, [OptionalStringType], [value]
    ).outs[0]


def make_nullopt_table():
    return _build_op(Op_make_nullopt_table, [OptionalTableType], []).outs[0]


def make_optional_table(table):
    return _build_op(
        Op_make_optional_table, [OptionalTableType], [table], chaining=True
    ).outs[0]


# Python


def to_pandas(table):
    return _build_op(Op_to_pandas, [Ty_pyobj], [table], chaining=True).outs[0]


def to_pandas_series(table):
    return _build_op(
        Op_to_pandas_series, [Ty_pyobj], [table], chaining=True
    ).outs[0]


def to_datetime(table, str_format, errors):
    return _build_op(
        Op_to_datetime, [TableType], [table, str_format, errors], chaining=True
    ).outs[0]


def to_numpy(table):
    return _build_op(Op_to_numpy, [Ty_pyobj], [table], chaining=True).outs[0]


def unique(table):
    return _build_op(Op_unique, [Ty_pyobj], [table], chaining=True).outs[0]


def to_frame(table, cname, to_rename):
    return _build_op(
        Op_to_frame,
        [TableType],
        [table, cname, create_i1_attr("to_rename", to_rename)],
        chaining=True,
    ).outs[0]


def print_table(table):
    return _build_op(Op_print_table, [], [table], chaining=True).outs[0]


def from_pandas_frame_metadata(df, metadata):
    return _build_op(
        Op_from_pandas_frame_metadata, [TableType], [df, metadata]
    ).outs[0]


def to_pandas_frame_metadata(df):
    return _build_op(
        Op_to_pandas_frame_metadata,
        [Ty_pyobj, MetadataType],
        [df],
        chaining=True,
    ).outs[0:2]
