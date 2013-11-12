#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmlrpclib

#server = xmlrpclib.ServerProxy("http://192.168.1.225:1234")
server = xmlrpclib.ServerProxy("http://127.0.0.1:1234")

print server.get_system()

#from tools.db import create_user
#
#create_user('zhwei','zhw','张卫')

