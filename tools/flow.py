#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
from Queue import Queue

import pymongo
from bson import ObjectId

from tools.db import documents

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

    servers = server.find()
    for s in servers:
        _task = ('server', s)
        with lock:
            queue.put(_task)

    print queue.qsize()
    queue.queue.clear()
    print queue.qsize()

def daemon_thread():

    """
    守护线程
    监控任务队列，每次取出一个任务执行，并将结果保存到数据库
    必须包含时间字符串
    所有任务执行完成后wait
    """
    pass

queue = Queue()
main_thread()