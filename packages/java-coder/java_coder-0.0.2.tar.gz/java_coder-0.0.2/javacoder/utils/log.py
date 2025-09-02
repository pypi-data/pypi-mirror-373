#!/user/bin/env python
# -*- coding: utf-8 -*-
# Time: 2025/8/18 23:40
# Author: chonmb
# Software: PyCharm

def warning(*strings):
    print("\033[33m[warning]\033[0m", *strings)


def info(*strings):
    print("\033[32m[info]\033[0m", *strings)


def error(*strings):
    print("\033[31m[error]\033[0m", *strings)


def debug(*strings):
    print("\033[34m[debug]\033[0m", *strings)

