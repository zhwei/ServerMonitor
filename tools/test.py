#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmlrpclib
#
##server = xmlrpclib.ServerProxy("http://192.168.1.225:1234")
##
##
##
import time
t = time.time()
print server.get_system()
print server.get_node()
print server.mem_info()
print server.cpu_info()
print server.cpu_usage()
print server.disk_stat()
print server.process_num()
print server.network()
print server.set_up()
print server.get_platform()
print server.get_uname()
print server.get_release()
print server.get_linux_distribution()
print server.get_architecture()
print server.get_machine()
print time.time() - t

#from tools.db import create_user

#create_user('zhwei','zhw','张卫')

#from tools.db import db
#
#db.control.insert({
#    'web_monitor': True,
#    'server_monitor': True,
#    'temp_monitor': True,
#})
