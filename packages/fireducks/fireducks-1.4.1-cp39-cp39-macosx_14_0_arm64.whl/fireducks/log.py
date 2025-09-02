# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import atexit
import datetime
import cProfile
import logging
import os

from fireducks import fireducks_ext


class ExtLogStream:
    def write(self, msg: str):
        fireducks_ext.write_log(msg)


def enable_logging_log(level=logging.DEBUG, path=None):
    def enable_logger(name, handler):
        logger = logging.getLogger(name)
        # change asctime to created for more precise time
        formatter = logging.Formatter(
            # "%(asctime)s %(thread)d %(name)s:%(lineno)d] %(message)s"
            "%(asctime)s %(name)s:%(lineno)d] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    if path is None:
        handler = logging.StreamHandler()
    else:
        handler = logging.StreamHandler(ExtLogStream())

    enable_logger("firefw", handler)
    enable_logger("fireducks", handler)


class FireDucksLogSystem:
    def enable(self, rootdir: str, auto_finalize=True):
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        basedir = os.path.join(rootdir, now)
        os.makedirs(basedir, exist_ok=True)

        path = os.path.join(basedir, "cpuinfo.json")
        import platform
        if platform.system() == "Windows":
            with open(path, "w") as f:
                f.write("Windows")
        else:
            # Save cpuinfo
            import cpuinfo
            with open(path, "w") as f:
                f.write(cpuinfo.get_cpu_info_json())

        # Setup to save log to a file
        logPath = os.path.join(basedir, "log.txt")
        fireducks_ext.set_file_log_sink(logPath)  # for LOG() in c++
        enable_logging_log(logging.DEBUG, logPath)

        # Setup python profiler
        pr = cProfile.Profile()
        pr.enable()

        if auto_finalize:
            atexit.register(self.finalize)

        self.cprof = pr
        self.basedir = basedir

    def finalize(self):
        self.cprof.disable()
        path = os.path.join(self.basedir, "prof.cprof")
        self.cprof.dump_stats(path)


_fireducks_log_system = FireDucksLogSystem()


def get_log_system():
    return _fireducks_log_system


def _init():
    log_dir = os.environ.get("FIREDUCKS_LOG_DIR")
    if log_dir is not None:
        os.environ["FIRE_LOG_LEVEL"] = "99"  # force full log
        _fireducks_log_system.enable(log_dir)
    else:
        lvl = int(os.environ.get("FIRE_LOG_LEVEL", "0"))
        if lvl == 1:
            enable_logging_log(logging.INFO)  # stderr
        elif lvl == 99:
            enable_logging_log(logging.DEBUG)  # stderr


_init()
