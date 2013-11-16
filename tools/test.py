#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmlrpclib
#
##server = xmlrpclib.ServerProxy("http://192.168.1.225:1234")
server = xmlrpclib.ServerProxy("http://210.44.176.171:1234")
##
print server.get_system()

#from tools.db import create_user

#create_user('zhwei','zhw','张卫')

#from tools.db import db
#
#db.control.insert({
#    'web_monitor': True,
#    'server_monitor': True,
#    'temp_monitor': True,
#})
