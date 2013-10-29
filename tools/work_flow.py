#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import xmlrpclib
from socket import error as SocketError

from bson.objectid import ObjectId
from db import documents
temperatures, server, location = documents()

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

def init_server(ip):
    '''
    after do_create_server() in sery.py
    init the server1
    '''
    a = server.find_one({'ip':ip})
    remote = connect(ip)
    set_server_values(a['_id'], remote)



#for i in get_server():
#    id = i['_id']
#    remote = connect(i['ip'])
#
#    set_server_values(id, remote)
#    print server.find()

#for i in server.find():
#    for a in i:
#        print a, i[a]