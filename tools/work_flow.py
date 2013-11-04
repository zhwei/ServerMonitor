#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import xmlrpclib
from Queue import Queue
from threading import Thread
from pymongo import Connection
from bson.objectid import ObjectId
from socket import error as SocketError

from db import documents, set_server, set_server_status, set_web, set_web_status
temperatures, server, location, server_status = documents()

con = Connection()
mon = con.ServerMonitor

web = mon.web
server = mon.server
location = mon.location
temperatures = mon.temperature
server_status = mon.server_status
web_status = mon.web_status

def get_server():
    servers = server.find()
    return servers

def connect(ip):
    try:
        RemoteServer = xmlrpclib.ServerProxy("http://%s" % ip)
    except SocketError:
        return 0
    return RemoteServer

def set_server_values(id, remote):
    """
    set server values in mongodb
    """
    server.update({'_id':ObjectId(id)},
                  {'$set':
                       dict(
                            system = remote.get_system(),
                            node = remote.get_node(),
                            uname = remote.get_uname(),
                            cpu_info = remote.cpu_info()
                        )
                  })

def init_server(oid):
    '''
    after do_create_server() in sery.py
    init the server1
    '''
    a = server.find_one({'_id':ObjectId(oid)})
    remote = connect(a['ip'])
    set_server_values(oid, remote)

def create_server_status(oid):
    """
    create server status function
    in the daemon thread
    """
    try:
        oip = server.find_one({'_id':ObjectId(oid)})['ip']
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
        set_server_status(dic)
        print('update server %s' % oid)
    except SocketError:
        dic = {'status_now': 1,} #无法连接
        set_server(oid, dic)

def create_web_status(oid):
    try:
        ourl = web.find({"_id":ObjectId(oid)})

        dic = {
            'web_ID': oid,
            'keywords': {'12':1}
        }
        set_web(oid, {'status_now': 0,})
        set_web_status(dic)
    except SocketError:
        set_web(oid, {'status_now': 1,})
