#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, run, view, static_file

from conf import STATIC_DIR


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_DIR)

@route("/")
@view('index')
def index():
    return dict(name="hello world!")

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)
