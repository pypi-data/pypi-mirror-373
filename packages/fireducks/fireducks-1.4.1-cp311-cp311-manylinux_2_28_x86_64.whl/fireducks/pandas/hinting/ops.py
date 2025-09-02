# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import logging

from typing import List, Optional

import numpy as np
import pandas
from fireducks.pandas.metadata import make_scalar
from fireducks.fireducks_ext import (
    Metadata,
    Scalar,
    ColumnMetadata,
    ColumnName,
)
from fireducks.fireducks_ext.metadata import (
    project,
)

from fireducks.pandas.hinting.hint import ColumnAxisHint, ColumnHint, TableHint

logger = logging.getLogger(__name__)


def _ensure_list(obj):
    return obj if isinstance(obj, list) else [obj]


def _is_supported_index(index):
    """
    This module does not support some index type.

    Ex:
        - `infer_project` dose not support:
            * `df["1/1/2000"]` on PeriodIndex.
            * `df[0.5] on IntervalIndex.from_breaks(np.arange(5))`
    """
    supported_dtypes = (
        np.bool_,
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
        np.object_,  # expect string, not python object
        # pandas.core.arrays.string_.StringDtype # Should we add this?
    )
    return index.dtype in supported_dtypes


def create_hint_from_pandas_frame(df: pandas.DataFrame) -> Optional[TableHint]:
    """Create a hint from pandas.DataFrame"""

    if not _is_supported_index(df.columns):
        return None

    isMultiLevel = isinstance(df.columns, pandas.MultiIndex)
    names = [list(name) if isMultiLevel else name for name in df.columns]
    columns = [ColumnHint(name) for name in names]
    return TableHint(
        columns=ColumnAxisHint(columns, is_multilevel=isMultiLevel)
    )


def create_hint_from_metadata(meta: Optional[Metadata]) -> Optional[TableHint]:
    """Create a hint from fireducks.fireducks_ext.Metadata"""

    if meta is None:
        return None

    names = [name for name in meta.column_names]
    columns = [ColumnHint(name) for name in names]
    return TableHint(
        columns=ColumnAxisHint(columns, meta.is_multi_level_column_index)
    )


def make_ext_column_name(name) -> ColumnName:
    """Create C++ fireducks::ColumnName from column name in a hint"""

    # In TableHint, list in column name means multilevel
    # multilevel with tuple element is not supported yet. Ex: ["a", ("b", "c")]
    if isinstance(name, list):
        return ColumnName.MultiFromScalars([make_scalar(e) for e in name])

    if isinstance(name, (frozenset, tuple)):  # single-level ("a", "b")
        return ColumnName.SingleFromScalars([make_scalar(e) for e in name])

    return ColumnName.Single(make_scalar(name))


def create_metadata_from_hint(hint: TableHint) -> Metadata:
    assert hint is not None
    assert hint.columns is not None

    column_names = [make_ext_column_name(col.name) for col in hint.columns]
    columns = [ColumnMetadata(name) for name in column_names]

    # make dummy column_index_names because TableHint does not have it.
    if hint.columns.is_multilevel:
        column_index_names = ColumnName.MultiFromScalars(
            [Scalar(None) for _ in range(hint.columns.nlevels)]
        )
    else:
        column_index_names = ColumnName.Single(Scalar(None))

    # make dummy is_multi_level_row_index because TableHint does not have index
    # columns
    is_multi_level_row_index = False
    return Metadata(columns, column_index_names, is_multi_level_row_index)


def create_vector_or_scalar_of_column_name(names):
    from fireducks.fireducks_ext import VectorOrScalarOfColumnNames

    def make_column_name(name):
        assert not isinstance(name, list)
        if isinstance(name, (frozenset, tuple)):
            return ColumnName.SingleFromScalars([make_scalar(k) for k in name])
        return ColumnName.Single(make_scalar(name))

    if isinstance(names, list):
        scalars = [make_column_name(name) for name in names]
        return VectorOrScalarOfColumnNames.make_vector(scalars)

    return VectorOrScalarOfColumnNames.make_scalar(make_column_name(names))


def infer_project(hint: TableHint, keys) -> Optional[TableHint]:
    """Infer TableHint for a project op.

    Args:
      keys (key-like): projection keys

    Returns:
      TableHint:
    """
    logger.debug("infer_project: hint=%s keys=%s", hint, keys)
    if hint is None or hint.columns is None:
        return None

    metadata = create_metadata_from_hint(hint)
    tmp = create_vector_or_scalar_of_column_name(keys)
    projected = project(metadata, tmp, False)  # ignoreMissing=False
    return create_hint_from_metadata(projected)


def is_column_name(hint: TableHint, name) -> bool:
    """Return True if name is a column name, False if not or unknown."""
    if hint is None or hint.columns is None:
        return False

    return any([col.name == name for col in hint.columns])
