# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
from datetime import datetime

__logger = None
__logger_file = None


def _get_logger():
    global __logger
    if __logger is None:
        logger_name = "lynx_e2e_console_log"
        __logger = logging.getLogger(logger_name)
        __logger.level = logging.DEBUG
        global __logger_file
        __logger_file = os.path.abspath(logger_name + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log")
        handler = logging.FileHandler(__logger_file)
        fmt = logging.Formatter("%(message)s")
        handler.setFormatter(fmt)
        __logger.addHandler(handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt)
        stream_handler.setLevel(logging.WARNING)
        __logger.addHandler(stream_handler)
        __logger.propagate = False
    return __logger


def get_log_file():
    if __logger_file is None:
        _get_logger()
    return __logger_file


def write(msg):
    _get_logger().info(msg)


def reset():
    global __logger, __logger_file
    __logger = None
    __logger_file = None
