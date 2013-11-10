#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'zhwei'

import time
from bson import ObjectId
from pymongo import Connection

# init mongodb
db=Connection().ServerMonitor

def get_session_id():
    return db.session.find_one()['_id']

class Session:

    def __init__(self, db, timeout=300):
        """
        db: mongodb set
        timeout: session expire time
        """
        self.timout=timeout
        self.coll = db.session
        self.coll.insert({'time_now': time.time()})


    def set(self, key, value):
        session_id= get_session_id()
        self.coll.update({'_id': ObjectId(session_id)},
                        {'$set':
                             {key: value}
                        }
        )

    def get(self, key):
        session_id=get_session_id()
        return self.coll.find_one({'_id':ObjectId(session_id)})[key]
