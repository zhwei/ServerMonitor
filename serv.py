#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import (route,
                    run,
                    request,
                    static_file,)
from bottle import (jinja2_view as view,
                    jinja2_template as template,)

from tools import db
from tools import plat
from conf import STATIC_DIR
from tools.proc_files import Proc
from tools.work_flow import init_server

from bson.objectid import ObjectId
temperatures, server, location = db.documents()

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_DIR)

@route("/")
def index():
    return template('index',name="hello world!")

@route('/server/list')
def list_server():
    """
    list server
    """
    servers = server.find()
    return template('list', servers = servers)

@route('/server/add')
def create_server():
    """
    create server
    """
    return template('server_form')

@route('/server/add', method='POST')
def do_create_server():
    """
    Server = {
        "name": _name,
        "ip": _ip,
        "description": _description,
        "date": _date,
        # ---auto---------
        "system": get_system(),
        "host": get_node(),
        "cpu_info": cpu_info(),
        "location_ID":location,
        "uname": get_uname(),
    }
    """
    _name = request.forms.get('name')
    _ip = request.forms.get('ip')
    _description = request.forms.get('description')
    _date = request.forms.get('date')

    server1 = {
        "name": _name,
        "ip": _ip,
        "description": _description,
        "date": _date,
    }
    server.insert(server1)
    init_server(ip)
    return "create server ok! <a href='/'>首页</a>"

@route('/server/detail/<id:re:.*>')
def detail_server(id):
    ser = server.find_one({'_id':ObjectId(id)})
    print ser['cpu_info']
    return template('detail_server', locals())

@route('/location/list')
def list_location():

    locations = location.find()

    return template('list', locals())



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

    uname = plat.get_uname()
    system = plat.get_system()

    node = plat.get_node()
    distribution = plat.get_linux_distribution()

    import platform as pl
    pl = pl

    return template('others', locals())

@route("/temp")
def temperature():
    """
     db.Account.find().sort("UserName",pymongo.ASCENDING)   --升序
     db.Account.find().sort("UserName",pymongo.DESCENDING)  --降序
    """
    datas = temperatures.find().sort('datetime', -1).limit(10)

    labels = [i for i in range(10)]

    return template('temp', labels=labels, datas=datas)


#if __name__ == '__main__':
#    run(host='localhost', port=8080, debug=True)

def dev_server():
    run(host='0.0.0.0', port=8080, debug=True)

if '__main__' == __name__:
    from django.utils import autoreload
    autoreload.main(dev_server)
