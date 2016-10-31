from xmlrpc.server import SimpleXMLRPCServer
import ssl
import threading
import logging
import pymysql
import config
import xmlrpc.client
import time


#####################################################
# Main Logic for Controller communicating to Agent(s)
#####################################################
def controlAgent(host, port, agtAlias):
    log = logging.getLogger(__name__)
    log.debug("Start of controlAgent Function...")
    print("ControlAgent Daemon Started")

    # Connect to database to register agent
    log.debug("Connecting to database")
    db = pymysql.connect(host=config.mysqlHost, port=config.mysqlPort,
                         user=config.ctlrMysqlUser, passwd=config.ctlrMysqlPwd,
                         db=config.mysqlDB)
    cursor = db.cursor()

    # Query to register agent
    sql = "INSERT INTO agents(timestamp, "\
          "host, port, alias) "\
          "VALUES (now(), '%s', %d, '%s')" % \
        (host, port, agtAlias)

    log.debug("SQL Query Made [shown as follows]:")
    log.debug(sql)

    # Register Agent in database
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit changes in the database
        db.commit()
        log.debug("SQL INSERT Successful")
    except:
        # Rollback in case there is any error
        db.rollback()
        log.exception("SQL INSERT FAILED!!")

    # Query to retrieve id/time of registration
    sql = "SELECT id, timestamp, host, port "\
          "FROM agents WHERE (host, port) = "\
          "('%s', %d) ORDER BY id DESC LIMIT 1" % \
        (host, port)

    success = False

    # Get id/time of registration
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists
        results = cursor.fetchall()
        for row in results:
            thisID = row[0]
            thisTime = row[1]
            thisTime = str(thisTime.isoformat())
        success = True
        log.debug("ID/TIME Recorded as: %d, %s" % (thisID, thisTime))

    except:
        log.exception("ERROR in db query>> %s" % sql)

    # Disconnect from database
    db.close()

    # Connect to Agent's server daemon to confirm
    # registration
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(config.CACERTFILE)

    thisHost = ''.join(['https://', host, ':', str(port)])

    with xmlrpc.client.ServerProxy(thisHost,
                                   context=myContext) as proxy:

        try:
            log.info("Sending Confirmation...")
            if success:
                log.debug("Insert SUCCESS. [success==True]")
                response = proxy.confirm(config.ctlrHostName,
                                         config.ctlrServerPort,
                                         thisID, thisTime)
                log.info(response)
                print("Connection to Agent ESTABLISHED")
            else:
                log.debug("Insert FAILURE. [success==False]")
                response = proxy.failed(config.ctlrHostName)
                log.info(response)
                print("Connection to Agent FAILED")

        except ConnectionRefusedError:
            log.warning("Connection to Agent FAILED")
            print("Connection to Agent FAILED:")
            print("Is Agent listening? Confirm and try again.")

        except:
            log.warning("Connection to Agent FAILED")
            print("Connection Failed. Suspected incorrect URL.")
            print("Settings used: '%s'" % thisHost)

    log.info("Entering 'while True' loop now.")
    while True:
        log.info("ControlAgent: Sleeping for 60 seconds...")
        time.sleep(60)

        # Connect to database to check monitor
        log.debug("Connecting to database")
        db = pymysql.connect(host=config.mysqlHost, port=config.mysqlPort,
                             user=config.ctlrMysqlUser,
                             passwd=config.ctlrMysqlPwd,
                             db=config.mysqlDB)
        cursor = db.cursor()

        # Query to check agent
        sql = "SELECT status, timestamp FROM status WHERE "\
              "alias = '%s' ORDER BY timestamp DESC LIMIT 1;" % \
            (agtAlias)

        log.debug("SQL Query Made [shown as follows]:")
        log.debug(sql)

        # Register Agent in database
        try:
            # Execute the SQL command
            cursor.execute(sql)

            thisAnswer = 0
            thisTime = "None"

            # Fetch all the rows
            results = cursor.fetchall()
            for row in results:
                thisAnswer = row[0]
                thisTime = row[1]

            log.debug("thisAnswer: %s" % thisAnswer)
            if thisAnswer == 1:
                log.debug("Host '%s' CLEAN as of '%s'." % (host, thisTime))
                print("Host '%s' CLEAN as of '%s'." % (host, thisTime))
            elif thisAnswer == 0:
                log.debug("Host NOT FOUND in status database!!")
                print("Host NOT FOUND in status database!!")
            else:
                log.debug("Host '%s' INFECTED!! as of '%s'." % (host, thisTime))
                print("Host '%s' INFECTED!! as of '%s'." % (host, thisTime))
                # TODO Make function to take appropriate action

            log.debug("Monitor query update successful")
        except:
            # Rollback in case there is any error
            log.exception("ERROR in db query>> %s" % sql)


#############################################################
# Define functions available to server via remote connections
#############################################################
def add(x, y):
    return x+y


def multiply(x, y):
    return x*y


# Disconnect Agent from controller
def disconnectAgent(agentHostName, connectionID, timestamp):
    log = logging.getLogger(__name__)
    log.info("Starting Disconnect Agent function")

    # Connect to database to disconnect agent
    log.debug("Connecting to database")
    db = pymysql.connect(host=config.mysqlHost, port=config.mysqlPort,
                         user=config.ctlrMysqlUser, passwd=config.ctlrMysqlPwd,
                         db=config.mysqlDB)
    cursor = db.cursor()

    # Query to retrieve id/time of registration
    sql = "SELECT id, host, timestamp "\
          "FROM agents WHERE (host, id) = "\
          "('%s', %s) ORDER BY timestamp DESC LIMIT 1" % \
        (agentHostName, connectionID)

    # Get time of registration
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists
        results = cursor.fetchall()
        for row in results:
            thisID = row[0]
            thisTime = row[2]
            thisTime = str(thisTime.isoformat())

        log.debug("ID/TIME Recorded as: %d, %s" % (thisID, thisTime))

        if thisTime == timestamp:
            log.debug("TIMESTAMPS MATCH!!!")
            log.debug("Removing from database...")

            # Query to delete proper rows
            sql = "DELETE FROM agents WHERE host='%s' "\
                  "AND id<=%s;" % \
                (agentHostName, connectionID)

            # Try delete operation
            try:
                # Execute the SQL command
                cursor.execute(sql)
                # Commit the changes
                db.commit()
                log.info("Records successfully deleted.")
            except:
                db.rollback()
                log.exception("ERROR in db query>> %s" % sql)
        else:
            log.warning("Timestamps DO NOT match!!")

    except:
        log.exception("ERROR in db query>> %s" % sql)

    # Disconnect from database
    db.close()
    return "Successful Disconnect"


# Register Agent with Controller so Agent can receive commands
def registerAgent(agentHostName, agentPortNum, agentAlias):
    log = logging.getLogger(__name__)
    log.info("Starting registerAgent function")

    # Start child process to run function for
    #  registering and eommunicating with Agent
    tName = ''.join(["Controller_to_", agentHostName])
    t = threading.Thread(name=tName,
                         target=controlAgent,
                         args=(agentHostName,
                               agentPortNum,
                               agentAlias
                               )
                         )
    t.daemon = True
    t.start()

    # Connect to Agent running at hostName, listening on portNum
    mymsg = ''.join(["Registering Agent '", agentHostName, "'..."])
    log.debug(mymsg)
    return mymsg


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
    try:
        server = SimpleXMLRPCServer((ipAdd, portNum))

        # Create/Wrap server socket with ssl
        server.socket = ssl.wrap_socket(server.socket,
                                        certfile=serverCert,
                                        keyfile=serverKey,
                                        do_handshake_on_connect=True,
                                        server_side=True)
        # Register available functions
        log.debug("Registering Functions")
        server.register_multicall_functions()
        server.register_function(add, 'add')
        server.register_function(multiply, 'multiply')
        server.register_function(disconnectAgent, 'disconnectAgent')
        server.register_function(registerAgent, 'registerAgent')

        # Start server listening [forever]
        log.info("Server listening on port %d." % (portNum))
        print("Server listening on port %d." % (portNum))
        server.serve_forever()

    except FileNotFoundError:
        log.exception("ERROR creating socket... "
                      "CERT or KEY NOT Present.")
    except OSError:
        log.exception("ERROR creating socket..."
                      "Verify port number [%d] is "
                      "available for controller." % portNum)
