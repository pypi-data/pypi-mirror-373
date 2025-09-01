#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/9/10 12:11
# @Author  : 江斌
# @Software: PyCharm

import os
import time
import win32api
import win32con
import win32clipboard as w
import subprocess


def getText():
    w.OpenClipboard()
    d = w.GetClipboardData(win32con.CF_TEXT)
    w.CloseClipboard()
    return d


def setText(aString):
    w.OpenClipboard()

    w.EmptyClipboard()

    w.SetClipboardData(win32con.CF_TEXT, aString)

    w.CloseClipboard()


def format_code():
    txt = getText()
    txt = txt.decode('utf-8')
    lines = txt.split('\n')
    idx = lines[0].find("'")
    if idx==-1:
        idx = lines[0].find("i")
    print(idx)
    new_lines = [line[idx:] for line in lines]
    new_txt = '\n'.join(new_lines)
    print(new_txt)
    setText(new_txt.encode('utf-8'))


format_code()
