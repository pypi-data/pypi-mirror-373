# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import builtins
import collections
import importlib
import importlib.machinery
import inspect
import os
import os.path
import sys
from itertools import product, takewhile

from . import _decorator
from ._decorator import nohook
from ._util import get_logger

import firefw.runtime

__all__ = ["nohook", "get_logger"]

SEP = "."
INIT = "__init__.py"
CACHE = "__pycache__"

# fmt: off
HookPair = collections.namedtuple(
    "HookPair", ["import_name", "as_name"]
)

HookEntry = collections.namedtuple(
    "HookEntry", ["import_name", "import_path", "as_name", "as_path"]
)
# fmt: on


# for ImportHook.ignore_names
def _get_default_ignore_names():
    suffixes = importlib.machinery.all_suffixes()

    result = []
    top = os.path.dirname(__file__)
    gtor = os.walk(top, topdown=True, followlinks=False)
    for dirpath, dirnames, filenames in gtor:
        for filename in filenames:
            if any(filename.endswith(s) for s in suffixes):
                result.append(os.path.join(dirpath, filename))
        if CACHE in dirnames:
            dirnames.remove(CACHE)

    result.remove(_decorator.__file__)
    # TODO: to skip ipyext enable next line. NOT TESTED
    # result.append(importlib.util.find_spec("fireducks.ipyext", None).origin)
    return result


class ImportHook:
    # genuine functions
    __import__ = builtins.__import__
    __importlib_import__ = importlib.__import__
    __import_module__ = importlib.import_module

    # filters for stack frames
    ignore_names = _get_default_ignore_names()
    ignore_words = ["frozen importlib"]

    # stoppers for stack frames
    stop_modules = ["IPython.core.interactiveshell"]

    # nohook
    nohook_modules = ["dask", "cudf"]

    def __init__(
        self,
        ignore_names=None,
        ignore_words=None,
        stop_modules=None,
        nohook_modules=None,
    ):
        cls = self.__class__
        if inspect.currentframe() is None:  # pragma: no cover
            get_logger().warning(
                "WARNING: The function inspect.currentframe() is not "
                "available on the current Python environment. This may cause "
                "importhook to be slow."
            )

        self._hooks = dict()

        self._ignames = cls.ignore_names[:]
        self._ignames.extend(ignore_names or [])
        self._igwords = cls.ignore_words[:]
        self._igwords.extend(ignore_words or [])

        self._stoppers = []
        stop_names = cls.stop_modules[:]
        stop_names.extend(stop_modules or [])
        for name in stop_names:
            self.add_stopper(name)

        self._nohooks = [_decorator.__file__]
        nohook_names = cls.nohook_modules[:]
        nohook_names.extend(nohook_modules or [])
        for name in nohook_names:
            self.add_nohook(name)

        self._debug = cls._is_debug_enabled()

    @staticmethod
    def _is_debug_enabled():
        import logging

        return get_logger().isEnabledFor(logging.DEBUG)

    def add_hook(self, import_, as_=None):
        """Add import hook.

        `add_hook(import_='egg.spam', as_='spam')` is an analogy of
        `import egg.spam as spam`.

        By setting `import_='egg.spam', as_='spam'` and activating this
        hook, an import statement `import spam` behaves itself like
        `import egg.spam as spam`. If `as_` is `None`, the name of the
        most descendent module of `import_` is used for `as_`.

        """

        cls = self.__class__
        import_name = import_
        as_name = as_

        if as_name is None:
            left, sep, right = import_name.rpartition(SEP)
            if right != import_name:
                as_name = right
            else:
                raise ValueError(
                    f"'as_' is not given but 'import_' has "
                    f"no child module: {import_name!r}"
                )

        amodule = cls.__import_module__(as_name)
        imodule = cls.__import_module__(import_name)
        left, sep, right = import_name.partition(SEP)
        if left != import_name:
            imodule = cls.__import_module__(left)

        as_path = amodule.__file__.removesuffix(INIT)
        as_path = os.path.abspath(as_path)
        import_path = imodule.__file__.removesuffix(INIT)
        import_path = os.path.abspath(import_path)

        entry = HookEntry(import_name, import_path, as_name, as_path)
        self._hooks[entry.as_name] = entry

        get_logger().info(repr(entry))
        return self

    def add_nohook(self, name, strict=False):
        """Add a module not to hook."""
        modpath = self._get_modulepath(name, strict)
        if modpath:
            self._nohooks.append(modpath)

    def add_stopper(self, name, strict=False):
        """Add a module to stop tracing stack frames."""
        modpath = self._get_modulepath(name, strict)
        if modpath:
            self._stoppers.append(modpath)

    def activate(self, hook_import_module=False):
        def _targets():
            return [
                builtins.__import__,
                importlib.__import__,
                importlib.import_module,
            ]

        before_hook = tuple(map(repr, _targets()))

        builtins.__import__ = self
        importlib.__import__ = self
        if hook_import_module:
            importlib.import_module = self.import_module

        after_hook = tuple(map(repr, _targets()))

        logger = get_logger()
        for s, t in zip(before_hook, after_hook):
            if s != t:
                logger.info(f"{s} is hooked by {t}")

    @classmethod
    def deactivate(cls):
        builtins.__import__ = cls.__import__
        importlib.__import__ = cls.__importlib_import__
        importlib.import_module = cls.__import_module__
        get_logger().info("an import hook is deactivated")

    def is_active(self):
        x = builtins.__import__ is self
        y = importlib.__import__ is self

        if (x and not y) or (not x and y):
            logger = get_logger()
            logger.error(f"builtins.__import__:  {builtins.__import__!r}")
            logger.error(f"importlib.__import__: {importlib.__import__!r}")
            raise ValueError("invalid importhook state")

        return x and y

    def is_active_for_import_module(self):
        # NOTE: An id of a bound method may differ every time.
        # So even if `foo = obj.method` and `bar = obj.method`,
        # `foo is bar` may be False. Instead of it, an instance
        # `__self__` which binds the method is used.
        return getattr(importlib.import_module, "__self__", None) is self

    def _get_modulepath(self, name, strict=False):
        cached = sys.modules.get(name)
        if cached:
            modpath = cached.__file__.removesuffix(INIT)
            return os.path.abspath(modpath)

        modpath = self._find_modulepath(name)
        if modpath:
            modpath = modpath.removesuffix(INIT)
            return os.path.abspath(modpath)

        if strict:
            raise ValueError(f"no such module: {name}")

        return None

    def _find_modulepath(self, fullname):
        finders = filter(
            lambda mpf: callable(getattr(mpf, "find_spec", None)),
            sys.meta_path,
        )

        current, _, remains = fullname.partition(SEP)
        for mpf in finders:
            spec = mpf.find_spec(current, None, None)
            if spec:
                break
        else:
            return None

        if remains:
            for subname in remains.split(SEP):
                search_locs = getattr(spec, "submodule_search_locations", None)
                if not search_locs:
                    return None
                current += SEP + subname
                spec = mpf.find_spec(current, search_locs, None)

        return getattr(spec, "origin", None)

    def _frameleader(self, filename):
        return not any(s == filename for s in self._stoppers)

    def _framefilter(self, filename):
        matches = any(s == filename for s in self._ignames)
        contains = any(s in filename for s in self._igwords)
        return not matches and not contains

    def _get_frames(self, skip=1):
        frames = firefw.runtime.get_frames(skip)
        filenames = map(inspect.getfile, frames)
        leading_filenames = takewhile(self._frameleader, filenames)
        filtered_filenames = filter(self._framefilter, leading_filenames)
        return map(os.path.abspath, filtered_filenames)

    def _to_be_hooked(self, name):
        assert name in self._hooks
        entry = self._hooks[name]

        return all(
            os.path.commonpath([descendant, ancestor]) != ancestor
            for descendant, ancestor in product(
                self._get_frames(2),
                [entry.as_path, entry.import_path] + self._nohooks,
            )
        )

    def __call__(self, name, globals=None, locals=None, fromlist=(), level=0):
        """A wrapper for the built-in function `__import__`."""

        cls = self.__class__
        names = name.split(SEP, maxsplit=1)
        top_name = names[0]

        if self._debug and top_name in self._hooks:
            import pprint

            get_logger().debug(pprint.pformat(list(self._get_frames())))

        # import the original module against fallback of dotted submodules
        orig = cls.__import__(name, globals, locals, fromlist, level)

        if top_name in self._hooks and self._to_be_hooked(top_name):
            entry = self._hooks[top_name]
            alter_name = SEP.join([entry.import_name] + names[1:])
            try:
                if fromlist:
                    ret = cls.__import_module__(alter_name)
                else:
                    ret = cls.__import_module__(entry.import_name)
                get_logger().info(f"hook: {name!r} -> {alter_name!r}")
                return ret
            except ModuleNotFoundError as e:
                # give up trying to hook
                get_logger().info(f"hook failed: no module named {e.name!r}")

        return orig

    def import_module(self, name, package=None):
        """A wrapper for the function `importlib.import_module`."""

        cls = self.__class__
        names = name.split(SEP, maxsplit=1)
        top_name = names[0]

        if top_name in self._hooks and self._to_be_hooked(top_name):
            entry = self._hooks[top_name]
            alter_name = SEP.join([entry.import_name] + names[1:])
            try:
                ret = cls.__import_module__(alter_name, package)
                get_logger().info(f"hook: {name!r} -> {alter_name!r}")
                return ret
            except ModuleNotFoundError as e:
                # give up trying to hook
                get_logger().info(f"hook failed: no module named {e.name!r}")

        return cls.__import_module__(name, package)

    @classmethod
    def _genuine_builtin_import(cls):
        return cls.__import__

    @classmethod
    def _genuine_importlib_import(cls):
        return cls.__importlib_import__

    @classmethod
    def _genuine_import_module(cls):
        return cls.__import_module__


def activate_hook_pairs(pairs, hook_import_module=False):
    """Activate pairs of import hooks."""

    hook = ImportHook()
    for import_name, as_name in pairs:
        hook.add_hook(import_name, as_name)

    hook.activate(hook_import_module)
    return hook


def activate_hook(import_, as_=None, hook_import_module=False):
    """Activate an import hook.

    `activate_hook(import_='egg.spam', as_='spam')` is an analogy of
    `import egg.spam as spam`.

    After this hook is activated, an import statement `import spam`
    behaves itself like `import egg.spam as spam`. If `as_` is `None`,
    the name of the most descendent module of `import_` is used for
    `as_`. For example, `import_='egg.bacon.spam.sausage.without.spam'`
    makes `as_='spam'`.

    By default, the built-in function `__import__` and the function
    `importlib.__import__` are hooked. If `hook_import_module` is
    `True`, the function `importlib.import_module` is also hooked.

    """

    return activate_hook_pairs([HookPair(import_, as_)], hook_import_module)


def deactivate_hook():
    ImportHook.deactivate()


def _get_current_hook():
    hook = builtins.__import__
    if isinstance(hook, ImportHook):
        return hook
    else:
        return None
