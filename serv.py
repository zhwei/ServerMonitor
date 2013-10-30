#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import (route,
                    run,
                    static_file,)
from bottle import (jinja2_view as view,
                    jinja2_template as template,)

import pymongo
from pymongo import Connection

from conf import STATIC_DIR
from tools.proc_files import Proc

con = Connection()
db = con.ServerMonitor
temperatures = db.temperature

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_DIR)

@route("/")
def index():
    return template('index',name="hello world!")

@route("/funcs")
def funcs():
    p = Proc()
    mem_info = p.mem_info()
    mem_usage = mem_info['mem_used']/mem_info['mem_total']
    cpu_usage = p.cpu_usage()
    print cpu_usage
    return template('funcs', locals())

@route('/list')
def lists():
    p = Proc()
    load_avg = p.load_avg()
    process_num = p.process_num()
    up_time = p.uptime_stat()
    disk_stat = p.disk_stat()
    cpu_info = p.cpu_info()
    net_stat = p.net_stat()

    return template('list', locals())

@route("/temp")
def temperature():
    """
     db.Account.find().sort("UserName",pymongo.ASCENDING)   --升序
     db.Account.find().sort("UserName",pymongo.DESCENDING)  --降序
    """
    datas = temperatures.find().sort('datetime',pymongo.DESCENDING).limit(10)

    labels = [i for i in range(10)]

    return template('temp', labels=labels, datas=datas)


#if __name__ == '__main__':
#    run(host='localhost', port=8080, debug=True)

def dev_server():
    run(host='0.0.0.0', port=8080, debug=True)

if '__main__' == __name__:
    from django.utils import autoreload
    autoreload.main(dev_server)
