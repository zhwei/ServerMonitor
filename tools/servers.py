#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zhwei'

import datetime
import threading
from bson.objectid import ObjectId
from socket import error as SocketError

from tools.db import db, update
from tools.toolbox import connect
from tools.flow import DaemonThread

lock = threading.RLock()

def set_server(oid, dic):
    """
    set server values in mongodb
    """
    server = db.server
    update(oid, server, dic)

def set_server_status(dic):
    """
    server status values in mongodb
    """
    _status = db.server_status
    _status.insert(dic)

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



def create_server_status(oid):
    """
    create server status function
    in the daemon thread
    """
    try:
        oip = db.server.find_one({'_id':ObjectId(oid)})['ip']
        remote = connect(oip)
        system = remote.get_system()
        db.server.update({'_id':ObjectId(oid)},
                      {'$set':
                           dict(
                                node = remote.get_node(),
                                uname = remote.get_uname(),
                                cpu_info = remote.cpu_info(),
                                system = system,
                            )
                      })
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
        if system == "Windows":
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

def on_create_server(oid):
    """ when create server
    """
    global queue
    _task = ('server', oid)
    with lock:
        queue.put(_task)
    #init_server(oid)
    #create_server_status(oid)
    print('succ put into queue')
    daemon = DaemonThread()
    daemon.name = 'on_create_server'+ str(datetime.datetime.now())
    daemon.setDaemon(True)
    daemon.start()