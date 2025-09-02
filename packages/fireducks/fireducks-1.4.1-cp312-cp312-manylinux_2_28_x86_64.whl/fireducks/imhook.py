# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import os.path
import runpy
import sys

from . import importhook
from . import pandas as apandas

# ignore this script itself
importhook.ImportHook.ignore_names.append(os.path.abspath(__file__))


def load_ipython_extension(ipython):
    # cf. https://ipython.readthedocs.io/en/stable/config/extensions/
    hook = importhook._get_current_hook()
    if hook is not None:
        raise RuntimeError(f"another import-hook is already active: {hook!r}")
    importhook.activate_hook(apandas.__name__)

    # fmt: off
    from . import ipyext  # noqa: E402
    ipyext.load_ipython_extension(ipython)
    # fmt: on


def unload_ipython_extension(ipython):
    # cf. https://ipython.readthedocs.io/en/stable/config/extensions/
    importhook.deactivate_hook()


def run_default_action():
    sys.argv.insert(1, apandas.__name__)
    runpy.run_module(importhook.__name__, run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    run_default_action()
