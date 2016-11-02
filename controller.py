import xmlrpc.client
import ssl
import socket     # Required for network/socket connections
import os         # Required for Forking/child processes
import time       # Required for sleep call
import threading  # Required for communication sub-threads
import pymysql
import server_controller as myServer
import certs.gencert as gencert
import config
import logging
from logging.config import fileConfig

# Load logging config
fileConfig('setup/logging.conf')
log = logging.getLogger(__name__)


# Global Variables -- Don't change. [No need to change.]
CERTFILE = "certs/domains/local.cert"   # Placeholder; updated when executed
KEYFILE = "certs/domains/local.key"     # Default; updated when executed
hostIP = "localhost"                    # Default; updated when executed
admin_selected = False


# Return ip address of local host where server is running
def getMyIP():
    log.info('Getting Host ip address.')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    ipAdd = s.getsockname()[0]
    s.close()
    log.debug('Socket closed: ipAdd=%s' % ipAdd)
    return ipAdd


# Return host name/fqdn of based on give ip address
def findHostName(ipAddress):
    log.info('Finding Host Name based on ip address')
    try:
        log.debug('Trying now...')
        name, alias, addresslist = socket.gethostbyaddr(ipAddress)
        log.debug('Returning name: %s' % name)
        return name
    except socket.herror:
        log.exception("Hostname/FQDN not found: Hostname/FQDN Required. "
                      "Correct by adding record in DNS server or within local"
                      "hosts file (/etc/hosts) and then restart controller.")
        return "None"


# Create SSL certs for current ip address if not already present
def verifyCerts():
    global CERTFILE
    global KEYFILE

    # Determine file path based on current ip address
    CERTFILE = ''.join([config.certPath, config.rootDomain, ".cert"])
    KEYFILE = ''.join([config.certPath, config.rootDomain, ".key"])
    log.debug("CERTFILE: %s" % (CERTFILE))
    log.debug("KEYFILE: %s" % (KEYFILE))

    # If cert or key file not present, create new certs
    if not os.path.isfile(CERTFILE) or not os.path.isfile(KEYFILE):
        gencert.gencert(config.rootDomain)
        log.info("Certfile(s) NOT present; new certs created.")
        print("Certfile(s) NOT present; new certs created.")

    else:
        log.info("Certfiles Verified Present")
        print("Certfiles Verified Present.")


# Start a thread child to run server connection as a daemon
def startServer():

    log.info("Starting Server...")

    # Now, start thread
    log.debug("Starting new thread...")
    t = threading.Thread(name="ServerDaemon",
                         target=myServer.runServer,
                         args=(hostIP,
                               config.ctlrServerPort,
                               CERTFILE,
                               KEYFILE
                               )
                         )
    t.daemon = True
    t.start()
    log.debug("Thread started; end of startServer fn.")


# Check and Display the status of all child processes
def checkStatus():
    log.debug("Checking Status of Threads...")
    totalThreads = threading.active_count()
    subThreads = totalThreads - 1
    print("\nSub-Thread(s): %d" % (subThreads))

    main_thread = threading.currentThread()
    k = 1
    for t in threading.enumerate():
        if t is main_thread:
            continue
        print("Thread #%d:" % (k))
        print("Name: %s" % (t.name))
        print("Ident: %d" % (t.ident))
        ans = "unknown"
        if t.is_alive():
            ans = "YES"
        else:
            ans = "NO"
        print("Alive? %s\n" % (ans))
        k = k+1
    log.debug("End of checkStatus fn.")


# Start a thread child to run control agent as daemon
def startControlAgent(hostName, portNum):

    log.info("Starting Server...")

    # Now, start thread
    log.debug("Starting new thread...")
    t = threading.Thread(name="ControlAgent",
                         target=myServer.controlAgent,
                         args=(hostName,
                               portNum,
                               "SELF TEST"
                               )
                         )
    t.daemon = True
    t.start()
    log.debug("Thread started; end of startControlAgent fn.")


# Display Agents currently connected
def displayAgents(shortList=False):
    log.debug("Displaying agents now")
    if not shortList:
        print("Displaying agents currently connected...")
    # Connect to database to query agents
    log.debug("Connecting to database")
    db = pymysql.connect(host=config.mysqlHost, port=config.mysqlPort,
                         user=config.ctlrMysqlUser, passwd=config.ctlrMysqlPwd,
                         db=config.mysqlDB)
    cursor = db.cursor()

    # Query to retrieve id/time of registration
    sql = "SELECT distinct host FROM agents;"

    hosts = []
    savedResults = []

    # Get hosts
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists
        results = cursor.fetchall()
        for row in results:
            thisHost = row[0]
            hosts.append(thisHost)

        log.debug("Host Received as: %s" % (thisHost))

    except:
        log.exception("ERROR in db query>> %s" % sql)

    if shortList:
        log.debug("FOUND %d agent(s) connected." % len(hosts))
    else:
        print("FOUND %d agent(s) connected." % len(hosts))

    # Query to retrieve each host's data
    for k in range(len(hosts)):
        sql = "SELECT host, port, timestamp, alias, id FROM "\
              "agents where host = '%s' ORDER BY id "\
              "DESC LIMIT 1" % (hosts[k])

        # Get host info
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Fetch all the rows in a list of lists
            results = cursor.fetchall()
            savedResults.append(results)
            if not shortList:
                print("Agent #%d" % (k + 1))
            for row in results:
                thisHost = row[0]
                thisPort = row[1]
                thisTime = row[2]
                thisAlias = row[3]
                thisID = row[4]

            if shortList:
                print("%d) Host: %s; Alias: %s; ID: %s" % ((k+1), thisHost,
                                                           thisAlias, thisID))
            else:
                print("Host: %s" % thisHost)
                print("Alias: %s" % thisAlias)
                print("Port: %s" % thisPort)
                print("Time Connected: %s" % thisTime)
                print("ID Number: %s\n" % thisID)

            log.debug("Host %d Displayed" % (k + 1))

        except:
            log.exception("ERROR in db query>> %s" % sql)

    # Disconnect from database
    db.close()

    return savedResults


# Select which function to call based on command selected
def processCommand(numSelected, thisHost, thisPort):
    # TODO Finish this
    log.debug("Processing command...")
    if numSelected == "1":
        rsp = myServer.sendStart(thisHost, thisPort)
        log.debug("Num1 Response: %s" % rsp)
    elif numSelected == "2":
        rsp = myServer.sendStop(thisHost, thisPort)
        log.debug("Num2 Response: %s" % rsp)
    elif numSelected == "5":
        rsp = myServer.sendClone(thisHost, thisPort)
        log.debug("Num5 Response: %s" % rsp)
        print("'Complete CLone' Command Executing...")
        print("WARNING: This make take a few minutes. Please be patient")
    else:
        print("Functionality NOT implemented or BAD selection.")


# Send command to Agent manually
def sendCommand():
    log.debug("Send Command to Agent -- Menu.")
    print("Send a command to which Agent?")
    hostOptions = displayAgents(shortList=True)
    selection1 = input("Select a number:\n>>> ")

    print("You selected Agent #%s" % selection1)
    hostSelected = hostOptions[(int(selection1) - 1)][0][0]
    portSelected = hostOptions[(int(selection1) - 1)][0][1]
    print("Host: %s; Port: %s" % (hostSelected, portSelected))
    log.debug(hostOptions[(int(selection1) - 1)])
    log.debug("Host: %s; Port: %s" % (hostSelected, portSelected))

    print("Which command?")
    myServer.displayCommandList()
    selection2 = input("Select a number:\n>>> ")

    print("You selected Command#%s" % selection2)
    processCommand(selection2, hostSelected, portSelected)
    log.debug("End of SendCommand function")


# Simple test function to ensure communication is working
def mathTest():

    log.debug("Start of Math Test Function...")
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(config.CACERTFILE)

    myurl = ''.join(['https://', config.agntHostName, ':',
                     str(config.agntServerPort)])
    with xmlrpc.client.ServerProxy(myurl,
                                   context=myContext) as proxy:
        try:
            print("5 + 9 is %d" % (proxy.add(5, 9)))
            print("21 x 3 is: %d" % (proxy.multiply(21, 3)))

        except ConnectionRefusedError:
            log.warning("Connection to Agent Server FAILED")
            print("Connection to Agent Server FAILED:\n",
                  "Is Agent listening? Confirm connection",
                  "settings and try again.")
            print("Settings used: '%s'" % myurl)

        except:
            log.warning("Connection to Agent Server FAILED")
            print("Connection Failed. Suspected incorrect URL.")
            print("Settings used: '%s'" % myurl)


# Quit gracefully after terminting all child processes
def myQuit():
    log.info("Controller Exiting. Goodbye.")
    print("Controller Exiting. Goodbye.\n")
    raise SystemExit


# Stop Controller Server
def stopServer():
    log.debug("Stopping Controller Server.")
    # TODO Determine if it is possible to stop a daemon thread
    # without stopping the whole program; for now, this just
    # ends the entire program
    print("Controller Server Stopping.")
    myQuit()


def invalid(choice):
    log.debug("Invalid choice: %s" % choice)
    print("INVALID CHOICE!")


def adminMenu():
    log.debug("Displaying admin menu")
    print("\nAdmin Menu:")
    print("a) Connection Test (simple math test)")
    print("b) SSL Verification (verify certificates")
    print("c) STOP Controller Server (program will exit)")
    print("d) START* Controller Server (only if not running already)")
    print("e) TEST register/control Agent (using Agent default settings)")
    print("9) BACK (return to 'Menu')")
    return input("Make a Choice\n>>> ")


def adminSelection():
    global admin_selected
    adminChoice = adminMenu()
    if adminChoice == "a":
        mathTest()
    elif adminChoice == "b":
        verifyCerts()
    elif adminChoice == "c":
        stopServer()
    elif adminChoice == "d":
        startServer()
    elif adminChoice == "e":
        startControlAgent("agent.shn.local", 38000)
    elif adminChoice == "9":
        log.debug("Admin is De-selected")
        print("Back to Main Menu...")
        admin_selected = False
    elif adminChoice == "r":
        # Refresh Menu (do nothing)
        log.info("Refreshing Menu")
    elif adminChoice in ["q", ":q"]:
        myQuit()
    else:
        invalid(adminChoice)


def menu():
    log.debug("Displaying menu")
    print("\n\nMENU[Controller]:")
    print("1) Check CONTROLLER server status")
    print("2) Display Connected Agents")
    print("3) Send Command to Agent")
    print("9) ADMIN MENU")
    print("q) QUIT")
    return input("Make a Choice\n>>> ")


def myMenu():
    global admin_selected
    choice = 0
    if admin_selected:
        choice = "9"
    else:
        choice = menu()
    if choice == "1":
        checkStatus()
    elif choice == "2":
        displayAgents()
    elif choice == "3":
        sendCommand()
    elif choice == "9":
        admin_selected = True
        log.debug("Admin is Selected")
        adminSelection()
    elif choice in ["q", ":q"]:
        myQuit()
    elif choice == "r":
        # Refresh Menu (do nothing)
        log.info("Refreshing Menu")
    else:
        invalid(choice)


# Start of Main
if __name__ == '__main__':
    log.info("Starting Main.")
    hostIP = getMyIP()
    verifyHostName = findHostName(hostIP)
    pid = os.getpid()
    print("Host IP: %s" % (hostIP))
    print("Hostname: %s" % (verifyHostName))
    log.debug("PID: %d" % (pid))

    if verifyHostName == "None":
        log.debug("Hostname not found: Returned 'None'")

    elif verifyHostName in [config.ctlrHostName, config.mntrHostName]:
        log.debug("HostName verified.")

        log.debug("Verifying certificates.")
        # Verify certificates present prior to displaying menu
        verifyCerts()

        # Starting Server
        startServer()
        time.sleep(2)

        # Display Menu [repeatedly] for user
        while True:
            myMenu()
            time.sleep(1)

    else:
        log.error("Hostname incorrect. "
                  "Hostname Found: %s; Hostname "
                  "Required: %s." % (verifyHostName, config.ctlrHostName))
