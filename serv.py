#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import bottle
from bottle import route, run, app, request, redirect, abort

import datetime
from pymongo import Connection
from bson.objectid import ObjectId
from socket import error as SocketError
from bottle import jinja2_template as template
from beaker.middleware import SessionMiddleware

from tools.db import find_one, check_code
from conf import STATIC_DIR, COOKIE_EXPIRES
from tools.toolbox import init_server, init_log
from tools.db import create_user as db_create_user, db,\
    update_user as db_update_user, update_monitor_status

logger = init_log(log_name='bottle_server', level_name='info',fi=True)

# 启动监控轮询线程
from tools.flow import start as flow_start
flow_start()

# Session Config
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': COOKIE_EXPIRES,
    'session.data_dir': './sessions',
    'session.auto': True
}
app = SessionMiddleware(app(), session_opts)
bottle.BaseTemplate.defaults['session'] = request.environ.get('beaker.session')

@bottle.hook('before_request')
def check_login():
    session = request.environ.get('beaker.session')
    if request.path not in ('/login',):
        try:
            if session['logged'] != True:
                redirect('/login?%s'%request.path)
        except KeyError:
            redirect('/login?%s'%request.path)


@route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root=STATIC_DIR)

@route("/")
def index():
    servers = db.server.find()
    webs = db.web.find()
    return template('index', locals())

def do_login(user, pw):
    try:
        crypt_pw = db.user.find_one({'username':user})['password']
    except TypeError:
        logger.info('用户名或密码错误！')
        return template('login', error='用户名或密码错误！')
    if check_code(pw, crypt_pw):
        session = request.environ.get('beaker.session')
        session['logged']=True
        session['username']=user
        return True
    else:
        logger.info('用户名或密码错误！')
        return template('login', error='用户名或密码错误！')

@route("/login")
@route("/login", method="POST")
def login():
    if request.method=='POST':
        _user=request.forms.get('username')
        _pw=request.forms.get('password')
        refer = request.urlparts[3]
        if do_login(_user, _pw):
            redirect(refer)
    return template('login')

@route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session['logged']=False
    redirect('/')


def index_error(content, referer=None):
    """error page base on base.html """
    return template('error', content=content, referer=referer)

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
        #webs = db.web.find()
        if len(webs) != 0:
            for i in webs:
                i['server_name']=db.server.find_one({"_id":ObjectId(i['server_ID'])})['name']
    elif name == 'user':
        users = db.user.find()
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

from tools.toolbox import init_web

@route('/<item>/init/<oid>/')
def init_info(item,oid):
    from requests import ConnectionError
    try:
        if item == "server":
            init_server(oid)
        elif item == "web":
            init_web(oid)
        else:
            abort(404)
    except SocketError:
        return index_error('无法连接，请检查网络或者配置是否正确。')
    except ConnectionError:
        return index_error("网站无法链接，请检查配置是否正确！")
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

    webs = db.web.find({'server_ID': oid})

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

@route('/location/detail/<oid>/')
def detail_location(oid):
    loc = db.location.find_one({'_id':ObjectId(oid)})
    servers = db.server.find({'location_ID': oid})
    return template('detail_loc', locals())

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

    try:
        status = db.web_status.find({'web_ID':ObjectId(oid)}).sort('datetime', -1).limit(10)
        status_list = [i for i in status]

        total_time_list = [i['total_time'] for i in status_list]
        connect_time_list = [i['connect_time'] for i in status_list]
        name_look_up_list = [i['name_look_up'] for i in status_list]

        last_status = status_list[0]
    except IndexError:
        pass
    try:
        _condition = {'_id':ObjectId(wb['server_ID'])}
        wb['server'] = db.server.find_one(_condition)['name']
    except:
        wb['server'] = u'<div class="alert alert-block">服务器未找到</div>'
    return template('detail_web', locals())


@route('/user/add')
@route('/user/add', method='POST')
def create_user():
    if request.method == "POST":
        _user = request.forms.get("username")
        _pw = request.forms.get("password")
        _real = request.forms.get("real_name")
        db_create_user(_user, _pw, _real)
        redirect('list')
    return template('user_form', locals())

@route('/user/update/<oid>/')
@route('/user/update/<oid>/', method="POST")
def update_user(oid):
    if request.method == "POST":
        _user = request.forms.get("username")
        _pw = request.forms.get("password")
        _real = request.forms.get("real_name")
        if _pw == '':
            user_instance = db.user.find_one({"_id": ObjectId(oid)})
            error='密码不能为空!'
            return template('user_form', locals())
        db_update_user(oid, _user, _pw, _real)
        redirect('../../list')

    user_instance = db.user.find_one({"_id": ObjectId(oid)})
    return template('user_form', locals())

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
    elif item == "user":
        obj, main = db.user, 'username'
    else:
        abort(404)
    if request.method == 'POST':
        post_id = request.forms.get('oid')
        obj.remove({"_id":ObjectId(post_id)})
        redirect('../../list')
    name = find_one(obj, oid)[main]
    return template('confirm_delete', name=name, oid=oid)

#@route('/history')
#def history():
#    items = {'cpu':'CPU', 'mem':'内存',
#             'load_1':'每一分钟负载',
#             'load_5':'每五分钟负载',
#             'load_15':'每十五分钟负载',
#             'total':'网站访问总时间',
#             'connect':'链接时间',
#             'lookup':'域名解析时间',}
#    return template('history')

@route('/<item>/<oid>/<num>/<t>/')
def history_items(item, oid, num,t=1):
    """
    The canvas's history
    item: server -- cpu, mem, load<1, 5, 15>
          web -- total connect lookup
    """
    if item in ('cpu', 'mem', 'load_1', 'load_5', 'load_15'):
        father, son=db.server, db.server_status
        id_name='server_ID'
    elif item in ('total', 'connect', 'lookup'):
        father, son=db.web, db.web_status
        id_name='web_ID'
    elif item == 'temp':
        father, son=db.server, db.temperature
        id_name='server_ID'
    else:
        abort(404)

    t = int(t)
    num = int(num)

    all_list=son.find({id_name:ObjectId(oid)}).sort('datetime', -1)
    page_count = all_list.count()//num + 1
    status_list=all_list.skip((t-1)*num).limit(num)
    status_list = [i for i in status_list]
    end, start = status_list[0]['datetime'], status_list[-1]['datetime']
    dates = [i['datetime'].strftime('%m-%d-%H:%M') for i in status_list]

    if item == 'cpu':
        data_list = [i['cpu_usage'] for i in status_list]
        name='cpu'
    elif item == 'mem':
        data_list = [i['mem_info']['mem_used']/i['mem_info']['mem_total']*100 for i in status_list]
        name='内存'
    elif item == 'load_1':
        data_list = [float(i['load_avg']['lavg_1']) for i in status_list]
        name ='最近一分钟负载'
    elif item == 'load_5':
        data_list = [float(i['load_avg']['lavg_5']) for i in status_list]
        name = '最近五分钟负载'
    elif item == 'load_15':
        data_list = [float(i['load_avg']['lavg_15']) for i in status_list]
        name='最近十五分钟负载'
    elif item == 'total':
        data_list=[i['total_time'] for i in status_list]
        name='总时间'
    elif item == 'connect':
        data_list = [i['connect_time'] for i in status_list]
        name='连接时间'
    elif item == 'lookup':
        data_list=[i['name_look_up'] for i in status_list]
        name='域名解析时间'
    elif item == 'temp':
        data_list=[t['temp'] for t in status_list]
        name='温度'
    else:
        abort(404)
    return template("history", locals())

@route("/temp/<oid>/")
def temperature(oid):
    """
     db.Account.find().sort("UserName",pymongo.ASCENDING)   --升序
     db.Account.find().sort("UserName",pymongo.DESCENDING)  --降序
    """
    datas = db.temperatures.find({'server_ID':ObjectId(oid)}).sort('datetime', -1).limit(10)
    temp_list = [t['temp'] for t in datas]
    return template('temp', locals())

@route('/control')
@route('/control', method="post")
def control():
    """ 监控管理
    """
    dic = {'server':'server_monitor',
           'web':'web_monitor',
           'temp':'temp_monitor'}
    if request.method == "POST":
        item=request.forms.get('item')
        if item in ('server', 'web', 'temp'):
            update_monitor_status(item, False)
        else:
            abort(404)
        redirect('/control')
    _what = request.urlparts[3]
    if _what in ('server', 'web', 'temp'):
        update_monitor_status(_what, True)
        redirect('/control')
    control = db.control.find_one()
    now = datetime.datetime.now()
    return template('control', locals())

#def dev_server():
#    run(app=app,host='0.0.0.0', port=8080, debug=True)

#if '__main__' == __name__:
    #from django.utils import autoreload
    #autoreload.main(dev_server)
    #run(app=app, host='0.0.0.0', port=8080, server='gunicorn')
