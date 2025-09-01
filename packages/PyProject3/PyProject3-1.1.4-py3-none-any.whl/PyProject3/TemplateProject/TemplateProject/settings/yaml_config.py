#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/19 11:31
# @Author  : 江斌
# @Software: PyCharm
import os
import json
import yaml


class YamlConfig(object):
    def __init__(self, filename):
        self.filename = filename
        self.config = None
        self._load()

    def _load(self):
        with open(self.filename, 'r') as yf:
            self.config = yaml.safe_load(yf)

    def save(self):
        with open(self.filename, 'w') as cfp:
            yaml.dump(self.config, cfp)
        return

    def get_value(self, key, expanding_user=False, make_dir=False):
        keys = key.split('.')
        value = self.config
        for key in keys:
            value = value[key]
        if expanding_user:
            value = os.path.expanduser(value)
        if make_dir:
            _, ext = os.path.splitext(value)
            if '.' in ext:  # value is a file.
                p = os.path.dirname(value)
            else:  # value is directory.
                p = value
            if not os.path.exists(p):
                os.makedirs(p)
        return value

    def update_config_yaml(self, key, value):
        if "." in key:
            tmp_key = None
            key_path = key.split(".")
            for i in key_path[:-1]:
                tmp_key = self.config[i]
            tmp_key[key_path[-1]] = value
        else:
            self.config[key] = value

    def __str__(self):
        return json.dumps(self.config, indent=4)

    def __repr__(self):
        return self.__str__()
