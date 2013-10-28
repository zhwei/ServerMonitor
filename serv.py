#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, run, static_file
from bottle import jinja2_view as view
from pymongo import Connection

from conf import STATIC_DIR

con = Connection()
db = con.ServerMonitor
temperatures = db.temperature

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_DIR)

@route("/")
@view('index')
def index():
    return dict(name="hello world!")

@route("/temp")
@view("temp")
def temperature():

    datas = temperatures.find()

    labels = []
    for i in datas:
        labels.append(i['datetime'])

    return dict(labels=labels, datas=datas)


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)
