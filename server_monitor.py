from xmlrpc.server import SimpleXMLRPCServer
import ssl
import logging
import pymysql
import config
import xmlrpc.client


#####################################################
# Main Logic for Monitor Receiving Updates
#####################################################
def reportStatus(host, status, port, agtAlias, ctlrid=0):
    log = logging.getLogger(__name__)
    log.debug("Start of reportStatus Function...")
    print("Monitor Processing...")

    # Connect to database to register agent
    log.debug("Connecting to database")
    db = pymysql.connect(host=config.mysqlHost, port=config.mysqlPort,
                         user=config.ctlrMysqlUser, passwd=config.ctlrMysqlPwd,
                         db=config.mysqlDB)
    cursor = db.cursor()

    # Query to register agent
    sql = "INSERT INTO status(timestamp, "\
          "agent, ctlrid, status, alias) "\
          "VALUES (now(), '%s', %d, %d, '%s')" % \
        (host, ctlrid, status, agtAlias)

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
    sql = "SELECT id, timestamp, agent "\
          "FROM status WHERE (agent, status) = "\
          "('%s', %d) ORDER BY id DESC LIMIT 1" % \
        (host, status)

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
            print("Sending Confirmation...")
            if success:
                log.debug("Insert SUCCESS. [success==True]")
                response = proxy.confirm(config.mntrHostName,
                                         config.mntrServerPort,
                                         thisID, thisTime)
                log.info(response)
            else:
                log.debug("Insert FAILURE. [success==False]")
                response = proxy.failed(config.mntrHostName)
                log.info(response)

        except ConnectionRefusedError:
            log.warning("Connection to Agent FAILED")
            print("Connection to Agent FAILED:")
            print("Is Agent listening? Confirm and try again.")

    log.debug("End or reportStatus Function")

    mymsg = ''.join(["Registering Update Complete; ", host,
                     " Status: ", str(status), "."])
    log.debug(mymsg)
    return mymsg


#############################################################
# Define functions available to server via remote connections
#############################################################
def add(x, y):
    return x+y


def multiply(x, y):
    return x*y


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
        server.register_function(reportStatus, 'reportStatus')

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
                      "available for monitor." % portNum)
