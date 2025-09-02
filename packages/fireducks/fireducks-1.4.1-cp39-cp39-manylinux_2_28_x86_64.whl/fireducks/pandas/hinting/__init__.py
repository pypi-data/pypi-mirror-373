# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

"""
This module provides hints for a frontend.

Hint can be accessed by :attr:`fireducks.pandas.DataFrame._fireducks_hint`.
"""

from fireducks.pandas.hinting.ops import (
    create_hint_from_pandas_frame,
    infer_project,
    is_column_name,
)

__all__ = (
    "create_hint_from_pandas_frame",
    "infer_project",
    "is_column_name",
)
