from xmlrpc.server import SimpleXMLRPCServer
import ssl
import os
import controller
import threading


######################################
# Define functions available to server
######################################
def add(x, y):
    return x+y


def subtract(x, y):
    return x-y


def multiply(x, y):
    return x*y


def divide(x, y):
    return x/y


def connectToServer(hostName, portNum):

    # Start child process to run function for
    #  communicating with Agent
    tName = ''.join(["Server-", hostName])
    t = threading.Thread(name=tName,
                         target=controller.controlAgent,
                         args=(hostName,
                               portNum
                               )
                         )
    t.daemon = True
    t.start()

    # Connect to Agent running at hostName, listening on portNum
    return "Connecting"


#########################################
# Main server function: An xml rpc server
# for responding to client requests.
#########################################
def runServer(ipAdd, portNum, serverCert, serverKey):
    print("runServer Module PID: %d" % (os.getpid()))

    print("serverCert: %s\nserverKey: %s" % (serverCert, serverKey))

    # Create XMLRPC Server, based on ipAdd/port received
    server = SimpleXMLRPCServer((ipAdd, portNum))

    # Create/Wrap server socket with ssl
    try:
        server.socket = ssl.wrap_socket(server.socket,
                                        certfile=serverCert,
                                        keyfile=serverKey,
                                        do_handshake_on_connect=True,
                                        server_side=True)
        # Register available functions
        server.register_multicall_functions()
        server.register_function(add, 'add')
        server.register_function(subtract, 'subtract')
        server.register_function(multiply, 'multiply')
        server.register_function(divide, 'divide')
        server.register_function(connectToServer, 'connectToServer')

        # Start server listening [forever]
        server.serve_forever()

        print("Listening on port %d..." % (portNum))

    except OSError:
        print("ERROR!!!\n--Error creating socket...")
        print("--CERT or KEY FILE not found.")
        print("--QUIT and RESTART CONTROLLER.")
