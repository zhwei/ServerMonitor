#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bcrypt
from bson import ObjectId
from pymongo import Connection

con = Connection()
db = con.ServerMonitor


def gen_code(password):
    """ Generate Encrypted Password
    """
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_code(raw_password, crypt_password):
    """ Check Password
    raw_password: from login page
    crypt_password: from mongodb
    """
    raw_hash = bcrypt.hashpw(raw_password, crypt_password)
    return raw_hash == crypt_password

def create_user(username, password, real_name):
    """
    user = {
        'username': str,
        'password': str,
        'real_name': str,
    }
    """
    dic = {
        'username': username,
        'password': gen_code(password),
        'real_name': real_name
    }
    db.user.insert(dic)

def update(oid, coll, dic):
    """Update one document
    oid: _id, coll: db.<collection>, dic: dict();
    """
    coll.update({'_id': ObjectId(oid)},
        {'$set':dic})

def find_one(obj, oid):
    return obj.find_one({"_id":ObjectId(oid)})

def set_server(oid, dic):
    """
    set server values in mongodb
    """
    server = db.server
    update(oid, server, dic)

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