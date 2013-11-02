#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import Connection
from bson import ObjectId

con = Connection()
db = con.ServerMonitor

def documents():
    """
    return documents form mongodb one time
    """
    temperatures = db.temperature
    server = db.server
    location = db.location

    return temperatures, server, location


def find_one(obj, oid):
    return obj.find_one({"_id":ObjectId(oid)})

def set_server(id, dic):
    """
    set server values in mongodb
    """
    server = db.server
    server.update({'_id':ObjectId(id)},
                  {'$set': dic})

def create_server_status(dic):
    """
    server status values in mongodb
    """
    _status = db.server_status
    _status.inset(dic)