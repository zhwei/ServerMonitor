#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bottle import (route,
                    run,
                    request,
                    static_file,
                    redirect,
                    abort,)
from bottle import (jinja2_view as view,
                    jinja2_template as template,)

from bson.objectid import ObjectId
from socket import error as SocketError

from tools import db
from tools.db import find_one
from tools import plat
from conf import STATIC_DIR
from tools.proc_files import Proc
from tools.work_flow import init_server

temperatures, server, location = db.documents()

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_DIR)

@route("/")
def index():
    return template('index',name="hello world!")

@route('/<name>/list')
def list(name):
    """
    list server
    """
    if name == 'server':
        servers = server.find()
    elif name == 'location':
        locations = location.find()
    return template('list', locals())

@route('/server/add')
def create_server():
    """
    create server
    """
    locations=[]
    for l in location.find():
        locations.append((l['_id'],l['location']))
    #print locations
    return template('server_form', locals())

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
    _location_ID=request.forms.get('location')
    
    server1 = {
        "name": _name,
        "ip": _ip,
        "description": _description,
        "date": _date,
        "location_ID": _location_ID,
    }
    server.insert(server1)
    redirect('list')

@route('/server/init/<oid:re:.*>')
def init_server_info(oid):

    try:
        init_server(oid)
    except SocketError:
        return 'ip and port error'
    redirect('/server/detail/%s' % oid)


@route('/server/update/<oid>/',method='GET')
@route('/server/update/<oid>/',method='POST')
def update_server(oid):
    ser_instance = server.find_one({'_id':ObjectId(oid)})
    locations=[]
    for l in location.find():
        locations.append((str(l['_id']),l['location']))

    if request.method == "POST":
        _name = request.forms.get('name')
        _ip = request.forms.get('ip')
        _description = request.forms.get('description')
        _date = request.forms.get('date')
        _location_ID = request.forms.get('location')
        server.update({'_id':ObjectId(oid)},
                      {'$set':{
                            "name": _name,
                            "ip": _ip,
                            "description": _description,
                            "date": _date,
                            "location_ID": _location_ID,
                        }
                      },)
        return redirect('/server/list')
    return template('server_form', locals())


@route('/server/detail/<id>/')
def detail_server(id):
    ser = server.find_one({'_id':ObjectId(id)})
    condition = {'_id':ObjectId(ser['location_ID'])}
    try:
        ser['location'] = location.find_one(condition)['location']
    except TypeError:
        ser['location'] = u'机房未找到'
    return template('detail_server', locals())

@route('/location/add')
@route('/location/add', method='POST')
def create_location():
    if request.method=="POST":
        _location = request.forms.get('location')
        _description = request.forms.get('description')
        _notes = request.forms.get('notes')
        _location1 = {
            'location':_location,
            'description': _description,
            'notes': _notes,
        }
        location.insert(_location1)
        redirect('list')
    return template('loc_form',locals())


@route('/location/update/<oid>/',method='GET')
@route('/location/update/<oid>/',method='POST')
def update_location(oid):
    loc_instance = location.find_one({'_id':ObjectId(oid)})
    if request.method == "POST":
        _location = request.forms.get('location')
        _description = request.forms.get('description')
        _notes = request.forms.get('notes')
        location.update({'_id':ObjectId(oid)},
                      {'$set':{
                        'location':_location,
                        'description': _description,
                        'notes': _notes,
                        }
                      },)
        redirect('/location/list')
    return template('loc_form', locals())

@route('/<item>/delete/<oid>/')
@route('/<item>/delete/<oid>/', method="POST")
def delete(item, oid):
    if item == "server":
        obj, main = server, 'name'
    elif item == "location":
        obj, main = location, 'location'
    else:
        abort(404)
    if request.method == 'POST':
        post_id = request.forms.get('oid')
        print type(post_id), post_id
        obj.remove({"_id":ObjectId(post_id)})
        redirect('../../list')
    name = find_one(obj, oid)[main]
    return template('confirm_delete', name=name, oid=oid)

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
