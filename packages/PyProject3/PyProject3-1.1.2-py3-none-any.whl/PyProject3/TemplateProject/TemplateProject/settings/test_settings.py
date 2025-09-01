#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/19 11:35
# @Author  : 江斌
# @Software: PyCharm

import os
import sys
from os.path import join, abspath, dirname

cur = abspath(join(dirname(__file__), '..'))
sys.path.append(cur)
from settings import logger, YAML_CONFIG as config


def main():
    print(config)
    print(config.get_value('camera.mode'))
    print(config.get_value('app_name'))
    logger.info('info ')
    logger.debug('debug')


if __name__ == '__main__':
    main()
