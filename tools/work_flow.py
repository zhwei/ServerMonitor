#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import xmlrpclib
from socket import error as SocketError

from bson.objectid import ObjectId
from db import documents
temperatures, server = documents()

def get_server():

    servers = server.find()

    return servers

def connect(ip):
    try:
        RemoteServer = xmlrpclib.ServerProxy("http://%s" % ip)
    except SocketError:
        return 0
    return RemoteServer

def set_server_values(id, **kwargs):
    """
    set server values in mongodb
    """
    server.update({'_id':ObjectId(id)},
                  {'$set':
                       {
                        "system": kwargs['system'],
                        "host": kwargs['node'],
                        "cpu_info": kwargs['cpu_info'],
                        "location_ID": '',
                        "uname": kwargs['uname'],
                        }
                  })



#for i in get_server():
#    id = i['_id']
#    remote = connect(i['ip'])
#    k = dict(
#        system = remote.get_system(),
#        node = remote.get_node(),
#        uname = remote.get_uname(),
#        cpu_info = remote.cpu_info()
#    )
#    set_server_values(id, **k)
#    print server.find()

for i in server.find():
    for a in i:
        print a, i[a]