# Copyright (c) 2025 NEC Corporation. All Rights Reserved.

import os
import glob
import pathlib
import sys
import logging

from pandas.io.common import is_url, is_fsspec_url

from firefw import tracing

with tracing.scope(tracing.Level.DEFAULT, "import pandas"):
    import pandas
    import pandas.api.extensions as pandas_extensions

from fireducks import ir, irutils, is_enterprise
import fireducks.core
from fireducks.pandas.api import concat
from fireducks.pandas.frame import DataFrame
import fireducks.pandas.utils as utils

import fireducks.pandas.hinting.ops as hinting

logger = logging.getLogger(__name__)

#
# Utility methods
#


def _check_if_supported_dtype_backend(dtype_backend):
    if (
        dtype_backend is not pandas_extensions.no_default
        and dtype_backend not in {"pyarrow"}
    ):
        return f"unsupported dtype_backend: '{dtype_backend}'"
    return None


def _check_if_supported_path(path, param_name, allow_dict=False):
    if not isinstance(path, (str, pathlib.PosixPath, pathlib.WindowsPath)):
        return f"{param_name} is not supported filepath", path

    reason = None
    path = os.path.expanduser(path)
    if os.path.isdir(path):
        if allow_dict:
            dir_contents = glob.glob(os.path.join(path, "*"))
            if any([os.path.isdir(e) for e in dir_contents]):
                reason = "path is a directory containing other directories"
        else:
            reason = "path is directory"
    elif is_url(path):
        reason = "path is url"
    elif is_fsspec_url(path):
        reason = "seems like fsspec path"

    return reason, path


def _check_if_supported_columns(columns, empty_list_as_none=True):
    reason = None
    columns_ = columns

    if columns is None:
        columns_ = []
    elif isinstance(columns, str):
        columns_ = [columns]
    elif isinstance(columns, list):
        if len(columns) == 0:
            if not empty_list_as_none:
                reason = "'columns' is an empty list"
        else:
            if not irutils._is_str_list(columns):
                reason = "'columns' is not a list-of-strings"
    else:
        reason = "unsupported 'columns' of type: {type(columns).__name__}"

    return reason, columns_


#
# PANDAS IO API
#


def read_csv(*args, **kwargs):
    decoded = utils.decode_args(args, kwargs, pandas.read_csv)
    names = decoded.names
    filepath_or_buffer = decoded.filepath_or_buffer
    index_col = decoded.index_col
    usecols = decoded.usecols
    dtype = decoded.dtype
    sep = decoded.sep
    delimiter = decoded.delimiter
    header = decoded.header

    if isinstance(header, bool):
        raise TypeError(
            "Passing a bool to header is invalid. Use header=None for no "
            "header or header=int or list-like of ints to specify the "
            "row(s) making up the column names"
        )

    reason, path = _check_if_supported_path(
        filepath_or_buffer, "filepath_or_buffer", allow_dict=False
    )

    if not reason and not utils._pd_version_under2:
        reason = _check_if_supported_dtype_backend(decoded.dtype_backend)

    if not reason:
        if (
            names is not pandas_extensions.no_default
            and not irutils._is_str_list(names)
        ):
            reason = "names is not a list of string"
        elif usecols is not None and not irutils._is_str_list(usecols):
            reason = "usecols is not a list of string"
        elif (
            header is not None
            and header != "infer"
            and not isinstance(header, int)
        ):
            reason = "unsupported header of type: '{type(header)}'"
        elif (
            dtype is not None
            and not isinstance(dtype, dict)
            and not utils.is_supported_dtype(dtype)
        ):
            reason = f"dtype is not supported: {dtype}"
        elif decoded.encoding not in (None, "utf-8", "utf8", "UTF-8", "UTF8"):
            reason = f"unsupported encoding: {decoded.encoding}"
        elif isinstance(dtype, dict):
            for key, typ in dtype.items():
                if not isinstance(key, str):
                    reason = f"column name of dtype is not string: {key}"
                elif not utils.is_supported_dtype(typ):
                    reason = f"dtype is not supported: {typ}"
            if hasattr(dtype, "default_factory"):  # defaultdict
                default_dtype = dtype.default_factory()
                if not utils.is_supported_dtype(default_dtype):
                    reason = f"default dtype is not supported: {default_dtype}"

    if reason is None and index_col is not None:
        if isinstance(index_col, bool):
            reason = "index_col is of boolean-type"
        else:  # bool is instance of int
            index_col = (
                [index_col] if isinstance(index_col, int) else index_col
            )
            if not irutils._is_list_of(index_col, int):
                reason = "index_col is not None, integer or list-of-integers"

    if decoded.comment is not None and (
        header is not None and header != "infer" and header != 0
    ):
        # 2025/08/13(ishizaka): `header` is implemented by using `skiprows` in
        # current implementation. In dfklbe, comment lines are not ignored by
        # `skiprows` as pandas, for example, no valid lines are skipped when
        # there are three comment lines before valid lines and skiprows=3. But
        # `header` ignores comment lines. Due to this difference, comment with
        # non-trivial header is fallback.
        reason = "comment is not supported with non-trivial header"

    if reason is None:
        exclude_args = [
            "names",
            "filepath_or_buffer",
            "index_col",
            "usecols",
            "dtype",
            "sep",
            "delimiter",
            "header",
            "encoding",
        ]

        if is_enterprise:
            # fallback at frontend to avoid double fallbacks-in-dfklbe for
            # read_csv_metadata and read_csv
            exclude_args.append("comment")

        if not utils._pd_version_under2:
            exclude_args.append("dtype_backend")
        reason = decoded.is_not_default(exclude=exclude_args)

    if reason is None:
        if header != "infer" and usecols is not None:
            reason = "usecols with header is provided"

    if reason is not None:
        return utils.fallback_call(
            utils._get_pandas_module,
            "read_csv",
            args,
            kwargs,
            reason=reason,
        )

    # when include_columns is empty, all columns are returned
    include_columns = [] if usecols is None else usecols

    from fireducks.fireducks_ext import ReadCSVOptions

    if isinstance(header, int) and header < 0:
        raise ValueError(
            "Passing negative integer to header is invalid. For no header, use header=None instead"
        )

    options = ReadCSVOptions()
    if decoded.comment is not None:
        # NOTE: comment in fireducks is not completely same as pandas. See
        # doc of ReadCSVOptions.
        #
        # pandas does not support multiple characters even though dfklbe
        # supports it.
        if len(decoded.comment) > 1:
            raise ValueError("Only length-1 comment characters supported")
        options.comment = decoded.comment

    # based on understanding of relationship between header and skiprows: #3385
    if names is not pandas_extensions.no_default:  # with names
        if len(names) != len(set(names)):
            raise ValueError("Duplicate names are not allowed.")
        options.names = names
        options.skiprows = (
            0 if header is None or header == "infer" else header + 1
        )
    else:  # without names
        if header is None:
            options.skiprows = 0
            options.autogenerate_column_names = True
        else:
            options.skiprows = 0 if header == "infer" else header

    if index_col is not None:
        options.index_col = index_col
    if include_columns:
        options.include_columns = include_columns
    if delimiter is None:
        delimiter = sep
    if delimiter is pandas_extensions.no_default:
        delimiter = ","
    options.delimiter = delimiter

    if isinstance(dtype, dict):
        for k, v in dtype.items():
            options.set_column_type(k, utils.to_supported_dtype(v))
        if hasattr(dtype, "default_factory"):  # defaultdict
            options.default_dtype = utils.to_supported_dtype(
                dtype.default_factory()
            )
    elif dtype is not None:
        options.default_dtype = utils.to_supported_dtype(dtype)

    options = fireducks.core.make_available_value(
        options, ir.ReadCSVOptionsType
    )

    if fireducks.core.get_ir_prop().has_metadata:
        value_meta = ir.read_csv_metadata(path, options)
        meta = fireducks.core.evaluate([value_meta])[0]
        _hint = hinting.create_hint_from_metadata(meta)
        value = ir.read_csv_with_metadata(path, options, value_meta)
        return DataFrame._create(value, hint=_hint)
    else:
        value = ir.read_csv(path, options)
        return DataFrame._create(value)


def _read_file(path, columns_, file_format):
    assert file_format in ("parquet", "feather")

    method_prefix = f"read_{file_format}"
    meta_reader, data_reader_with_meta, data_reader = (
        f"{method_prefix}_metadata",
        f"{method_prefix}_with_metadata",
        f"{method_prefix}",
    )
    columns = irutils.make_tuple_of_column_names(columns_)
    if fireducks.core.get_ir_prop().has_metadata:
        value_meta = getattr(ir, meta_reader)(path, columns)
        meta = fireducks.core.evaluate([value_meta])[0]
        _hint = hinting.create_hint_from_metadata(meta)
        value = getattr(ir, data_reader_with_meta)(path, columns, value_meta)
        return DataFrame._create(value, hint=_hint)

    value = getattr(ir, data_reader)(path, columns)
    return DataFrame._create(value)


def read_feather(*args, **kwargs):
    decoded = utils.decode_args(args, kwargs, pandas.read_feather)
    path = decoded.path
    columns = decoded.columns

    reason = []
    stat, path = _check_if_supported_path(path, "path", allow_dict=False)
    if stat is not None:
        reason += [stat]

    stat, columns_ = _check_if_supported_columns(
        columns, empty_list_as_none=True
    )
    if stat is not None:
        reason += [stat]

    if not utils._pd_version_under2:
        stat = _check_if_supported_dtype_backend(decoded.dtype_backend)
        if stat is not None:
            reason += [stat]

    exclude_args = ["path", "columns"]
    if not utils._pd_version_under2:
        exclude_args.append("dtype_backend")
    no_default = decoded.is_not_default(exclude=exclude_args)
    if no_default:
        reason += [no_default]

    if len(reason) > 0:
        return utils.fallback_call(
            utils._get_pandas_module,
            "read_feather",
            args,
            kwargs,
            reason="; ".join(reason),
        )
    return _read_file(path, columns_, file_format="feather")


def read_json(*args, **kwargs):
    decoded = utils.decode_args(args, kwargs, pandas.read_json)
    reason = None

    path_or_buf = decoded.path_or_buf
    lines = decoded.lines

    reason, path = _check_if_supported_path(
        path_or_buf, "path_or_buf", allow_dict=False
    )

    if not reason and not lines:
        reason = "target is not a new-line terminated json file"

    if reason is None:
        exclude = ["path_or_buf", "lines"]
        if not utils._pd_version_under2:
            exclude.append("engine")
        reason = decoded.is_not_default(exclude=exclude)

    if reason is not None:
        return utils.fallback_call(
            utils._get_pandas_module,
            "read_json",
            args,
            kwargs,
            reason=reason,
        )

    value = ir.read_json(path)
    return DataFrame._create(value)


def read_parquet(*args, **kwargs):
    decoded = utils.decode_args(args, kwargs, pandas.read_parquet)
    path = decoded.path
    engine = decoded.engine
    columns = decoded.columns

    reason = []
    # engine=pyarrow should be supported?
    if engine not in {"auto", "pyarrow"}:
        reason += [f"unsupported engine: '{engine}'"]

    stat, path = _check_if_supported_path(path, "path", allow_dict=True)
    if stat is not None:
        reason += [stat]

    stat, columns_ = _check_if_supported_columns(
        columns, empty_list_as_none=False
    )
    if stat is not None:
        reason += [stat]

    if not utils._pd_version_under2:
        stat = _check_if_supported_dtype_backend(decoded.dtype_backend)
        if stat is not None:
            reason += [stat]

    exclude_args = ["path", "engine", "columns"]
    if not utils._pd_version_under2:
        exclude_args.append("dtype_backend")
    no_default = decoded.is_not_default(exclude=exclude_args)
    if no_default:
        reason += [no_default]

    if len(reason) > 0:
        return utils.fallback_call(
            utils._get_pandas_module,
            "read_parquet",
            args,
            kwargs,
            reason="; ".join(reason),
        )

    if os.path.isdir(path):
        loaded_data = []
        dir_contents = glob.glob(os.path.join(path, "*"))
        for file in sorted(dir_contents):
            loaded_data.append(
                _read_file(file, columns_, file_format="parquet")
            )
        return concat(loaded_data)
    return _read_file(path, columns_, file_format="parquet")


def to_parquet(df, *args, **kwargs):
    def fallback_call(reason):
        return df._fallback_call(
            "to_parquet",
            args,
            kwargs,
            reason="; ".join(reason),
        )

    if not isinstance(df, DataFrame):
        raise ValueError("to_parquet only supports IO with DataFrames")

    if not is_enterprise:
        return fallback_call(
            reason="to_parquet is not supported in community edition"
        )

    arg = utils.decode_args(args, kwargs, pandas.DataFrame.to_parquet)

    reason = []
    # engine=pyarrow should be supported?
    if arg.engine not in {"auto", "pyarrow"}:
        reason += [f"unsupported engine: '{arg.engine}'"]

    if not isinstance(arg.path, (str, os.PathLike)):
        reason += ["path_or_buf is not str"]

    if arg.compression not in (None, "snappy"):
        reason += ["Only None and 'snappy' are supported for compression."]

    exclude_args = ["path", "engine", "compression", "index"]
    no_default = arg.is_not_default(exclude=exclude_args)
    if no_default:
        reason += [no_default]

    if len(reason) > 0:
        return fallback_call(reason=reason)

    from fireducks.fireducks_ext import WriteParquetOptions

    options = WriteParquetOptions()

    # evaluate before creating metadata
    fireducks.core.evaluate([df._value])

    # create a 0-rows pandas DataFrame
    header_pandas_df = df.head(0).to_pandas()

    # make metadata to embed into parquet-file using pyarrow
    import pyarrow.pandas_compat

    _, schema, _ = pyarrow.pandas_compat.dataframe_to_arrays(
        header_pandas_df, None, arg.index
    )
    options.metadata = schema.metadata[b"pandas"].decode(encoding="utf-8")

    file_path = (
        arg.path.__fspath__()
        if isinstance(arg.path, os.PathLike)
        else arg.path
    )

    options.compression = (
        "None" if arg.compression is None else arg.compression
    )
    options.preserve_index = arg.index in (None, True)
    options.keep_range = arg.index is None

    options = fireducks.core.make_available_value(
        options, ir.WriteParquetOptionsType
    )

    result = ir.write_parquet(
        df._value,
        file_path,
        options,
    )

    try:
        ret = fireducks.core.evaluate([result])
    except Exception as e:  # RuntimeError etc. at backend
        reason = f"{type(e).__name__}: {e}. Falling back to pandas."
        return df._fallback_call("to_parquet", args, kwargs, reason=reason)

    return ret[0]


def to_pickle(obj, *args, **kwargs):
    logger.debug("to_pickle")
    pandas.to_pickle(utils._unwrap(obj), *args, **kwargs)


def _get_pandas_io_api_module(reason=None):
    return pandas.api


# Borrow unknown module attributes from pandas
def __getattr__(name):
    logger.debug("Borrow %s from pandas.io.api", name)
    if name in ["__path__", "__spec__"]:
        return object.getattr(sys.modules[__name__], name)
    reason = f"borrow {name} from pandas.io.api"
    return utils.fallback_attr(_get_pandas_io_api_module, name, reason=reason)
