import xmlrpclib

server = xmlrpclib.ServerProxy("http://0.0.0.0:1234")

print server.get_uname()
