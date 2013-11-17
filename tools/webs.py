#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zhwei'

import datetime
import threading
from bson.objectid import ObjectId
from socket import error as SocketError

from tools.db import db
from tools.web_monitor import WebMonitor
#from tools.flow import DaemonThread

lock = threading.RLock()

def set_web(id, dic):
    """
    set web values in mongodb
    """
    server = db.web
    server.update({'_id':ObjectId(id)},
                  {'$set': dic})

def set_web_status(dic):
    """
    server web values in mongodb
    """
    _status = db.web_status
    _status.insert(dic)

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


def create_web_status(oid):
    try:
        target = db.web.find_one({"_id":ObjectId(oid)})
        try:
            monitor = WebMonitor(target['url'])
        except TypeError:
            set_web(oid, {'status_now': 2,})
        db.web.update({'_id':ObjectId(oid)},
                      {'$set':
                           dict(
                                title = monitor.get_title(),
                                encoding = monitor.get_encoding(),
                                content_type=monitor.content_type(),
                            )
                      })
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

import threading
from toolbox import init_log
# 初始化日志模块
logger = init_log(log_name='flow', level_name='info',fi=True)

class DaemonThread(threading.Thread):

    def run(self):
        """
        守护线程
        监控任务队列，每次取出一个任务执行，并将结果保存到数据库
        必须包含时间字符串
        所有任务执行完成后wait
        """
        global queue
        for i in range(queue.qsize()):
            obj, oid = queue.get()

            if obj == 'web':
                logger.info("This is web %s" % oid)
                create_web_status(oid)
            else:
                logger.error('obj wrong')

def on_create_web(oid):

    global queue
    #init_web(oid)
    #create_web_status(oid)
    _task = ('web', oid)
    with lock:
        queue.put(_task)
    daemon = DaemonThread()
    daemon.setDaemon(True)
    daemon.start()