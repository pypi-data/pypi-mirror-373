# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import argparse
import errno
import logging
import os.path
import re
import runpy
import shutil
import sys
import textwrap

from . import HookPair, activate_hook_pairs
from ._util import get_logger, get_logging_handler

STDINARG = "-"
DUMMYARG = "--"
MODULEOPT = "-m"

IMPORTAS_PATTERN = r"""(?x:
    (?:import\s+)?                              # 'import'
    (?!(?:as|import)(?:[^.\w]|\Z))([.\w]+)      # a module name
    (?:
        \s+as\s+                                # 'as'
        (?!(?:as|import)(?:[^.\w]|\Z))([.\w]+)  # an alias
    )?
)"""


class NoArgumentError(ValueError):
    def __init__(self, msg="cannot find an argument to execute"):
        super().__init__(msg)


def split_args(args):
    """Split arguments for hooks and for the target program."""

    n = len(args)
    i = j = k = n + 1

    # find a dummy argument
    dindices = iter(index for index, arg in enumerate(args) if arg == DUMMYARG)
    pos = next(dindices, n)
    if pos + 1 < n:
        i, j = pos, pos + 1

    # find a module option
    # fmt: off
    mindices = iter(
        index
        for index, arg in enumerate(args)
        if arg.startswith(MODULEOPT)
    )
    # fmt: on
    pos = next(mindices, n)
    if pos < n:
        if args[pos] == MODULEOPT and pos + 1 < n:
            k = pos + 2
        else:
            k = pos + 1
        if k < i:
            i = j = k

    if i <= n and j <= n:
        return args[:i], args[j:]

    # find a file or a directory
    findices = iter(
        index
        for index, arg in enumerate(args)
        if arg == STDINARG or os.path.exists(arg)
    )
    pos = next(findices, n)

    if pos < n:
        return args[:pos], args[pos:]

    # give up
    raise NoArgumentError()


def parse_args(args):
    description = f"""
        Hook import mechanisms and execute the following python program.

        By specifying 'import egg.spam as spam' for a hook argument, an
        import statement 'import spam' in the target python program
        behaves itself like 'import egg.spam as spam'.
        In other words, 'egg.spam' substitutes for 'spam' without
        modifying the target python program.

        The 'import' keyword is just optional and there is no difference
        in behavior with or without it.
        If the 'as ...' clause is not specified, the name of the most
        descendent module specified in the 'import ...' clause is used
        for the identifier to be bound to the module.
        For example, 'egg.bacon.sausage.spam' is the same to
        'import egg.bacon.sausage.spam as spam'.
        To specify multiple hooks, concatenate them with commas (or
        delimiters specified by a '--delimiter' option).
        For example, 'egg.bacon, egg.sausage, egg.spam'.

        A '{DUMMYARG}' separates hooks and the target python program.
        If '{DUMMYARG}' is not given, the first argument which is an
        existing file is set to the target python program.
    """

    nn = "\n\n"
    nbsp = chr(0xA0)
    nregex = re.compile(r"\n\n+")
    sregex = re.compile(r"\s+")
    qregex = re.compile(r"'[^']*'")

    columns = shutil.get_terminal_size().columns
    wrapper = textwrap.TextWrapper(
        width=(columns - 2),
        initial_indent=(" " * 2),
        subsequent_indent=(" " * 2),
    )

    def _nobreak_replacer(m):
        return m.group().replace(" ", nbsp).replace("-", "_")

    def _nobreak_reverter(m):
        return m.group().replace("_", "-").replace(nbsp, " ")

    def _descformatter(s):
        s = s.strip()
        s = sregex.sub(" ", s)
        s = qregex.sub(_nobreak_replacer, s)
        s = wrapper.fill(s)
        s = qregex.sub(_nobreak_reverter, s)
        return s

    description = nn.join(map(_descformatter, nregex.split(description)))

    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        MODULEOPT,
        metavar="mod",
        dest="module",
        help="run the specified module under the import-hook",
    )
    parent.add_argument(
        "hooks",
        metavar="hook",
        nargs="+",
        help=(
            "a module name and an alias to hook, in a format like import "
            "statements: '[import] egg.spam [as spam]'"
        ),
    )
    parent.add_argument(
        "--delimiter",
        metavar="CHAR",
        default=",",
        help="a delimiter for multiple hooks (default: '%(default)s')",
    )
    parent.add_argument(
        "--hook-import-module",
        action="store_true",
        help="also hook the function importlib.import_module",
    )

    logopts = parent.add_argument_group("logging options")
    # fmt: off
    logopts.add_argument(
        "-q", "--quiet",
        action="count",
        default=0,
        help="raise a quiet level of logs",
    )
    logopts.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="raise a verbose level of logs",
    )
    logopts.add_argument(
        "--suppress-logs",
        action="store_true",
        help="do not print logs to STDERR",
    )
    # fmt: on

    # a dummy parser is to print help messages
    dummyparser = argparse.ArgumentParser(
        prog=__package__,
        description=description,
        parents=[parent],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    dummyparser.add_argument(
        "sep",
        metavar=DUMMYARG,
        nargs="?",
        help="a separator of arguments",
    )
    dummyparser.add_argument(
        "prog",
        help="the python program to execute",
    )
    dummyparser.add_argument(
        "arg",
        nargs="*",
        help="arguments for the python program to execute",
    )
    usage = dummyparser.format_usage()

    # a help parser is only to get -h/--help
    helper = argparse.ArgumentParser(add_help=False, usage=usage)
    helper.add_argument("-h", "--help", action="store_true")

    # split arguments
    args = list(args)
    try:
        args, remain_args = split_args(args)
    except NoArgumentError as e:
        namespace, _ = helper.parse_known_args(args)
        if namespace.help:
            dummyparser.print_help()
            dummyparser.exit(0)
        dummyparser.error(str(e))

    namespace, _ = helper.parse_known_args(args)
    if namespace.help:
        dummyparser.print_help()
        dummyparser.exit(0)

    # actual parser
    parser = argparse.ArgumentParser(parents=[parent], usage=usage)
    namespace = parser.parse_args(args)

    # parse hook arguments
    pairs = list()
    iregex = re.compile(IMPORTAS_PATTERN)
    hookargs = " ".join(namespace.hooks)
    hookstrs = hookargs.split(namespace.delimiter)
    for hookstr in filter(None, map(str.strip, hookstrs)):
        match = iregex.fullmatch(hookstr)
        if match:
            pairs.append(HookPair(*match.groups()))
        else:
            dummyparser.error(f"invalid hooks: {hookstr!r}")
    if not pairs:
        dummyparser.error(f"invalid hooks: {hookargs!r}")

    namespace.pairs = pairs
    del namespace.delimiter, namespace.hooks
    return namespace, remain_args


def run_module(mod_name, args):
    sys.argv = [mod_name] + args
    runpy.run_module(mod_name, run_name=__name__, alter_sys=True)


def run_file(args):
    if len(args) == 0:
        raise NoArgumentError()

    filename = args[0]
    if os.path.isdir(filename):
        # TODO: support executing a directory of which path contains separators
        run_module(filename, args[1:])
        return

    if filename == STDINARG:
        filename = "<stdin>"
        target = sys.stdin.fileno()
    else:
        target = filename

    if not os.path.exists(target):
        raise FileNotFoundError(errno.ENOENT, "No such file", target)

    closefd = not isinstance(target, int)
    with open(target, mode="r", closefd=closefd) as f:
        text = f.read()

    code_object = compile(text, filename=filename, mode="exec")
    sys.path.insert(0, os.path.dirname(filename))

    sys.argv = args
    exec(code_object, globals(), globals())


def main():
    """Hook imports and execute the following python program."""

    args, remain_args = parse_args(sys.argv[1:])

    logger = get_logger()
    quiet_level = args.quiet - args.verbose
    if quiet_level < -2:
        loglevel = logging.NOTSET
    elif quiet_level > 2:
        loglevel = logging.WARNING + quiet_level * 10
    else:
        loglevel = (
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        )[quiet_level + 2]
    logger.setLevel(loglevel)
    if not args.suppress_logs:
        logger.addHandler(get_logging_handler())
    del args.quiet, args.verbose, args.suppress_logs

    mod_name = args.module
    del args.module

    activate_hook_pairs(**vars(args))

    if mod_name:
        run_module(mod_name, remain_args)
    else:
        run_file(remain_args)


if __name__ == "__main__":
    main()
