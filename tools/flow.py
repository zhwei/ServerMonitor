#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import threading
from Queue import Queue
from socket import error as SocketError

from pymongo import Connection
from bson import ObjectId

from tools.db import documents, set_server
from tools.work_flow import connect, create_server_status, create_web_status

con = Connection()
db = con.ServerMonitor


lock = threading.RLock()
con = threading.Condition()

def main_thread():

    """
    主线程
    向队列中添加任务， 没过特定时间扫描一遍数据库，将需要查询的项目添加到队列
    此处需要查询的项目有： 服务器、网站、机房温度
    所有查询出的信息都必须包含时间字符串
    每一轮创建任务开始是检查任务队列是否为空
    不为空时输出日志并清空队列
    """
    global queue
    while True:
        if queue.empty() is False:
            # 如果队列非空则清空队列
            print('queue not empty!')
            queue.queue.clear()

        servers = db.server.find()
        for s in servers:
            _task = ('server', s['_id'])
            with lock:
                queue.put(_task)

        for w in db.web.find():
            _task = ('web', w['_id'])
            with lock:
                queue.put(_task)

        daemon = threading.Thread(name='daemon thread %s' % time.time(),
                                  target=daemon_thread())
        daemon.setDaemon(True)
        daemon.start()
        #print('%s update value' % daemon.name)
        print "wait..."
        time.sleep(100)


def daemon_thread():

    """
    守护线程
    监控任务队列，每次取出一个任务执行，并将结果保存到数据库
    必须包含时间字符串
    所有任务执行完成后wait
    """
    global queue
    for i in range(queue.qsize()):
        obj, oid = queue.get()

        if obj == 'server':
            print "this is server %s" % oid
            create_server_status(oid)
        elif obj == 'web':
            print "This is web %s" % oid
            create_web_status(oid)
        else:
            print('obj wrong')

queue = Queue()
main_thread()