# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

"""
This module provide two tracings.

- global tracing: enabled by `FIREDUCKS_FLAGS="--trace=<level>"`. The result
  is stored to the file specified by `--trace-file` at program exit.
- temporal tracing: enabled by :meth:`enable_tracing`. The result
  is returned by :meth:`disable_tracing`.

Both tracings are exclusive.
"""


import atexit
from contextlib import contextmanager
import os

import firefw.tracing
from fireducks.core import get_fireducks_options
import fireducks.fireducks_ext.tracing as ext_tracing
import fireducks.tracing.helper as helper

_is_global_tracing_enabled = False


@contextmanager
def trace(callback=None):
    """
    Context manager for temporal tracing.

    ``callback`` is called with the result of tracing as chrome://tracing json string
    """
    enable_tracing()
    try:
        yield
    finally:
        s = disable_tracing()
        if callback is not None:
            callback(s)


def enable_tracing(level=None):
    """
    Enable temporal tracing
    """
    if _is_global_tracing_enabled:
        raise RuntimeError(
            "global tracing is enabled. tracing.enable_tracing is not available"
        )

    if level is None:
        level = firefw.tracing.Level.DEBUG
    firefw.tracing.enable_tracing(level)


def disable_tracing():
    """
    Disable temporal tracing and return chrome-tracing json string.
    """
    firefw.tracing.disable_tracing()
    return ext_tracing.to_json()


def start_global_tracing(level: str):
    level = firefw.tracing.Level.from_str(level)
    enable_tracing(level)

    global _is_global_tracing_enabled
    _is_global_tracing_enabled = True

    # NOTE: This top level scope is for backward compatibility. Is this
    # required?
    scope = firefw.tracing.TracingScope(firefw.tracing.Level.DEFAULT, "top")

    def finalize():
        scope.pop()
        s = disable_tracing()

        filename = get_fireducks_options().trace_file
        if filename == "-":
            helper.print_profile(s)
        else:
            with open(filename, "w") as f:
                f.write(s)

    atexit.register(finalize)


def init():
    firefw.tracing.init(ext_tracing)

    level = get_fireducks_options().trace_level
    if level is not None:
        start_global_tracing(level)
