#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SimpleXMLRPCServer

from proc_files import Proc
from plat import get_uname, get_system, get_node, get_linux_distribution

obj = Proc()
obj.get_uname = get_uname
obj.get_system = get_system
obj.get_node = get_node
obj.get_linux_distribution = get_linux_distribution

server = SimpleXMLRPCServer.SimpleXMLRPCServer(("127.0.0.1", 1236))
server.register_instance(obj)

print "Listening on port 1234"
server.serve_forever()