# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

"""
This module provides fallback

Notes
-----
This module should be moved to firefw package in the future.
"""

from contextlib import contextmanager
import functools
import inspect
import logging
import time
import types
import warnings
from typing import List, Optional

from firefw import runtime, tracing

from fireducks.errors import FallbackWarning

logger = logging.getLogger(__name__)


class FallbackChecker:
    def on_fallback(self):
        """
        Called on each fallback
        """
        pass

    def on_exit(self):
        """
        Called on exit of the context manager.
        """
        pass


class ProhibitFallbackChecker(FallbackChecker):
    def __init__(
        self,
        raises: bool,
        targets: Optional[List[str]] = None,
    ):
        """
        Parameters
        ----------
        raises : bool
            When True, RuntimeError is raised on fallback, otherwise this
            checker raises no error.
        targets: List[str] | None
            Any of fallbacks in the list raises an error. When None, all
            fallbacks raises an error.
        """
        self.raises = raises
        self.targets = targets

    def is_targets(self, attr: str):
        if self.targets is None:
            return True
        return any([t == attr for t in self.targets])

    def on_fallback(self, attr: str, msg: str):
        if self.raises and self.is_targets(attr):
            raise RuntimeError(f"fallback prohibited: {msg}")


class EnforceFallbackChecker(FallbackChecker):
    def __init__(self, targets: Optional[List[str]] = None):
        """
        Parameters
        ----------
        enforce: bool
            When True, AssertionError raises when no fallback occurs.
        targets: List[str] | None
            When List, AssertionError is raised when any of fallbacks in the
            list do not occurs.
            When None, AssertionError is raises when no fallback occurs.
        """
        self.has_fallback = False
        self.occurred = {k: False for k in targets or []}

    def on_exit(self):
        assert self.has_fallback, "No fallback"

        no_fallbacks = [k for k, v in self.occurred.items() if not v]
        assert not no_fallbacks, f"No fallback for {', '.join(no_fallbacks)}"

    def on_fallback(self, attr: str, msg: str):
        self.has_fallback = True
        if attr in self.occurred:
            self.occurred[attr] = True


class FallbackCheckerStack:
    def __init__(self):
        self.stack: List[FallbackChecker] = []

    def peek(self):
        if not self.stack:
            return None
        return self.stack[-1]

    def push(self, checker: FallbackChecker):
        self.stack.append(checker)

    def pop(self):
        assert self.stack, "No FallbackChecker to pop"
        return self.stack.pop(-1)


# singleton
_fallback_checker_stack = FallbackCheckerStack()


def _get_fallback_checker_stack():
    global _fallback_checker_stack

    return _fallback_checker_stack


def _fallback_checker_on_fallback(attr, msg: str):
    c = _get_fallback_checker_stack().peek()
    if c is not None:
        c.on_fallback(attr, msg)


@contextmanager
def setting_fallback_checker(checker: FallbackChecker):
    stack = _get_fallback_checker_stack()
    stack.push(checker)
    try:
        yield
    finally:
        checker.on_exit()
        stack.pop()


@contextmanager
def prohibit_fallback(
    raises: bool = True, *, targets: Optional[List[str]] = None
):
    c = ProhibitFallbackChecker(raises=raises, targets=targets)
    with setting_fallback_checker(c):
        yield


@contextmanager
def enforce_fallback(*, targets: Optional[List[str]] = None):
    c = EnforceFallbackChecker(targets=targets)
    with setting_fallback_checker(c):
        yield


@contextmanager
def prohibit_or_enforce_fallback(
    *,
    prohibit: bool,
    targets: Optional[List[str]] = None,
):
    """
    Execute code with prohibiting fallback or enforcing fallback.

    Example
    -------
    This function is typically used with `is_enterprise` like this:

    >>> with prohibit_or_enforce_fallback(prohibit=is_enterprise):
    ...     # do something which has no fallback in enterprise edition and works
    ...     # with fallback in community edition.
    """

    assert isinstance(prohibit, bool)
    if prohibit:
        with prohibit_fallback(targets=targets):
            yield
    else:
        with enforce_fallback(targets=targets):
            yield


def find_user_frame(package="fireducks"):
    for frame in runtime.get_frames(2):
        module = inspect.getmodule(frame)
        if module is None or not module.__name__.startswith(package):
            return frame
    return None


def get_attr_long_name(owner, name):
    if hasattr(owner, "__name__"):  # ex: pandas
        return f"{owner.__name__}.{name}"
    elif hasattr(owner, "__class__"):  # ex: DataFrame
        return f"{owner.__class__.__name__}.{name}"
    return name


class FallbackWarningBuilder:
    def __init__(self, name, reason, warn_fallback):
        self.reason = reason
        self.warn_fallback = warn_fallback
        if warn_fallback:
            self.start_time = time.time()
            self.name = name
            self.timings = {}

    @contextmanager
    def timing(self, key):
        if self.warn_fallback:
            t0 = time.time()
            yield
            self.timings[key] = time.time() - t0
        else:
            yield

    def warn(self, owner, stacklevel):
        if self.warn_fallback:
            tot = time.time() - self.start_time
            name = get_attr_long_name(owner, self.name)
            timings = " ".join(
                [f"{k} {v:.6f}" for k, v in self.timings.items()]
            )
            warnings.warn(
                f"{name} {tot:.6f} sec {timings} {self.reason}",
                FallbackWarning,
                stacklevel=stacklevel,
            )


def fallback_attr(
    fallbacker,
    name,
    reason=None,
    *,
    stacklevel=0,
    wrap_func=None,
    unwrap_func=None,
    log_lineno=False,
    warn_fallback=False,
):
    """
    Fallback attribute reference.

    Parameters
    ----------
    fallbacker: Callable which returns the object having the attribute.
    name:       Name of attribute
    reason:     Reason of fallback for logging
    stacklevel: Depth from user code for warning
    """
    warn_builder = FallbackWarningBuilder(name, reason, warn_fallback)

    at = ""
    if log_lineno:
        frame = find_user_frame()
        if frame is not None:
            at = f"at={inspect.getfile(frame)}:{frame.f_lineno}"
        else:
            at = "at=unknown"

    _fallback_checker_on_fallback(
        name, f"fallback_attr: attr={name}: {reason}"
    )

    with warn_builder.timing("getobj"):
        obj = fallbacker(reason=reason)

    logger.debug(
        "fallback_attr: name=%s reason=%s %s",
        get_attr_long_name(obj, name),
        reason,
        at,
    )

    with warn_builder.timing("getattr"):
        with tracing.scope(tracing.Level.VERBOSE, f"fallback:getattr:{name}"):
            # to support attribute chain: e.g. getattr(df, "iloc.__setitem__")
            attr = obj
            for nm in name.split("."):
                attr = getattr(attr, nm)

    if isinstance(attr, (types.MethodType, types.FunctionType)):

        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            if isinstance(attr, types.MethodType):
                fullname = f"{type(attr.__self__).__name__}.{name}"
                logger.debug(
                    "fallback_attr.wrapper: call method `%s.%s` on %x",
                    type(attr.__self__).__name__,
                    name,
                    id(attr.__self__),
                )
            else:
                fullname = name
                logger.debug("fallback_attr.wrapper: call %s", name)
            reason = "argument for fallback"

            with warn_builder.timing("args"):
                args = unwrap_func(args, reason=reason)
                kwargs = unwrap_func(kwargs, reason=reason)

            with warn_builder.timing("call"):
                with tracing.scope(
                    tracing.Level.VERBOSE, f"fallback:{fullname}"
                ):
                    ret = attr(*args, **kwargs)

            ret = wrap_func(ret)
            lv = stacklevel or 3
            warn_builder.warn(obj, stacklevel=lv)
            return ret

        return wrapper
    else:
        lv = stacklevel or 5
        warn_builder.warn(obj, stacklevel=lv)

    logger.debug("fallback_attr: return attr for %s: %s", name, type(attr))
    return wrap_func(attr)


def fallback_call(
    fallbacker,
    method,
    args=None,
    kwargs=None,
    *,
    reason=None,
    stacklevel=6,
    wrap_func=None,
    unwrap_func=None,
    log_lineno=False,
    warn_fallback=False,
):
    """
    Fallback a method call with packed arguments: args and kwargs.

    After resolving attribute, call it with arguments.

    Parameters
    ----------
    args, kwargs: Arguments passed to the method
    stacklevel:   Level from user code to warnings.warn
    """
    method = fallback_attr(
        fallbacker,
        method,
        reason,
        stacklevel=stacklevel,
        wrap_func=wrap_func,
        unwrap_func=unwrap_func,
        log_lineno=log_lineno,
        warn_fallback=warn_fallback,
    )
    assert callable(method)
    args = [] if args is None else args
    kwargs = {} if kwargs is None else kwargs
    # fallback_attr returns a wrapper for _wrap, _unwap. we can simply call a
    # method
    return method(*args, **kwargs)
