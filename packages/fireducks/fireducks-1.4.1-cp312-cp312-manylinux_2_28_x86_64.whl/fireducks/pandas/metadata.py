# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from datetime import datetime
import logging

import numpy as np
import pandas

from fireducks.fireducks_ext import Scalar
import fireducks.pandas.utils as utils
from fireducks import ir

logger = logging.getLogger(__name__)


class IRMetadataWrapper:
    """
    This class is a wrapper of a metadata defined by IR.

    This class provide convenient methods to use IR metadata.

    In this document, following example is used.

    >>> df
    Month       Jan                 Feb
    Day         Mon       Tue       Mon       Tue
    ABC
    a      0.476154  0.803732  0.520757  0.170070
    b      0.363055  0.919802  0.135537  0.755907
    c      0.939023  0.999877  0.596680  0.628549
    """

    def __init__(self, meta):
        self.meta = meta

    @property
    def column_names(self):
        """
        Column names
        """
        return self.meta.column_names

    @property
    def num_col(self):
        """
        Number of columns
        """
        return len(self.meta.column_names)

    # Map from fireducks IR data type to pandas dtype.
    # Pandas changes data type when null, missing values, exists.
    #
    # Reference:
    #   [1] https://numpy.org/doc/stable/reference/arrays.scalars.html
    #   [2] https://pandas.pydata.org/docs/user_guide/basics.html#dtypes

    class DtypeInfo:
        def __init__(self, dtype, nullable=True, nulltype=None):
            self.dtype = dtype
            self.nullable = nullable
            nulltype = nulltype or np.dtype(np.float64)
            self.nulltype = dtype if nullable else nulltype

    _dtype_info_map = {
        "bool": DtypeInfo(np.dtype(np.bool_), False, np.dtype(np.object_)),
        "int8": DtypeInfo(np.dtype(np.int8), False),
        "int16": DtypeInfo(np.dtype(np.int16), False),
        "int32": DtypeInfo(np.dtype(np.int32), False),
        "int64": DtypeInfo(np.dtype(np.int64), False),
        "uint8": DtypeInfo(np.dtype(np.uint8), False),
        "uint16": DtypeInfo(np.dtype(np.uint16), False),
        "uint32": DtypeInfo(np.dtype(np.uint32), False),
        "uint64": DtypeInfo(np.dtype(np.uint64), False),
        "halffloat": DtypeInfo(np.dtype(np.float16)),
        "float": DtypeInfo(np.dtype(np.float32)),
        "double": DtypeInfo(np.dtype(np.float64)),
        "utf8": DtypeInfo(np.dtype(np.object_)),
        "large_utf8": DtypeInfo(np.dtype(np.object_)),
        "date32": DtypeInfo(np.dtype(np.object_)),
        "list": DtypeInfo(np.dtype(np.object_)),
        "timestamp": DtypeInfo(np.dtype("datetime64[ns]")),
        "duration[s]": DtypeInfo(np.dtype("timedelta64[s]")),
        "duration[ms]": DtypeInfo(np.dtype("timedelta64[ms]")),
        "duration[us]": DtypeInfo(np.dtype("timedelta64[us]")),
        "duration[ns]": DtypeInfo(np.dtype("timedelta64[ns]")),
        # pandas, and numpy, supports following data types, but since it can
        # not be converted to arrow, those types are never used here.
        #   - float128
        #   - complex64
        #   - complex128
        #   - complex256
        # Category types are "dictionary" in fireducks IR data type as arrow.
        # Because pandas's CategoricalDtype has categories, i.e.  values of
        # dictionary and it can not be created only from metadata, it is not in
        # the map. It is taken care differently inside '_get_dtypes()'.
    }

    def _get_dtypes(self, data):
        """
        Data types of columns
        """

        def get_timestamp_dtype(col):
            unit = "ns" if pandas.__version__ < "2" else col.unit

            if len(col.timezone) == 0:
                return np.dtype(f"datetime64[{unit}]")
            else:
                import pytz

                if col.timezone[0] in ["+", "-"]:
                    from datetime import datetime

                    # Parse "+09:00" as UTC offset format and convert to minutes
                    minutes = (
                        datetime.strptime(col.timezone, "%z")
                        .tzinfo.utcoffset(None)
                        .total_seconds()
                        / 60
                    )
                    tz_obj = pytz.FixedOffset(minutes)
                else:
                    tz_obj = pytz.timezone(col.timezone)

                return pandas.api.types.DatetimeTZDtype(unit, tz=tz_obj)

        def get_dtype(col_idx, unsupported):
            col = self.meta.additional_column_metadata_vector[col_idx]
            if col.dtype == "timestamp":
                dtype_obj = get_timestamp_dtype(col)
                info = IRMetadataWrapper.DtypeInfo(dtype_obj)
            elif col.dtype.startswith("dictionary"):
                from fireducks.pandas.series import Series

                # Currently it returns pandas.CategoricalDtype() with
                # 'category' of type pandas.Index (instead of fireducks.Index)
                # TODO: To avoid such a mixed dtype issue (fireducks methods
                # returning pandas object), Wrap pandas.CategoricalDtype.
                s = data if isinstance(data, Series) else data.iloc[:, col_idx]
                dtype_obj = pandas.CategoricalDtype(
                    Series._create(ir.cat_categories(s._value)).to_pandas(),
                    ordered=col.is_ordered_categorical_column,
                )
                info = IRMetadataWrapper.DtypeInfo(dtype_obj)
            else:
                info = IRMetadataWrapper._dtype_info_map.get(col.dtype)
                if info is None:
                    unsupported += [col.dtype]
                    return None

            return info.dtype if col.null_count == 0 else info.nulltype

        unsupported = []
        dtypes = [
            get_dtype(col_idx, unsupported) for col_idx in range(self.num_col)
        ]
        if len(unsupported) > 0:
            return None, unsupported
        idx = (
            pandas.MultiIndex.from_tuples(self.meta.column_names)
            if self.meta.is_multi_level_column_index
            else self.meta.column_names
        )
        return pandas.Series(dtypes, index=idx), []

    def _get_raw_dtypes(self) -> list[str]:
        """
        Return raw dtypes as list of strings.
        """
        out = []
        acmv = self.meta.additional_column_metadata_vector
        for col in acmv:
            if col.dtype == "halffloat":
                t = "float16"
            elif col.dtype == "float":
                t = "float32"
            elif col.dtype == "double":
                t = "float64"
            else:
                t = col.dtype
            out.append(t)
        return out

    def create_column_index(self):
        """
        Return column index as pandas class.

        >>> Example
        col_names = [('Jan', 'Mon'), ('Jan', 'Tue'), ...]
        idx_names = ['Month', 'Day']
        """
        col_names = self.meta.column_names
        idx_names = self.meta.column_index_names
        if self.meta.is_multi_level_column_index:
            return pandas.MultiIndex.from_tuples(col_names, names=idx_names)
        return pandas.Index(col_names, name=idx_names[0], tupleize_cols=False)

    # row index
    def apply_index_metadata(self, df):
        assert self.meta.additional_index_metadata is not None
        index_metadata = self.meta.additional_index_metadata

        # At least table has one index as pandas assigns RangeIndex
        assert len(index_metadata.indexes) > 0

        indexes = []
        to_be_drop = []
        for index in index_metadata.indexes:
            if index.is_range_index:
                r = index.range
                indexes += [
                    pandas.RangeIndex(r.start, r.stop, r.step, name=index.name)
                ]
            else:
                to_be_drop += [index.pos]
                s = df.iloc[:, index.pos]
                if isinstance(index.name, list):
                    # If index.name is list, it is multiindex.
                    indexes += [pandas.Index(s, name=tuple(index.name))]
                else:
                    # If index.name is None, use rename().
                    indexes += [pandas.Index(s.rename(index.name))]

        df = df.drop(df.columns[to_be_drop], axis=1)

        if (
            not self.meta.is_multilevel_row_index
        ):  # index_metadata.isMultiLevel:
            if len(indexes) > 1:
                raise RuntimeError("multiple indexes with isMultiLevel=False")
            indexes = indexes[0]

        df.index = indexes
        return df

        # `df.set_index` does not work when length of df and indexes are
        # different. This happens when df is empty.
        # return df.set_index(indexes)

    def apply(self, df: pandas.DataFrame):
        """
        Apply this metadata to the given dataframe.
        """
        df = self.apply_index_metadata(df)
        columnAsRange = False
        if len(df.columns) == 0 and not self.meta.is_multi_level_column_index:
            if utils._pd_version_under2:
                # This case we use RangeIndex as pandas. See GT #1363
                columnAsRange = isinstance(df.index, pandas.RangeIndex)
            else:
                """
                df = pandas.DataFrame()
                pandas 2.2
                    df.index        :  RangeIndex(start=0, stop=0, step=1)
                    df.columns      :  RangeIndex(start=0, stop=0, step=1)
                pandas 1.5.3
                    df.index        :  Index([], dtype='object')
                    df.columns      :  Index([], dtype='object')
                """
                columnAsRange = True

        df.columns = (
            pandas.RangeIndex(0, 0, 1)
            if columnAsRange
            else self.create_column_index()
        )

        return df

    def is_column_name(self, name):
        """
        Test if name is a column name.
        """
        return name in self.meta.column_names


def make_scalar(name) -> Scalar:
    """
    Create C++ fireducks::Scalar from python object

    See MainModule.cc to know which type of python object is allowed.
    """

    if isinstance(name, datetime):
        return Scalar.from_datetime(name)
    elif isinstance(name, pandas.Timestamp):
        return Scalar.from_timestamp(name)
    elif isinstance(name, pandas.Timedelta):
        return Scalar.from_timedelta(name)
    elif isinstance(name, bytes):
        return Scalar.from_bytes(name)
    else:
        return Scalar(name)
