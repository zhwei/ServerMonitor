#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import bottle
from bottle import (route,
                    run,
                    app,
                    hook,
                    request,
                    static_file,
                    redirect,
                    abort,)

from bottle import jinja2_template as template

from beaker.middleware import SessionMiddleware

from pymongo import Connection
from bson.objectid import ObjectId
from socket import error as SocketError


from conf import STATIC_DIR
from tools.db import find_one, check_code
from tools.work_flow import init_server

con = Connection()
db = con.ServerMonitor

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './sessions',
    'session.auto': True
}

app = SessionMiddleware(app(), session_opts)
bottle.BaseTemplate.defaults['session'] = request.environ.get('beaker.session')



@hook('before_request')
def check_login():
    session = request.environ.get('beaker.session')
    if request.path not in ('/login',):
        try:
            if session['logged'] != True:
                redirect('/login')
        except KeyError:
            redirect('/login')


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_DIR)

@route('/aaaa')
def aaa():
    print request.environ.get('beaker.session')
    return template('others')

@route("/")
def index():
    return template('index')

def do_login(user, pw):
    try:
        crypt_pw = db.user.find_one({'username':user})['password']
    except TypeError:
        return template('login', error='用户名或密码错误！')
    if check_code(pw, crypt_pw):
        session = request.environ.get('beaker.session')
        session['logged']=True
        session['username']=user
        redirect('/')
    else:
        return template('login', error='用户名或密码错误！')

@route("/login")
@route("/login", method="POST")
def login():
    if request.method=='POST':
        _user=request.forms.get('username')
        _pw=request.forms.get('password')
        return do_login(_user, _pw)
    return template('login')

@route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session['logged']=False
    redirect('/')


def index_error(content):
    """error page base on base.html """
    return template('error', content=content)

@route('/<name>/list')
def list(name):
    """
    list server
    """
    if name == 'server':
        servers = db.server.find()
    elif name == 'location':
        locations = db.location.find()
    elif name == 'web':
        #webs = db.web.find()
        webs = [i for i in db.web.find()]
        for i in webs:
            i['server_name']=db.server.find_one({"_id":ObjectId(i['server_ID'])})['name']
    else:
        abort(404)
    return template('list', locals())

@route('/server/add')
@route('/server/add', method='POST')
def create_server():
    """
    create server
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

    if request.method == "POST":
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
        db.server.insert(server1)
        redirect('list')

    locations=[(l['_id'],l['location']) for l in db.location.find()]
    return template('server_form', locals())

from tools.work_flow import init_web

@route('/<item>/init/<oid>/')
def init_info(item,oid):
    try:
        if item == "server":
            init_server(oid)
        elif item == "web":
            init_web(oid)
        else:
            abort(404)
    except SocketError:
        return index_error('无法连接，请检查网络或者配置是否正确。')
    redirect('/%s/detail/%s/' %(item, oid))

@route('/server/update/<oid>/',method='GET')
@route('/server/update/<oid>/',method='POST')
def update_server(oid):
    if request.method == "POST":
        _name = request.forms.get('name')
        _ip = request.forms.get('ip')
        _description = request.forms.get('description')
        _date = request.forms.get('date')
        _location_ID = request.forms.get('location')
        db.server.update({'_id':ObjectId(oid)},
                      {'$set':{
                            "name": _name,
                            "ip": _ip,
                            "description": _description,
                            "date": _date,
                            "location_ID": _location_ID,
                        }
                      },)
        return redirect('/server/list')

    ser_instance = db.server.find_one({'_id':ObjectId(oid)})
    locations=[(str(l['_id']),l['location']) for l in db.location.find()]

    return template('server_form', locals())

@route('/server/detail/<oid>/')
def detail_server(oid):
    ser = db.server.find_one({'_id':ObjectId(oid)})
    try:
        condition = {'_id':ObjectId(ser['location_ID'])}
        ser['location'] = db.location.find_one(condition)['location']
    except:
        ser['location'] = u'<span style="color:red;">机房未找到'

    status = db.server_status.find({'server_ID':ObjectId(oid)}).sort('datetime', -1).limit(10)
    status_list = [i for i in status]
    try:
        last_time = status_list[0]
    except IndexError:
        error="<a href='/init/%s/' class='btn btn-primary'>请初始化</a>"

    if ser['system'] == "Linux":
        try:
            cpu_usage_list = [i['cpu_usage']*100 for i in status_list]
            mem_info_list = [i['mem_info']['mem_used']/i['mem_info']['mem_total']*100 for i in status_list]
            up_time = status_list[0]['up_time']
            load_avg_1 = [float(i['load_avg']['lavg_1']) for i in status_list]
            load_avg_5 = [float(i['load_avg']['lavg_5']) for i in status_list]
            load_avg_15 = [float(i['load_avg']['lavg_15']) for i in status_list]
            tpl_name='detail_server'
        except IndexError:
            return index_error('暂无历史记录<a href="/server/delete/%s/">删除</a>'% oid)
    elif ser['system'] == "Windows":
        try:
            cpu_usage_list = [i['cpu_usage']*100 for i in status_list]
            mem_info_list = [i['mem_info']['mem_used']/i['mem_info']['mem_total']*100 for i in status_list]
            tpl_name="detail_server_win.html"
        except IndexError:
            return index_error('暂无历史记录<a href="/server/delete/%s/">删除</a>'% oid)

    return template(tpl_name, locals())

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
        db.location.insert(_location1)
        redirect('list')
    return template('loc_form',locals())

@route('/location/update/<oid>/',method='GET')
@route('/location/update/<oid>/',method='POST')
def update_location(oid):
    """update location """
    if request.method == "POST":
        _location = request.forms.get('location')
        _description = request.forms.get('description')
        _notes = request.forms.get('notes')
        db.location.update({'_id':ObjectId(oid)},
                      {'$set':{
                        'location':_location,
                        'description': _description,
                        'notes': _notes,
                        }
                      },)
        redirect('/location/list')
    loc_instance = db.location.find_one({'_id':ObjectId(oid)})
    return template('loc_form', locals())

@route('/web/add')
@route('/web/add', method='POST')
def create_web():
    """
    create web page
    """
    if request.method == "POST":
        _name = request.forms.get('name')
        _url = request.forms.get('url')
        _description = request.forms.get('description')
        _keywords = request.forms.get('keywords')
        _keys = [i.strip() for i in _keywords.split(',') if i.strip() is not '']
        _server_ID = request.forms.get('server')
        web1 = {
            'name':_name,
            'url':_url,
            'description': _description,
            'keywords': _keys,
            'server_ID': _server_ID,
        }
        db.web.insert(web1)
        redirect('/web/list')

    servers=[(s['_id'],s['name']) for s in db.server.find()]
    return template('web_form', locals())

@route('/web/update/<oid>/')
@route('/web/update/<oid>/', method='POST')
def update_web(oid):
    if request.method == "POST":
        _name = request.forms.get('name')
        _url = request.forms.get('url')
        _description = request.forms.get('description')
        _keywords = request.forms.get('keywords')
        _keys = [i.strip() for i in _keywords.split(',') if i.strip() is not '']
        _server_ID = request.forms.get('server')
        db.web.update({'_id':ObjectId(oid)},
                   {'$set':{
                    'name':_name,
                    'url':_url,
                    'description': _description,
                    'keywords': _keys,
                    'server_ID': _server_ID,
                }})
        redirect('/web/list')
    web_instance=db.web.find_one({'_id':ObjectId(oid)})
    web_instance['keywords']=','.join(web_instance['keywords'])
    servers=[(str(s['_id']),s['name']) for s in db.server.find()]
    return template('web_form', locals())

@route('/web/detail/<oid>/')
def detail_web(oid):
    wb = db.web.find_one({'_id':ObjectId(oid)})
    status = db.web_status.find({'web_ID':ObjectId(oid)}).sort('datetime', -1).limit(10)
    status_list = [i for i in status]

    total_time_list = [i['total_time'] for i in status_list]
    connect_time_list = [i['connect_time'] for i in status_list]
    name_look_up_list = [i['name_look_up'] for i in status_list]

    last_status = status_list[0]
    try:
        _condition = {'_id':ObjectId(wb['server_ID'])}
        wb['server'] = db.server.find_one(_condition)['name']
    except:
        wb['server'] = u'<div class="alert alert-block">服务器未找到</div>'
    return template('detail_web', locals())

@route('/<item>/delete/<oid>/')
@route('/<item>/delete/<oid>/', method="POST")
def delete(item, oid):
    """
    general delete function
    need the collection name and the id
    """
    if item == "server":
        obj, main = db.server, 'name'
        if db.web.find({'server_ID':oid}).count() != 0:
            return index_error('该服务器包含可用网站，请先迁移网站！')
    elif item == "location":
        obj, main = db.location, 'location'
        if db.server.find({"location_ID":oid}).count() != 0:
            return index_error('该机房包含可用服务器，请先迁移服务器！')
    elif item == "web":
        obj, main = db.web, 'name'
    else:
        abort(404)
    if request.method == 'POST':
        post_id = request.forms.get('oid')
        obj.remove({"_id":ObjectId(post_id)})
        redirect('../../list')
    name = find_one(obj, oid)[main]
    return template('confirm_delete', name=name, oid=oid)

@route("/temp")
def temperature():
    """
     db.Account.find().sort("UserName",pymongo.ASCENDING)   --升序
     db.Account.find().sort("UserName",pymongo.DESCENDING)  --降序
    """
    datas = db.temperatures.find().sort('datetime', -1).limit(10)
    labels = [i for i in range(10)]
    datas = [t for t in datas]
    return template('temp', labels=labels, datas=datas)


def dev_server():
    run(app=app,host='0.0.0.0', port=8080, debug=True)

if '__main__' == __name__:
    from django.utils import autoreload
    autoreload.main(dev_server)