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
    server_status = db.server_status
    return temperatures, server, location, server_status


def find_one(obj, oid):
    return obj.find_one({"_id":ObjectId(oid)})

def set_server(id, dic):
    """
    set server values in mongodb
    """
    server = db.server
    server.update({'_id':ObjectId(id)},
                  {'$set': dic})

def set_web(id, dic):
    """
    set web values in mongodb
    """
    server = db.web
    server.update({'_id':ObjectId(id)},
                  {'$set': dic})

def set_server_status(dic):
    """
    server status values in mongodb
    """
    _status = db.server_status
    _status.insert(dic)


def set_web_status(dic):
    """
    server web values in mongodb
    """
    _status = db.web_status
    _status.insert(dic)