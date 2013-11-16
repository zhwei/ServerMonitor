#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# 程序主目录
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

# MongoDB 配置
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017

# Session过期时间
COOKIE_EXPIRES = 3000
# 静态文件目录
STATIC_DIR = os.path.join(CURRENT_DIR, 'static')
# 日志文件目录
LOG_PWD = os.path.join(CURRENT_DIR, 'logs')
# 监控轮询时间
POLLING=100
