# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import argparse
from contextlib import contextmanager
import logging
import os
from typing import List

import pandas.errors

import firefw as fire
from firefw import tracing

from fireducks import fireducks_ext

logger = logging.getLogger(__name__)


class EvalOptions:
    """Evaluation options.

    Evaluation options can be changed upon each evaluation.

    At the moment, this options is intended to internal use.
    """

    def __init__(self, inherit_default=True):
        self._compile_options = fireducks_ext.FireDucksCompileOptions()
        self.prohibit_evaluation = False  # For test
        self._eval_logger_manager = None

        if inherit_default:
            src = (
                get_fireducks_options()._default_eval_options._compile_options
            )
            self._compile_options.target = src.target
            # inherit more options if you need

    def set_pass_options(self, name: str, enabled: bool, options: str = None):
        opts = fireducks_ext.PassOptions()
        opts.enabled = enabled
        opts.options = options or ""

        pass_options = self._compile_options.pass_options  # returns copy
        pass_options[name] = opts
        self._compile_options.pass_options = pass_options
        return self

    def get_pass_options(self, name: str):
        return self._compile_options.pass_options.get(name)

    def _set_eval_logger_manager(self, manager: "EvalLoggerManager"):
        self._eval_logger_manager = manager
        return self


class _FireDucksIRProperty:
    """Global constant IR property.

    IR property is not changed during lifetime of process.

    has_series : bool
      True if IR supports pandas-like series.

    has_metadata: bool
      True if IR supports a metadata.

    NOTE: At the moment, we change IRProperty depending on a backend.
    """

    def __init__(self):
        logger.debug("_FireDucksIRProperty.__init__")
        self.has_metadata = False
        self.has_series = True


def parse_fireducks_flags(flags, namespace=None):
    parser = argparse.ArgumentParser(
        prog="FIREDUCKS_FLAGS", formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--benchmark-mode",
        action="store_true",
        dest="_benchmark_mode",
        help="Enable benchmark mode",
    )

    # Log line number when fallback when True.
    # (efault is False because of non-negligible overhead
    parser.add_argument(
        "--fallback-lineno",
        action="store_true",
        help="Show line number on fallback log",
    )

    parser.add_argument(
        "--fireducks-version",
        action="store_true",
        help="pd.__version__ returns fireducks version",
    )

    # Fast fallback is allowed when True.
    # When it is allowed and other conditions are met, fast fallback is
    # used to minimize fallback overhead by:
    #   - no check if fallback is prohibited
    #   - no logger
    #   - no trace
    #   - no unwrap and wrap
    # Note that other conditions depends on methods and should be checked
    # at fallback site.
    parser.add_argument(
        "--no-fast-fallback",
        action="store_false",
        dest="fast_fallback",
        help="Disable fast fallback",
    )

    parser.add_argument(
        "--trace",
        type=str,
        default=None,
        dest="trace_level",
        help="Enable tracing. 0-3",
    )

    parser.add_argument(
        "--trace-file",
        type=str,
        default="trace.json",
        help="filename to store trace",
    )

    parser.add_argument(
        "-Wfallback",
        action="store_true",
        dest="warn_fallback",
        help="Enable fallback warning and timing",
    )

    parser.add_argument(
        "-t", "--target", default="dfkl", help="Change backend (default: dfkl)"
    )

    parser.add_argument(
        "--pass-options",
        "-P",
        action="append",
        dest="pass_options",
        help="""Options passed to an optimization pass. This option can be
specified multiple times to pass options to multiple passes.
If PASS_OPTIONS are `pass_name` or `pass_name=on`, the pass
named `pass_name` will be enabled.
If PASS_OPTIONS are `pass_name=off`, the pass will be disabled.
If PASS_OPTIONS are `pass_name,string_options`, the pass will be
enabled and trailing string options will be passed to the pass.
""",
    )

    return parser.parse_known_args(flags.split(" "), namespace)


def parse_pass_options(values):
    """
    pass_name,key0=value0,key1=value1,...
    pass_name=on,key0=value0,key1=value1,...
    pass_name=off
    """
    configs = {}
    for value in values:
        pass_name, *key_values = value.split(",")
        pass_name += "=on" if "=" not in pass_name else ""
        pass_name, switch = pass_name.split("=", maxsplit=1)

        allowed = {"on": True, "off": False, "1": True, "0": False}

        if switch not in allowed:
            raise ValueError(f"Invalid pass option: {switch}")

        config = fireducks_ext.PassOptions()
        config.enabled = allowed[switch]
        config.options = ",".join(key_values)

        configs[pass_name] = config

    return configs


class _FireDucksOptions:
    """Global and singleton options. Not read-only."""

    def __init__(self):
        self._default_eval_options = EvalOptions(inherit_default=False)
        self.ir_prop = _FireDucksIRProperty()
        self._benchmark_mode = False
        self._configure()

    def _configure(self):
        flags = os.environ.get("FIREDUCKS_FLAGS", "")
        args, unknowns = parse_fireducks_flags(flags, self)

        self._transfer_fireducks_flags_to_compile_options(args, unknowns)

        # FIXME:
        if self._default_eval_options._compile_options.target == "dfkl":
            self.ir_prop.has_series = False
            self.ir_prop.has_metadata = True

        # FIXME: Depends on frovedis
        if self._default_eval_options._compile_options.target == "frovedis":
            import fireducks.frovedis_initialize  # noqa

        # Not to include import time in execution time
        if self._default_eval_options._compile_options.target == "cudf":
            import cudf.pandas._wrappers.pandas  # noqa
            import cudf  # noqa

            # If this option is True, some results become incorrect.
            # This was True by default, but current version of cuDF set this
            # when "install" of cudf.pandas is called. But just in case.
            cudf.set_option("mode.pandas_compatible", False)

    def _transfer_fireducks_flags_to_compile_options(self, args, unknowns):
        # parse unknown flags by extension
        options = self._default_eval_options._compile_options
        if fireducks_ext.ParseFireDucksFlags(" ".join(unknowns), options) != 0:
            raise RuntimeError("fireducks flags parse error")

        # transfer known flags
        options.target = self.target

        if args.pass_options:
            options.pass_options = parse_pass_options(args.pass_options)

    @property
    def benchmark_mode(self):
        return self._benchmark_mode

    def set_benchmark_mode(self, flag: bool):
        self._benchmark_mode = flag


_fireducks_options = _FireDucksOptions()


def get_fireducks_options():
    global _fireducks_options
    return _fireducks_options


# for tests.
def _get_default_backend():
    return (
        get_fireducks_options()._default_eval_options._compile_options.target
    )


def get_ir_prop():
    return get_fireducks_options().ir_prop


def set_fireducks_option(key, value):
    opts = get_fireducks_options()
    if key == "fallback-lineno":
        opts.fallback_lineno = value
    elif key == "fast-fallback":
        opts.fast_fallback = value
    elif key == "warn-fallback":
        opts.warn_fallback = value
    elif key == "fireducks-version":
        opts.fireducks_version = value
        from fireducks.pandas import set_version

        set_version(value)
    else:
        raise RuntimeError(f"unknown or read-only option: {key}")


_context = None


class Context:
    def __init__(self):
        self.ext_context = fireducks_ext.FireDucksContext()
        self.irbuilder = fire.IRBuilder()


def context():
    global _context
    if _context is None:
        _context = Context()
    return _context


def build_op(*args, **kwargs):
    return context().irbuilder.build_op(*args, **kwargs)


def make_available_value(x, ty):
    return context().irbuilder.make_available_value(x, ty)


def make_attr(typ, name, value):
    return context().irbuilder.new_attr(typ, name, value)


# Not well tested. Use only for testing.
@contextmanager
def prohibit_evaluation():
    options = get_fireducks_options()._default_eval_options
    options.prohibit_evaluation = True
    try:
        yield
    finally:
        options.prohibit_evaluation = False


class EvalLogger:
    """Evaluation logger to collect logs during evaluation."""

    def __init__(self):
        self._extLogger = fireducks_ext.ExecutionLogger()

    @property
    def optimized_ir(self):
        return self._extLogger.optimized_ir

    @property
    def input_pretty_ir(self):
        return self._extLogger.input_pretty_ir

    @property
    def optimized_pretty_ir(self):
        return self._extLogger.optimized_pretty_ir


class EvalLoggerManager:
    def __init__(self):
        self._loggers = []

    def new_logger(self):
        evalLogger = EvalLogger()
        self._loggers.append(evalLogger)
        return evalLogger


def _evaluate(
    values: List[fire.Value], options: EvalOptions = None, evalLogger=None
):
    for value in values:
        if value.is_available():
            logger.debug(f"evaluate: {value} (already available)")
        else:
            logger.debug(
                "evaluate: %s (defined by %s)", value, value.get_def()
            )

    if options is None:
        options = get_fireducks_options()._default_eval_options

    # evalLogger argument is priority
    if options._eval_logger_manager is not None and evalLogger is None:
        evalLogger = options._eval_logger_manager.new_logger()

    import fireducks.pandas.utils as _utils

    options._compile_options._pd_version_under2 = _utils._pd_version_under2

    if options.prohibit_evaluation:
        raise RuntimeError("evaluation prohibited")

    def wrapper(ir, input_values, output_values):
        fi = fireducks_ext.FunctionInvocation()
        fi.ir = ir
        fi.input_types = [v.mlir_type for v in input_values]
        fi.input_values = [v.get_result() for v in input_values]
        fi.output_types = [v.mlir_type for v in output_values]

        return fireducks_ext.execute(
            context().ext_context,
            options._compile_options,
            fi,
            evalLogger._extLogger if evalLogger is not None else None,
        )

    try:
        return fire.evaluate(values, wrapper, package="fireducks")
    except fireducks_ext.AssertionError as e:
        raise AssertionError(e)
    except fireducks_ext.IndexingError as e:
        raise pandas.errors.IndexingError(e)
    except fireducks_ext.InvalidIndexError as e:
        raise pandas.errors.InvalidIndexError(e)
    except fireducks_ext.MergeError as e:
        raise pandas.errors.MergeError(e)
    except fireducks_ext.NotImplementedError as e:
        raise NotImplementedError(e)
    except fireducks_ext.OSError as e:
        raise OSError(e)
    except fireducks_ext.SpecificationError as e:
        raise pandas.errors.SpecificationError(e)


def evaluate(
    values: List[fire.Value],
    options: EvalOptions = None,
    evalLogger: EvalLogger = None,
):
    with tracing.scope(tracing.Level.DEFAULT, "fireducks.core.evaluate"):
        ret = _evaluate(values, options, evalLogger)
    return ret


def evaluate_ops_depending_on_defs_of(values: List[fire.Value]):
    ops = context().irbuilder.get_ops_with_any_inputs_in(values)
    values = []
    for op in ops:
        values += op.outs
    evaluate(list(set(values)))
