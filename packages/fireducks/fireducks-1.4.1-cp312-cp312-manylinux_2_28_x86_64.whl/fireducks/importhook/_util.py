# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import logging


class LoggingHandlerWrapper:
    _handler = logging.StreamHandler()

    @classmethod
    def _set(cls, handler):
        cls._handler = handler

    @classmethod
    def get(cls):
        return cls._handler


def get_logger():
    return logging.getLogger(__package__)


def get_logging_handler():
    return LoggingHandlerWrapper.get()


_logger = get_logger()
_logger.addHandler(logging.NullHandler())
_logger.propagate = False
