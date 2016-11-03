from xmlrpc.server import SimpleXMLRPCServer
import ssl
import logging
import config
import dbm
import subprocess
import datetime


######################################
# Supporting Functions
######################################
# Return name of current VUD/VM
def getCurrentVUD():
    log = logging.getLogger(__name__)
    log.debug("Getting current VM/VUD name...")
    currentVUD = "NONE"
    try:
        with dbm.open('cache_agent_history', 'r') as db:
            currentVUD = (db.get('current')).decode("utf-8")
            log.debug("Name retreived: '%s'" % currentVUD)
    except:
        log.debug("No cache found or read failed")

    return currentVUD


# Return name to use for clone
def getCloneName(currentName):
    log = logging.getLogger(__name__)
    log.debug("Finding name for clone...")
    fileName = "ERROR"

    # Starting with 1, test if clone name exists until name is found
    # that does not exist
    exists = True
    num = 1
    while exists:
        # Create name
        fileName = ''.join([currentName, "_clone_", str(num)])
        log.debug("Trying name: %s" % fileName)
        try:
            with dbm.open('cache_agent_history', 'r') as db:
                oldClone = db.get(fileName)
                log.debug("Clone name tested as: %s" % oldClone)
                if oldClone is None:
                    exists = False
                else:
                    num = num + 1
        except:
            log.warning("No cache found or read failed")
            exists = False

    log.debug("Returning name: %s" % fileName)
    return fileName


# Save successful clone name to persistent memory
def saveCloneName(newName, timeSaved):
    log = logging.getLogger(__name__)
    log.debug("Saving clone name to memory...")
    status = "FAILED"
    try:
        with dbm.open('cache_agent_history', 'c') as db:
            # Store name and time pair to memory
            db[newName] = timeSaved
            log.debug("Saved clone name: %s" % newName)
            status = "SUCCESS"
    except:
        log.warning("ERROR writing to cache.")

    return status


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


def startVM(key):
    log = logging.getLogger(__name__)
    log.debug("Starting up VM...")
    result = "NO ACTION TAKEN"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Make process call string
    callString = ''.join(["/usr/sbin/xl create /etc/xen/", vudName, ".cfg"])
    log.debug("Command: %s" % callString)

    # Execute Command
    if key == "start":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "Success"
            elif rc == 1:
                result = "Failed"
                print("Starting VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                log.debug("Starting VM: %s." % result)
        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to start"
            log.debug("No VM Started: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    return "Starting VM[%s]: %s." % (vudName, result)


def stopVM(key):
    log = logging.getLogger(__name__)
    log.debug("Stopping VM...")
    result = "NO ACTION TAKEN"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Make process call string
    callString = ''.join(["/usr/sbin/xl shutdown ", vudName])
    log.debug("Command: %s" % callString)

    if key == "stop":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "Success"
            elif rc == 1:
                result = "Failed"
                print("Stopping VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                print("Stopping VM... FAILED")

            log.debug("Stopping VM %s." % result)
        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to stop"
            log.debug("No VM Stopped: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    return "Shutting down VM[%s]: %s." % (vudName, result)


def cloneVM(key):
    log = logging.getLogger(__name__)
    log.debug("Cloning VM...")
    result = "NO ACTION TAKEN"
    result2 = "NO RESULT FOR WRITE"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Get name for clone
    cloneName = getCloneName(vudName)

    # Make process call string
    callString = ''.join(["./scripts/clone.sh ", vudName, " ", cloneName])
    log.debug("Command: %s" % callString)
    log.info("WARNING: This may take a few minutes!")

    if key == "clone":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "Success"
            elif rc == 1:
                result = "Failed"
                print("Cloning VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                print("Cloning VM... FAILED")

            log.debug("Cloning VM %s." % result)

            # Save clone name in persistent memory
            saveTime = str((datetime.datetime.now()).isoformat())
            result2 = saveCloneName(cloneName, saveTime)
            log.debug("Saved to memory: %s saved at %s" % (cloneName, saveTime))
            log.info("Write to DB result: %s" % result2)

        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to clone"
            log.debug("No VM Cloned: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    # Summarize cloning result prior to sending back to user
    if result == "SUCCESS" and result2 == "SUCCESS":
        result3 = ''.join(["Cloning VM[", vudName, "]: Clone-", result,
                           ", DB Save-", result2, ", saved as '",
                           cloneName, "'"])
        log.debug("Result logged as: %s" % result3)
    else:
        result3 = ''.join(["Cloning VM[", vudName, "] FAILED: Clone-", result,
                           ", DB Save-", result2])
        log.debug("Result logged as: %s" % result3)

    return result3


def failed(name):
    log = logging.getLogger(__name__)
    log.debug("Agent registration with %s FAILED." % name)
    return "Failed registration acknowledged."


def confirm(name, port, idnum, time):
    log = logging.getLogger(__name__)
    log.debug("Agent Registered to "
              "%s:%d [Conf# %d] at %s." % (name, port, idnum, time))

    log.debug("Values Received: %s, %d, %d, %s" % (name, port, idnum, time))
    storeName = str(name)
    storePort = str(port)
    storeID = str(idnum)
    storeTime = str(time)
    log.debug("Values Storing: %s, %s, %s, %s" % (storeName, storePort,
                                                  storeID, storeTime))

    try:
        with dbm.open('cache_agent', 'w') as db:
            # Get current total and add 1 with type conversions
            newtotal = str(int((db.get('total')).decode("utf-8")) + 1)
            # Store new total in persistent storage
            db['total'] = newtotal
            # Create names based on connection number
            savename = "%s.name" % (newtotal)
            saveport = "%s.port" % (newtotal)
            saveid = "%s.id" % (newtotal)
            savetime = "%s.time" % (newtotal)
            # Save connection info to persistent storage
            db[savename] = storeName
            db[saveport] = storePort
            db[saveid] = storeID
            db[savetime] = storeTime
            log.debug("Cache found. Values stored in old cache.")
            log.debug("Saved: %s, %s, %s, %s" % (storeName, storePort,
                                                 storeID, storeTime))
    except:
        log.debug("No cache file found; creating new file.")
        with dbm.open('cache_agent', 'c') as db:
            db['total'] = "1"
            savename = "1.name"
            saveport = "1.port"
            saveid = "1.id"
            savetime = "1.time"
            db[savename] = storeName
            db[saveport] = storePort
            db[saveid] = storeID
            db[savetime] = storeTime
            log.debug("Saved: %s, %s, %s, %s" % (storeName, storePort,
                                                 storeID, storeTime))

    returnMessage = ''.join(["Conf# ", str(idnum), " Acknowledged."])
    print("Registration Acknowledged (ID#%d)" % (idnum))
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
        server.register_function(startVM, 'startVM')
        server.register_function(stopVM, 'stopVM')
        server.register_function(cloneVM, 'cloneVM')

        # Start server listening [forever]
        log.info("Server listening on port %d..." % (portNum))
        print("Server listening on port %d..." % (portNum))
        server.serve_forever()

    except FileNotFoundError:
        log.warning("CERT or KEY FILE not found.")
        log.warning("Verify CERT/KEY Files and try again.")
