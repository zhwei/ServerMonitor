#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import xmlrpclib
import logging.handlers
from socket import error as SocketError

from tools.conf import LOG_PWD
#from db import set_server, set_server_status, set_web, set_web_status

LEVELS = {
    'debug':logging.DEBUG,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'error':logging.ERROR,
    'critical':logging.CRITICAL,
}

def init_log(log_name, level_name="error", fi=True):
    log_file_name = os.path.join(LOG_PWD, '%s.log'%log_name)
    # 创建一个logger
    logger=logging.getLogger(log_name)
    # 日志级别， 默认为error, 超过所设级别才会显示
    level = LEVELS.get(level_name, logging.NOTSET)
    logger.setLevel(level)
    if fi:
        # 创建一个handler, 用于写进日志文件
        # maxBytes 单个日志文件大小，超过后会新建文件，备份为 log.n
        # backupCount 超过多少个文件后会自动删除
        handler = logging.handlers.RotatingFileHandler(log_file_name,
                                                  maxBytes=1000000,
                                                  backupCount=50,)
    else:
        # 显示在控制台上
        handler = logging.StreamHandler()
    # 日志格式
    # 2011-08-31 19:18:29,816-log_name-INFO-log_line-message
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-line:%(lineno)d::%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def connect(ip):
    """ Connect XMLRPCServer
    """
    try:
        RemoteServer = xmlrpclib.ServerProxy("http://%s" % ip)
    except SocketError:
        return 0
    return RemoteServer