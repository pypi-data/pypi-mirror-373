# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import functools


def nohook(func):
    """A decorator to disable import hooks.

    In a function or method (and all descendent calls from them) with
    this decorator, all import hooks are disabled.

    """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return _wrapper
