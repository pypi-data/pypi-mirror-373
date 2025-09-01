#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/12/15 14:01
# @Author  : 江斌
# @Software: PyCharm
import os
import json
import logging
import logging.config


def setup_logging(default_path="logconfig.json", default_level=logging.DEBUG):
    path = default_path
    if os.path.exists(path):
        with open(path, "r") as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def setup_logging_by_dict(data):
    logging.config.dictConfig(data)


def setup_default_logging():
    """
    名称	说明
    %(levelno)s	打印日志级别的数值
    %(levelname)s	打印日志级别名称
    %(pathname)s	打印当前执行程序的路径，其实就是sys.argv[0]
    %(filename)s	打印当前执行程序名
    %(funcName)s	打印日志的当前函数
    %(lineno)d	打印日志的当前行号
    %(asctime)s	打印日志的记录时间
    %(thread)d	打印线程ID
    %(threadName)s	打印线程的名称
    %(process)d	打印进程的ID
    %(message)s	打印日志的信息
    """
    setup_logging_by_dict(DEFAULT_CONFIG)


DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s - %(levelname)s - %(filename)s - line(%(lineno)d) %(funcName)s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "info_file_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "info.log",
            "when": "D",
            "interval": 1,
            "backupCount": 50,
            "encoding": "utf8"
        },
        "error_file_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "errors.log",
            "when": "D",
            "interval": 1,
            "backupCount": 50,
            "encoding": "utf8"
        },
        "debug_file_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "debug.log",
            "when": "D",
            "interval": 1,
            "backupCount": 50,
            "encoding": "utf8"
        }
    },
    "loggers": {
        "my_module": {
            "level": "ERROR",
            "handlers": ["info_file_handler"],
            "propagate": "no"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "info_file_handler", "error_file_handler"]
    }
}

get_logger = logging.getLogger

