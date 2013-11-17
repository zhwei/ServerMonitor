#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from bson import ObjectId
from pymongo import Connection

from tools.conf import MONGODB_HOST, MONGODB_PORT, DB_NAME

con = Connection(host=MONGODB_HOST,port=MONGODB_PORT)
db = con[DB_NAME]




def update(oid, coll, dic):
    """Update one document
    oid: _id, coll: db.<collection>, dic: dict();
    """
    coll.update({'_id': ObjectId(oid)},
        {'$set':dic})



def update_monitor_status(item, status):
    """更新监控的运行状态
     item: server, web, temp
    """
    oid = db.control.find_one()['_id']
    dic = {item+'_monitor':status,}
    if status:
        dic[item+'_date'] = datetime.datetime.now()
    else:
        dic[item+'_date'] = False
    update(oid, db.control, dic)

def find_one(obj, oid):
    return obj.find_one({"_id":ObjectId(oid)})



