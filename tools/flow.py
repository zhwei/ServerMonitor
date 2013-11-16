#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import threading
from Queue import Queue

from tools.db import db
from conf import POLLING
from tools.toolbox import init_log
from tools.toolbox import create_server_status, create_web_status

lock = threading.RLock()
queue = Queue()

# 初始化日志模块
logger = init_log(log_name='flow', level_name='info',fi=True)

class MainThread(threading.Thread):

    #def main_thread():
    def run(self):

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
                logger.error('queue not empty!')
                queue.queue.clear()
            try:
                if db.control.find_one()['server_monitor']:
                    for s in db.server.find():
                        _task = ('server', s['_id'])
                        with lock:
                            queue.put(_task)
                else:
                    logger.info('server monitor stopped')
                if db.control.find_one()['web_monitor']:
                    for w in db.web.find():
                        _task = ('web', w['_id'])
                        with lock:
                            queue.put(_task)
                else:
                    logger.info('web monitor stopped!')
            except TypeError:
                date_now = datetime.datetime.now()
                db.control.insert({
                    'web_monitor': True,
                    'web_date': date_now,
                    'server_monitor': True,
                    'server_date': date_now,
                    'temp_monitor': True,
                    'temp_date': date_now,
                })


            daemon = DaemonThread()
            daemon.setDaemon(True)
            daemon.start()
            logger.info( "wait...")
            time.sleep(POLLING)

class DaemonThread(threading.Thread):

    #def daemon_thread():
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

            if obj == 'server':
                logger.info("this is server %s" % oid)
                create_server_status(oid)
            elif obj == 'web':
                logger.info("This is web %s" % oid)
                create_web_status(oid)
            else:
                logger.error('obj wrong')

def start():
    s = MainThread()
    s.setDaemon(True)
    s.start()
