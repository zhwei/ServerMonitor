#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# 程序主目录
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


# 静态文件目录
STATIC_DIR = os.path.join(CURRENT_DIR, 'static')
# 日志文件目录
LOG_PWD = os.path.join(CURRENT_DIR, 'logs')
# 监控轮询时间
POLLING=100
