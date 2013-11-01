#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import threading
from Queue import Queue
from socket import error as SocketError

import pymongo
from bson import ObjectId

from tools.db import documents, create_server_status, set_server
from tools.work_flow import connect

temperatures, server, location, server_status = documents()

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

        servers = server.find()
        for s in servers:
            _task = ('server', s['_id'], s['ip'])
            with lock:
                queue.put(_task)

        daemon = threading.Thread(name='daemon thread %s' % time.time(),
                                  target=daemon_thread())
        daemon.setDaemon(True)
        daemon.start()
        print('%s update value' % daemon.name)
        time.sleep(50)


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
        try:
            remote = connect(oip)
            dic = {
                'server_ID': oid,
                'datetime': datetime.datetime.now(),
                'mem_info': remote.mem_info(),
                'cpu_usage': remote.cpu_usage(),
                'net_stat': remote.net_stat(),
                'disk_stat': remote.disk_stat(),
                'up_time': remote.uptime_stat(),
                'load_avg': remote.load_avg(),
                }
            set_server(oid, {'status_now': 0,}) # update "server
            create_server_status(dic)
            print('update server %s' % oid)
        except SocketError:
            dic = {'status_now': 1,} #无法连接
            set_server(oid, dic)

queue = Queue()
main_thread()