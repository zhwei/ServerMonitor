#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, run, static_file
from bottle import jinja2_view as view, jinja2_template as template

import pymongo
from pymongo import Connection

from conf import STATIC_DIR

con = Connection()
db = con.ServerMonitor
temperatures = db.temperature

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_DIR)

@route("/")
def index():
    return template('index',name="hello world!")


@route("/temp")
def temperature():
    """
     db.Account.find().sort("UserName",pymongo.ASCENDING)   --升序
     db.Account.find().sort("UserName",pymongo.DESCENDING)  --降序
    """
    datas = temperatures.find().sort('datetime',pymongo.DESCENDING).limit(10)

    labels = [i for i in range(10)]

    return template('temp', labels=labels, datas=datas)


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)
