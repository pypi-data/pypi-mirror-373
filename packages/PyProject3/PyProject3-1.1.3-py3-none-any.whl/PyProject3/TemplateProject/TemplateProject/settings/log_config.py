#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/19 11:39
# @Author  : 江斌
# @Software: PyCharm
import os
import logging
import shutil
from .constants import *


def get_logger(app_name, log_file='data.log', with_console_log=False):
    if os.path.exists(log_file):
        shutil.copy(log_file, log_file + ".old")
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    root_logger = logging.getLogger()
    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(process)d:%(thread)d %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s")  # or whatever
    handler = logging.FileHandler(log_file, "w", "utf-8")  #
    console_handler = root_logger.handlers[0]
    console_handler.setFormatter(formatter)
    handler.setFormatter(formatter)  # Pass handler as a parameter, not assign
    root_logger.addHandler(handler)
    if not with_console_log:
        root_logger.removeHandler(console_handler)
    logger = logging.getLogger(app_name)
    return logger


logger = get_logger(app_name=APP_NAME, log_file=LOG_FILE, with_console_log=WITH_CONSOLE_LOG)

# logger.level = logging.DEBUG
