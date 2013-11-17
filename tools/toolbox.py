#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import datetime
import xmlrpclib
import logging.handlers
from bson.objectid import ObjectId
from socket import error as SocketError

from db import db
from conf import LOG_PWD
from db import set_server, set_server_status, set_web, set_web_status

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


def get_server():
    servers = db.server.find()
    return servers

def connect(ip):
    try:
        RemoteServer = xmlrpclib.ServerProxy("http://%s" % ip)
    except SocketError:
        return 0
    return RemoteServer


def init_server(oid):
    '''
    after do_create_server() in sery.py
    init the server1
    '''
    a = db.server.find_one({'_id':ObjectId(oid)})
    remote = connect(a['ip'])
    db.server.update({'_id':ObjectId(oid)},
                  {'$set':
                       dict(
                            node = remote.get_node(),
                            uname = remote.get_uname(),
                            cpu_info = remote.cpu_info(),
                            system = remote.get_system(),
                        )
                  })

def init_web(oid):
    """
    set web values in mongodb
    """
    target = db.web.find_one({"_id":ObjectId(oid)})
    monitor = WebMonitor(target['url'])
    db.web.update({'_id':ObjectId(oid)},
                  {'$set':
                       dict(
                            title = monitor.get_title(),
                            encoding = monitor.get_encoding(),
                            content_type=monitor.content_type(),
                        )
                  })

def create_server_status(oid):
    """
    create server status function
    in the daemon thread
    """
    try:
        o = db.server.find_one({'_id':ObjectId(oid)})
        oip = o['ip']
        o_system=o['system']
        remote = connect(oip)
        dic = {
            'server_ID': oid,
            'load_avg': remote.load_avg(),
            'mem_info': remote.mem_info(),
            'net_stat': remote.net_stat(),
            'cpu_usage': remote.cpu_usage(),
            'disk_stat': remote.disk_stat(),
            'up_time': remote.uptime_stat(),
            'partition': remote.partition(),
            'datetime': datetime.datetime.now(),
            }
        if o_system == "Windows":
            dic = dict(dic, **{
                'machine': remote.get_machine(),
                'set_up':remote.set_up(),
                'network': remote.network(),
                'process_num': remote.process_num(),
            })
        #try:
        #    dic = dict(dic, **{
        #        'disk_stat': remote.disk(),
        #    })
        #except xmlrpclib.Fault:
        #    print('passsssssssss')

        set_server(oid, {'status_now': 0,}) # update "server
        set_server_status(dic)
        print('update server %s' % oid)
    except SocketError:
        dic = {'status_now': 1,} #无法连接
        set_server(oid, dic)

from web_monitor import WebMonitor

def create_web_status(oid):
    try:
        target = db.web.find_one({"_id":ObjectId(oid)})
        try:
            monitor = WebMonitor(target['url'])
        except TypeError:
            set_web(oid, {'status_now': 2,})
        dic = {
            'web_ID': oid,
            'title': monitor.get_title(),
            'encoding': monitor.get_encoding(),
            'total_time': monitor.total_time(),
            'content_type': monitor.content_type(),
            'name_look_up': monitor.name_look_up(),
            'connect_time': monitor.connect_time(),
            'status_code': monitor.get_status_code(),
            'per_transfer_time': monitor.per_transfer_time(),
            'content_encoding': monitor.get_content_encoding(),
            'start_transfer_time': monitor.start_transfer_time(),
            'keywords': monitor.contain_keyword(target['keywords']),
            'datetime': datetime.datetime.now(),
        }
        set_web(oid, {'status_now': 0,})
        set_web_status(dic)
    except SocketError:
        set_web(oid, {'status_now': 1,})


def on_create_server(oid):
    """ when create server
    """
    init_server(oid)
    create_server_status(oid)

def on_create_web(oid):
    init_web(oid)
    create_web_status(oid)