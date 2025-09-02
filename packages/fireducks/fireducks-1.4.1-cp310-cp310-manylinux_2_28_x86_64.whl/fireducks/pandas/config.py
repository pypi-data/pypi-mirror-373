# This module provides wrappers for pandas.options to implements special
# handling for FireDucks. This module is not intended to be fully compatible
# with pandas._config module because it should not be public API.

from contextlib import ContextDecorator
import inspect
import os
import warnings

import pandas


# copied from pandas/util/_exceptions.py and modified
def find_stack_level() -> int:
    """
    Find the first place in the stack that is not inside pandas
    (tests notwithstanding).
    """

    import fireducks.pandas as pd

    pkg_dir = os.path.dirname(pd.__file__)
    test_dir = os.path.join(pkg_dir, "tests")

    # https://stackoverflow.com/questions/17407119/python-inspect-stack-is-slow
    frame: FrameType | None = inspect.currentframe()
    try:
        n = 0
        while frame:
            filename = inspect.getfile(frame)
            if filename.startswith(pkg_dir) and not filename.startswith(
                test_dir
            ):
                frame = frame.f_back
                n += 1
            else:
                break
    finally:
        # See note in
        # https://docs.python.org/3/library/inspect.html#inspect.Traceback
        del frame
    return n


def handle_pandas_option(name, value) -> bool:
    """If return False, option will be passed to pandas"""
    if name == "mode.use_inf_as_na":
        warnings.warn(
            "use_inf_as_na option is not supported by FireDucks."
            " Convert inf values to NaN before operating instead.",
            stacklevel=find_stack_level(),
        )
        return True

    return False


def filter_options(args):
    if len(args) == 0 or len(args) % 2 != 0:
        return args

    forward_args = []
    for pat, val in zip(args[::2], args[1::2]):
        if not handle_pandas_option(pat, val):
            forward_args += [pat, val]

    return forward_args


class option_context(ContextDecorator):
    def __init__(self, *args):
        self.args = args
        self.context = None

    def __enter__(self) -> None:
        filtered = filter_options(self.args)
        if len(self.args) == 0 or len(filtered) > 0:
            self.context = pandas.option_context(*filtered)
            self.context.__enter__()

    def __exit__(self, *args) -> None:
        if self.context is not None:
            self.context.__exit__(*args)


class PandasOptionsWrapper:
    def __init__(self, po=None):
        object.__setattr__(self, "_pandas_options", po)

    def __setattr__(self, key: str, value):
        po = object.__getattribute__(self, "_pandas_options")
        prefix = object.__getattribute__(po, "prefix")
        if prefix:
            prefix += "."
        prefix += key
        handled = handle_pandas_option(prefix, value)
        if not handled:
            setattr(po, key, value)

    def __getattr__(self, key: str):
        from pandas._config.config import DictWrapper

        po = object.__getattribute__(self, "_pandas_options")
        value = getattr(po, key)
        if isinstance(value, DictWrapper):
            return PandasOptionsWrapper(value)
        return value


def set_option(*args):
    filtered = filter_options(args)
    if len(args) == 0 or len(filtered) > 0:
        import pandas._config.config as cf

        # To pass the tests in pandas2_tests/tests/config/test_config.py, we
        # have to use cf.set_option here instead of pandas.set_option. Usually
        # pandas.set_option is equal to cf.set_option, but when cf.set_option
        # is used in cf.config_prefix context as in the test, those are
        # different.
        cf.set_option(*filtered)


options = PandasOptionsWrapper(pandas.options)


# For pandas2_tests/tests/config/test_config.py, attributes which are not
# pandas public API are also imported from pandas.
def __getattr__(name):
    from pandas._config import config as cf

    return getattr(cf, name)
