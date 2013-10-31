#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
from Queue import Queue

import pymongo
from bson import ObjectId

from tools.db import documents
from tools.work_flow import connect, set_server

temperatures, server, location = documents()

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

    if queue.empty() is False:
        # 如果队列非空则清空队列
        print('queue not empty!')
        queue.queue.clear()

    servers = server.find()
    for s in servers:
        _task = ('server', s['_id'], s['ip'])
        with lock:
            queue.put(_task)

def daemon_thread():

    """
    守护线程
    监控任务队列，每次取出一个任务执行，并将结果保存到数据库
    必须包含时间字符串
    所有任务执行完成后wait
    """
    global queue

    for i in range(queue.qsize()):
        obj, oid, oip = queue.get()
        print obj, oid, oip

        remote = connect(oip)
        dic = {
            'mem_info': remote.mem_info(),
            'cpu_usage': remote.cpu_usage(),
            'load_avg': remote.load_avg(),
            'net_stat': remote.net_stat(),
            'disk_stat': remote.disk_stat(),
            'up_time': remote.uptime_stat(),
        }
        print(dic)
        set_server(oid, dic)

queue = Queue()
main_thread()
daemon_thread()