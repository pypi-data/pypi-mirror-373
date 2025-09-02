# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import atexit
import os
from frovedis.exrpc.server import FrovedisServer

import logging

logger = logging.getLogger(__name__)


def _initialize():
    nprocs = 8
    if "FROVEDIS_NUM_PROCS" in os.environ:
        nprocs = int(os.environ["FROVEDIS_NUM_PROCS"])

    if "FROVEDIS_SERVER" not in os.environ:
        raise RuntimeError("Set FROVEDIS_SERVER")

    server = os.environ["FROVEDIS_SERVER"]

    command = f"mpirun -np {nprocs} {server}"
    logger.info("call FrovedisServer.initialize(%s})", command)
    FrovedisServer.initialize(command)

    def finalize():
        logger.info("call FrovedisServer.shut_down()")
        FrovedisServer.shut_down()

    atexit.register(finalize)


_initialize()
