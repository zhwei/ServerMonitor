#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SimpleXMLRPCServer

from proc_files import Proc
from plat import get_uname, get_system, get_node

obj = Proc()
obj.get_uname = get_uname
obj.get_system = get_system
obj.get_node = get_node

server = SimpleXMLRPCServer.SimpleXMLRPCServer(("127.0.0.1", 1234))
server.register_instance(obj)

print "Listening on port 1234"
server.serve_forever()