from SimpleXMLRPCServer import SimpleXMLRPCServer
import os

def add(x,y):
    return x+y

def subtract(x, y):
    return x-y

def multiply(x, y):
    return x*y

def divide(x, y):
    return x/y

# A simple server with simple arithmetic functions
def runServer(ipAdd,portNum):
    print "runServer Module PID: %d" % (os.getpid())
    server = SimpleXMLRPCServer((ipAdd, portNum))
    print "Listening on port %d..." % (portNum)
    server.register_multicall_functions()
    server.register_function(add, 'add')
    server.register_function(subtract, 'subtract')
    server.register_function(multiply, 'multiply')
    server.register_function(divide, 'divide')
    server.serve_forever()
