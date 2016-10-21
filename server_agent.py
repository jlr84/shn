from xmlrpc.server import SimpleXMLRPCServer
import ssl
import logging
import config
import dbm


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


def failed(name):
    log = logging.getLogger(__name__)
    log.debug("Agent registration with %s FAILED." % name)
    return "Failed registration acknowledged."


def confirm(name, idnum, time):
    log = logging.getLogger(__name__)
    log.debug("Agent Registered to "
              "%s [Conf# %d] at %s." % (name, idnum, time))

    log.debug("Values Received: %s, %d, %s" % (name, idnum, time))
    storeName = str(name)
    storeID = str(idnum)
    storeTime = str(time)
    log.debug("Values Storing: %s, %s, %s" % (storeName, storeID, storeTime))

    try:
        with dbm.open('cache_agent', 'w') as db:
            # Get current total and add 1 with type conversions
            newtotal = str(int((db.get('total')).decode("utf-8")) + 1)
            # Store new total in persistent storage
            db['total'] = newtotal
            # Create names based on connection number
            savename = "%s.name" % (newtotal)
            saveid = "%s.id" % (newtotal)
            savetime = "%s.time" % (newtotal)
            # Save connection info to persistent storage
            db[savename] = storeName
            db[saveid] = storeID
            db[savetime] = storeTime
            log.debug("Cache found. Values stored in old cache.")
            log.debug("Saved: %s, %s, %s" % (storeName, storeID, storeTime))
    except:
        log.debug("No cache file found; creating new file.")
        with dbm.open('cache_agent', 'c') as db:
            db['total'] = "1"
            savename = "1.name"
            saveid = "1.id"
            savetime = "1.time"
            db[savename] = storeName
            db[saveid] = storeID
            db[savetime] = storeTime
            log.debug("Saved: %s, %s, %s" % (storeName, storeID, storeTime))

    returnMessage = ''.join(["Conf# ", str(idnum), " Acknowledged."])
    return returnMessage


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
    log.debug("Trying socket now...")
    foundPort = False
    loopNumber = 1
    config.AgentServerUp = False
    while not foundPort and loopNumber < 3:
        try:
            server = SimpleXMLRPCServer((ipAdd, portNum))
            foundPort = True
            config.agentServerUp = True

        except OSError:
            log.debug("Port [%d] already in use." % portNum)
            # Keep port range between 35000 and 39000
            if portNum < 39000:
                portNum = portNum + 1
            else:
                portNum = 35000
                loopNumber = loopNumber + 1

    if loopNumber > 2:
        log.exception("NO open ports found!!!")
        raise SystemExit

    # Set global var in agent to portNum used
    config.agntServerPort = portNum

    # Create/Wrap server socket with ssl
    try:
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
        server.register_function(confirm, 'confirm')
        server.register_function(failed, 'failed')

        # Start server listening [forever]
        log.info("Server listening on port %d..." % (portNum))
        print("Server listening on port %d..." % (portNum))
        server.serve_forever()

    except FileNotFoundError:
        log.warning("CERT or KEY FILE not found.")
        log.warning("Verify CERT/KEY Files and try again.")
