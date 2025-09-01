#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/11/17 19:42
# @Author  : 江斌
# @Software: PyCharm

import os

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def create_dir(abs_filename):
    """
    创建目录，如果目录不存在。
    :param abs_filename: 绝对路径。
    :return:
    """
    created = False
    if not os.path.exists(abs_filename):
        print(f'created: {abs_filename}')
        os.makedirs(abs_filename)
        created = True
    return created


def create_file(abs_filename, content, override=False):
    path, filename = os.path.split(abs_filename)
    create_dir(path)
    if filename:  # 是文件
        if (not os.path.exists(abs_filename)) or override:  # 文件不存在，或者强制覆盖
            print(f'created: {abs_filename}')
            with open(abs_filename, 'w+', encoding='utf-8') as fid:
                fid.write(content)
