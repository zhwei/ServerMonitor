#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import xmlrpclib
#
#server = xmlrpclib.ServerProxy("http://0.0.0.0:1234")
#
#print server.get_uname()

from tools.db import create_user

create_user('zhwei','zhw','张卫')

