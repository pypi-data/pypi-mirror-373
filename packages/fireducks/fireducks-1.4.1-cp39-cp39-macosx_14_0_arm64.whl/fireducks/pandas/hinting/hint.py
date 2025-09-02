# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from __future__ import annotations
from typing import List
import logging

logger = logging.getLogger(__name__)


class ColumnHint:
    """Hint for a column

    Attributes:
        name(name-like): Column name. Always correct.
                         None is allowed as a column name.
    """

    def __init__(self, name):
        self.name = name
        self.nlevels = len(name) if isinstance(name, list) else 1

    def __str__(self) -> str:
        return "ColumnHint" f"(name={self.name},nlevels={self.nlevels})"

    def add_suffix(self, suffix) -> ColumnHint:
        name = self.name
        if isinstance(name, (list, tuple)):
            name = "(" + ", ".join(name) + ")"
        return ColumnHint(name + suffix)


def _get_level(columns: List[ColumnHint]) -> int:
    assert len(columns) > 0
    lv = columns[0].nlevels
    assert all([lv == column.nlevels for column in columns])
    return lv


class ColumnAxisHint:
    """
    Hint on column axis.

    Immutable.

    Number of columns should be always correct.
    """

    def __init__(self, columns: List[ColumnHint], is_multilevel=None):
        assert columns is not None
        self._columns = columns

        if is_multilevel is None:
            assert len(columns) > 0
            self._is_multilevel = _get_level(columns) > 1
        else:
            assert isinstance(is_multilevel, bool)
            # if both columns and is_multilevel are given, those should be
            # consistent
            assert (
                is_multilevel or len(columns) == 0 or _get_level(columns) == 1
            )
            self._is_multilevel = is_multilevel

    def __getitem__(self, index):
        """Return i-th column."""
        return self._columns[index]

    def __iter__(self):
        """Iterate over columns."""
        for col in self._columns:
            yield col

    def __len__(self):
        """Return number of columns."""
        return len(self._columns)

    def __str__(self) -> str:
        return "[" + ",".join([str(col) for col in self._columns]) + "]"

    @property
    def is_multilevel(self):
        """Return true if column axis is multilevel"""
        return self._is_multilevel

    @property
    def nlevels(self):
        """Return number of levels of column axis"""
        return _get_level(self._columns)


class TableHint:
    """
    Hint on a Table defined by IR.

    Immutable.
    """

    def __init__(self, *, columns: ColumnAxisHint = None):
        self._columns = columns

    def __str__(self):
        return f"TableHint(columns={str(self._columns)})"

    @property
    def columns(self) -> ColumnAxisHint:
        """
        Hint on data columns

        Return:
          :class:`ColumnAxisHint` if available, otherwise None.
        """
        return self._columns
