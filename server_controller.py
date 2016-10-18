from xmlrpc.server import SimpleXMLRPCServer
import ssl
import controller
import threading
import logging


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
    log = logging.getLogger(__name__)
    log.info("Starting runServer Module")
    log.debug("serverCert: %s" % (serverCert))
    log.debug("serverKey: %s" % (serverKey))

    # Create XMLRPC Server, based on ipAdd/port received
    server = SimpleXMLRPCServer((ipAdd, portNum))

    # Create/Wrap server socket with ssl
    try:
        log.debug("Trying socket now...")
        server.socket = ssl.wrap_socket(server.socket,
                                        certfile=serverCert,
                                        keyfile=serverKey,
                                        do_handshake_on_connect=True,
                                        server_side=True)
        # Register available functions
        log.debug("Registering Functions")
        server.register_multicall_functions()
        server.register_function(add, 'add')
        server.register_function(subtract, 'subtract')
        server.register_function(multiply, 'multiply')
        server.register_function(divide, 'divide')
        server.register_function(connectToServer, 'connectToServer')

        # Start server listening [forever]
        log.info("Server listening on port %d." % (portNum))
        print("Server listening on port %d." % (portNum))
        server.serve_forever()

    except OSError:
        log.exception("ERROR creating socket...")
        log.critical("--CERT or KEY FILE not found.")
        log.critical("--QUIT and RESTART CONTROLLER.")
