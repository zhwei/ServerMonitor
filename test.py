#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmlrpclib
#
##server = xmlrpclib.ServerProxy("http://192.168.1.225:1234")
#server = xmlrpclib.ServerProxy("http://210.44.176.171:1234")
server = xmlrpclib.ServerProxy("http://127.0.0.1:1234")
##
import time
t = time.time()
#print server.get_system()
#print server.get_node()
#print server.mem_info()
#print server.cpu_info()
#print server.cpu_usage()
#print server.disk_stat() --
#print server.process_num()
#     print server.network()
#print server.set_up()
#print server.get_platform() --
print server.get_uname()
print server.get_release()
#print server.get_linux_distribution()
print server.get_architecture()
#print server.get_machine()
#print time.time() - t

print server.net_stat()
print server.load_avg()
print server.uptime_stat()
print server.partition()

#from tools.db import create_user

#create_user('zhwei','zhw','张卫')

#from tools.db import db
#
#db.control.insert({
#    'web_monitor': True,
#    'server_monitor': True,
#    'temp_monitor': True,
#})
