#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import xmlrpclib
from Queue import Queue
from threading import Thread
from socket import error as SocketError


from bson.objectid import ObjectId
from db import documents
temperatures, server, location, server_status = documents()

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
