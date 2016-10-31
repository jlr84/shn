import xmlrpc.client
import ssl
import socket     # Required for network/socket connections
import os         # Required for Forking/child processes
import sys        # Required for getting command-line arguments
import time       # Required for sleep call
import threading  # Required for communication sub-threads
import datetime
import dbm
import server_agent as myServer
import certs.gencert as gencert
import config
import logging
from logging.config import fileConfig

# Load logging config
fileConfig('logging.conf')
log = logging.getLogger(__name__)

# Global Variables -- Don't change. [No need to change.]
CERTFILE = "certs/domains/local.cert"   # Placeholder; updated when executed
KEYFILE = "certs/domains/local.key"     # Placeholder; updated when executed
hostIP = "localhost"                    # Default; updated when executed
AGENT_ALIAS = "agent"   # Default; updated to match hostname when executed
admin_selected = False


# Return ip address of local host where server is running
def getMyIP():
    log.info('Getting Host ip address')
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
    log.debug("CERTFILE: %s" % CERTFILE)
    log.debug("KEYFILE: %s" % KEYFILE)

    # If cert or key file not present, create new certs
    if not os.path.isfile(CERTFILE) or not os.path.isfile(KEYFILE):
        gencert.gencert(config.rootDomain)
        log.info("Certfile(s) NOT present; new certs created.")
        print("Certfile(s) NOT present; new certs created.")

    else:
        log.info("Certfiles Verified Present")
        print("Certfiles Verified Present")


# Check and Display the status of all child processes
def checkServer(do_not_print=False):
    log.debug("Checking Status of Agent Server Thread(s)...")
    totalThreads = threading.active_count()
    subThreads = totalThreads - 1

    if do_not_print:
        log.debug("Total Agent Server(s): %d" % (subThreads))
    else:
        print("\nTotal Agent Server(s): %d" % (subThreads))

    main_thread = threading.currentThread()
    k = 1
    for t in threading.enumerate():
        if t is main_thread:
            continue
        if do_not_print:
            log.debug("Thread #%d:" % (k))
            log.debug("Name: %s" % (t.name))
            log.debug("Ident: %d" % (t.ident))
        else:
            print("Thread #%d:" % (k))
            print("Name: %s" % (t.name))
            print("Ident: %d" % (t.ident))
        ans = "unknown"
        if t.is_alive():
            ans = "YES"
        else:
            ans = "NO"
        if do_not_print:
            log.debug("Alive? %s" % (ans))
        else:
            print("Alive? %s\n" % (ans))
        k = k + 1
    log.debug("End of checkServer fn.")
    return subThreads


# Establish connection with Controller
def establishConnection(remoteName, remotePort):

    log.debug("Start of Establish Connection Function...")
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(config.CACERTFILE)

    myurl = ''.join(['https://', remoteName, ':', str(remotePort)])
    with xmlrpc.client.ServerProxy(myurl,
                                   context=myContext) as proxy:

        # Send server my name and port number
        try:
            print("Register with controller:",
                  "%s" % (proxy.registerAgent(config.agntHostName,
                                              config.agntServerPort,
                                              AGENT_ALIAS)))

        except ConnectionRefusedError:
            log.warning("Connection to Controller Server FAILED")
            print("Connection to Controller Server FAILED:\n",
                  "Is Controller listening? Confirm connection",
                  "settings and try again.")
            print("Settings used: '%s'" % myurl)

        except:
            log.warning("Connection to Controller FAILED")
            print("Connection Failed. Suspected incorrect URL.")
            print("Settings used: '%s'" % myurl)


# Start a thread child to run server connection as a daemon
def startServer():

    log.info("Attempting to start server on "
             "Port# %d..." % (config.agntServerPort))
    startConfirmation = "y"     # Default = 'yes'
    config.agentServerUp = False

    # Check to see if any Agent Servers are already running
    log.debug("Checking server(s) already running.")
    alreadyRunning = checkServer(True)

    # If server already running, prompt user for confirmation
    # before starting an additional server
    if alreadyRunning > 0:
        log.debug("Warning: %d Agent Servers already running" % alreadyRunning)
    if alreadyRunning == 1:
        print("WARNING: 1 Agent Server Already Running!")
    elif alreadyRunning > 1:
        print("WARNING: %d Agent Servers Already Running!" % alreadyRunning)

    if alreadyRunning > 0:
        print("Confirm you want to start an ADDITIONAL Agent",
              "server.")
        startConfirmation = input("Confirm YES['y'] or NO['n']:\n>>> ")

    if startConfirmation in ["y", "Y", "YES", "yes", "Yes"]:
        # Now, start thread
        log.debug("Starting new thread...")
        t = threading.Thread(name="AgentDaemon",
                             target=myServer.runServer,
                             args=(hostIP,
                                   config.agntServerPort,
                                   CERTFILE,
                                   KEYFILE
                                   )
                             )
        t.daemon = True
        t.start()
        log.debug("Thread started... waiting for server to come up.")

        while not config.agentServerUp:
            time.sleep(1)
            log.debug("Waiting for Agent Server to Start")
            log.debug("Agent Port: %d" % config.agntServerPort)
        log.debug("New Agent server listening"
                  " on port %d." % config.agntServerPort)

        # Connect to Controller to establish connection
        log.debug("Connecting to Controller %s" % config.ctlrHostName)
        establishConnection(config.ctlrHostName, config.ctlrServerPort)

    elif startConfirmation in ["n", "N", "NO", "no", "No"]:
        print("'NO' Selected: Aborting.")
        log.debug("'%s' selected. Aborting server start" % startConfirmation)
    else:
        invalid(startConfirmation)
        print("Aborting server start")


# View current external connections
def viewConnections(admin=False):
    log.debug("Checking Status of Agent Connection(s)...")
    try:
        with dbm.open('cache_agent', 'r') as db:
            # get total records
            total = int((db.get('total')).decode("utf-8"))
            # Display Records for each
            for k in range(total):
                # Create names based on connection number
                readname = "%s.name" % (k + 1)
                readport = "%s.port" % (k + 1)
                readid = "%s.id" % (k + 1)
                readtime = "%s.time" % (k + 1)
                print("\nConnection #%d of %d:" % ((k + 1), total))
                nameAnswer = (db.get(readname)).decode("utf-8")
                portAnswer = (db.get(readport)).decode("utf-8")
                idAnswer = (db.get(readid)).decode("utf-8")
                timeAnswer = (db.get(readtime)).decode("utf-8")
                print("Name: %s" % nameAnswer)
                print("Port: %s" % portAnswer)
                if admin:
                    print("ID: %s" % idAnswer)
                print("Status updated: %s\n" % timeAnswer)
                log.debug("Read record %d Successfully" % (k + 1))
            print("END OF RECORDS")
    except:
        log.debug("ERROR READING from Cache file!!!")

    log.debug("End of View Connections Fn")


# Simple test function to ensure communication is working
def mathTest():

    log.debug("Start of Math Test Function...")
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(config.CACERTFILE)

    myurl = ''.join(['https://', config.ctlrHostName, ':',
                     str(config.ctlrServerPort)])
    with xmlrpc.client.ServerProxy(myurl,
                                   context=myContext) as proxy:
        try:
            print("3 + 7 is %d" % (proxy.add(3, 7)))
            print("11 x 9 is: %d" % (proxy.multiply(11, 9)))

        except ConnectionRefusedError:
            log.warning("Connection to Controller Server FAILED")
            print("Connection to Controller Server FAILED:\n",
                  "Is Controller listening? Confirm connection",
                  "settings and try again.")
            print("Settings used: '%s'" % myurl)

        except:
            log.warning("Connection to Controller FAILED")
            print("Connection Failed. Suspected incorrect URL.")
            print("Settings used: '%s'" % myurl)


# Send status update
def sendStatus():

    log.debug("Start of Send Status Function...")
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(config.CACERTFILE)

    print("Enter Current Status:")
    print("1) CLEAN[1]")
    print("2) Compromised[999]")
    answer = input("Make a choice\n>>> ")
    if answer == "1":
        mystatus = 1
    else:
        mystatus = 999

    if mystatus == 1:
        print("Status selected: 'CLEAN'")
    else:
        print("Status selected: 'COMPROMISED'")
    print("If this is incorrect, resubmit IMMEDIATELY!")

    myurl = ''.join(['https://', config.mntrHostName, ':',
                     str(config.mntrServerPort)])
    with xmlrpc.client.ServerProxy(myurl,
                                   context=myContext) as proxy:
        try:
            response = proxy.reportStatus(agntHostName, mystatus,
                                          agntServerPort, AGENT_ALIAS)
            log.debug("Update status response: %s" % response)
            print(response)

        except ConnectionRefusedError:
            log.warning("Connection to Controller Server FAILED")
            print("Connection to Controller Server FAILED:\n",
                  "Is Controller listening? Confirm connection",
                  "settings and try again.")
            print("Settings used: '%s'" % myurl)

        except:
            log.warning("Connection to Controller FAILED")
            print("Connection Failed. Suspected incorrect URL.")
            print("Settings used: '%s'" % myurl)


def masterQuitConnection(total, ids, names, ports, times):
    log.debug("Master Quit Connection Function")
    returnCode = 9999

    # If more than 0 connections, determine options and then close them
    if total == 0:
        log.debug("ZERO connections; no connections to close")
        print("No connections to close.")
    else:
        log.debug("Determining Options.")
        options = []
        for k in range(total):
            log.debug("%d) ID: %s; Name: %s" % ((k + 1), ids[k], names[k]))
            options.append(str(k + 1))

        # Pick Connection to close >> simply start with highest number
        t = total
        log.debug("Connection t: %d" % t)
        valuePicked = False
        t = t - 1

        while not valuePicked and t > 0:
            if ports[t] == "000000":
                t = t - 1
            else:
                # Option is valid (i.e., not port# '000000')
                valuePicked = True

        # Close Connection if valuePicked (if valid option for closing found)
        if valuePicked:
            log.debug("Value Picked: %d" % t)

            # Close connection chosen above
            myContext = ssl.create_default_context()
            myContext.load_verify_locations(config.CACERTFILE)

            myurl = ''.join(['https://', names[t], ':', ports[t]])
            with xmlrpc.client.ServerProxy(myurl,
                                           context=myContext) as proxy:

                # Send server my name and port number
                try:
                    log.info("Disconnecting from controller: "
                             "%s" % (proxy.disconnectAgent(config.agntHostName,
                                                           ids[t],
                                                           times[t])))
                    returnCode = t

                except ConnectionRefusedError:
                    log.warning("Connection to Controller Server FAILED")
                    returnCode = 9999
                    print("Connection to Controller Server FAILED:\n",
                          "Is Controller listening? Confirm connection",
                          "settings and try again.")
                    print("Settings used: '%s'" % myurl)

                except:
                    log.warning("Connection to Controller FAILED")
                    returnCode = 9999
                    print("Connection Failed. Suspected incorrect URL.")
                    print("Settings used: '%s'" % myurl)

        else:
            log.debug("All connections closed")
            returnCode = 111111
    return returnCode


# Allow user to choose which connection to close; then close
def userQuitConnection(total, ids, names, ports, times):
    log.debug("User Quit Connection Function...")
    returnCode = 9999

    # Get user choice of which connection to quit
    if total == 0:
        log.debug("ZERO connections; no connections to close")
        print("No connections to close.")
    else:
        log.debug("Getting user choice of what connection to quit.")
        print("Confirm the connection you wish to terminate.")
        options = []
        for k in range(total):
            print("%d) ID: %s; Name: %s" % ((k + 1), ids[k], names[k]))
            options.append(str(k + 1))
        s = input("Make a Choice\n>>> ")
        t = int(s) - 1
        if s not in options:
            invalid(s)
            print("Try Again. Valid options are %s." % (options))
            print("Exiting to Menu.")
        elif ports[t] == "000000":
            log.debug("PortNumber: %s" % ports[t])
            print("Connection already closed.")
            print("Exiting to Menu.")
        else:
            returnCode = t
            # Close connection chosen by user
            myContext = ssl.create_default_context()
            myContext.load_verify_locations(config.CACERTFILE)

            myurl = ''.join(['https://', names[t], ':', ports[t]])
            with xmlrpc.client.ServerProxy(myurl,
                                           context=myContext) as proxy:

                # Send server my name and port number
                try:
                    log.info("Disconnecting from controller: "
                             "%s" % (proxy.disconnectAgent(config.agntHostName,
                                                           ids[t],
                                                           times[t])))

                except ConnectionRefusedError:
                    log.warning("Connection to Controller Server FAILED")
                    returnCode = 9999
                    print("Connection to Controller Server FAILED:\n",
                          "Is Controller listening? Confirm connection",
                          "settings and try again.")
                    print("Settings used: '%s'" % myurl)

                except:
                    log.warning("Connection to Controller FAILED")
                    returnCode = 9999
                    print("Connection Failed. Suspected incorrect URL.")
                    print("Settings used: '%s'" % myurl)

    return returnCode


# Stop Agent Server
def stopServer(masterQuit=False):
    log.debug("Stopping Agent Server.")
    # TODO Determine if it is possible to stop a daemon thread
    # without stopping the whole program; for now, this just
    # disconnects from Controller and leaves daemon running

    returnCode = 1
    names = []
    ports = []
    ids = []
    times = []
    total = 0

    # Get current connection list to choose which one to close
    try:
        with dbm.open('cache_agent', 'r') as db:
            # get total records
            total = int((db.get('total')).decode("utf-8"))
            # Display Records for each
            for k in range(total):
                # Create names based on connection number
                readname = "%s.name" % (k + 1)
                readport = "%s.port" % (k + 1)
                readid = "%s.id" % (k + 1)
                readtime = "%s.time" % (k + 1)
                if not masterQuit:
                    print("\nConnection #%d of %d:" % ((k + 1), total))
                else:
                    log.debug("Connection #%d of %d:" % ((k + 1), total))

                names.append((db.get(readname)).decode("utf-8"))
                ports.append((db.get(readport)).decode("utf-8"))
                ids.append((db.get(readid)).decode("utf-8"))
                times.append((db.get(readtime)).decode("utf-8"))
                if not masterQuit:
                    print("Name: %s" % names[k])
                    print("Port: %s" % ports[k])
                    print("ID: %s" % ids[k])
                    print("Status updated: %s\n" % times[k])
                    log.debug("Read record %d Successfully" % (k + 1))
                else:
                    log.debug("Name: %s" % names[k])
                    log.debug("Port: %s" % ports[k])
                    log.debug("ID: %s" % ids[k])
                    log.debug("Status updated: %s" % times[k])
                    log.debug("Read record %d Successfully" % (k + 1))
            if not masterQuit:
                print("END OF RECORDS")
            else:
                log.debug("END OF RECORDS")
    except:
        log.debug("ERROR READING from Cache file!!!")

    t = 9999

    if total > 0:
        if masterQuit:
            t = masterQuitConnection(total, ids, names, ports, times)
        else:
            t = userQuitConnection(total, ids, names, ports, times)

    # If connection was closed (if connection number chosen was NOT
    # 9999 or 111111) then remove connection from cache
    if t not in [9999, 111111]:
        # Remove connection from cache
        delName = names[t]
        delid = ids[t]
        for k in range(total):
            if names[k] == delName:
                if ids[k] <= delid:
                    try:
                        with dbm.open('cache_agent', 'w') as db:
                            savename = "%s.name" % (k + 1)
                            saveport = "%s.port" % (k + 1)
                            saveid = "%s.id" % (k + 1)
                            savetime = "%s.time" % (k + 1)
                            db[savename] = "CONNECTION_CLOSED"
                            db[saveport] = "000000"
                            db[saveid] = "000000"
                            time = (datetime.datetime.now()).isoformat()
                            db[savetime] = str(time)
                            log.debug("Cache found. Values deleted.")
                    except:
                        log.warning("Error updating cache.")
                else:
                    log.debug("Wrong id range")
            else:
                log.debug("Wrong name")
        log.debug("End of cache update")

    elif t == 111111:
        returnCode = 111111
        log.debug("All connections already closed; rc=111111")
    else:
        returnCode = 9999
        log.debug("No connections closed; rc=9999")

    log.debug("End of Disconnect Agent Fn")
    return returnCode


# Quit gracefully after terminting all child processes
def myQuit():
    log.info("Agent Exiting. Goodbye.")

    # Disconnecting from Controller
    log.info("Disconnecting from Controller")
    rc = 0
    while rc not in [9999, 111111]:
        log.debug("Running stopServer once...")
        rc = stopServer(True)

    # Delete agent cache file
    log.debug("Deleting Agent Cache File")
    os.remove("cache_agent")
    print("Agent Exiting. Goodbye.\n")
    raise SystemExit


def invalid(choice):
    log.debug("Invalid choice: %s" % choice)
    print("INVALID CHOICE!")


def adminMenu():
    log.debug("Displaying admin menu")
    print("\nAdmin Menu:")
    print("a) Connection Test (simple math test)")
    print("b) SSL Verification (verify certificates")
    print("c) STOP/Disconnect Agent Server")
    print("d) START* Agent Server (*start/re-start/start additional)")
    print("e) Re-Register with Controller")
    print("f) View External Connections (with Admin view)")
    print("g) Send TEST Status to Monitor")
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
        establishConnection(config.ctlrHostName, config.ctlrServerPort)
    elif adminChoice == "f":
        viewConnections(True)
    elif adminChoice == "g":
        sendStatus()
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
    print("\n\nMENU[Agent]:")
    print("1) Check AGENT server status")
    print("2) View External Connections")
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
        checkServer()
    elif choice == "2":
        viewConnections()
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

    # Verify argument provided; if not provided use default,
    # if too many exit, if provided use provided
    if len(sys.argv) == 2:
        log.debug("Using controller hostname: %s" % (sys.argv[1]))
        print("Using controller hostname: '%s'" % (sys.argv[1]))
        config.ctlrHostName = sys.argv[1]

    else:
        print("usage: %s <hostname>" % sys.argv[0])
        print("Example:\n$ %s controller.shn.local" % sys.argv[0])

        # If too many arguments, exit
        if len(sys.argv) > 2:
            log.debug("Too many arguments. Exiting.")
            sys.exit(1)

        # If zero arguments, use default controller hostname
        else:
            log.debug("Using default controller hostname")
            print("No controller hostname provided.\n",
                  "Using default setting: %s" % config.ctlrHostName)

    log.info("Starting Main [Agent]")
    hostIP = getMyIP()
    verifyHostName = findHostName(hostIP)
    pid = os.getpid()
    print("Host IP: %s" % (hostIP))
    log.debug("Hostname: %s" % (verifyHostName))
    log.debug("PID: %d" % (pid))

    AGENT_ALIAS = (config.agntHostName).split('.')[0]
    log.debug("Alias: %s" % (AGENT_ALIAS))
    print("Alias: %s" % (AGENT_ALIAS))

    if verifyHostName == "None":
        log.debug("Hostname not found: Returned 'None'")

    # If hostname matches 'config.agntHostName' OR controller, then execute;
    # this is to allow Agent to run on the same localhost as the
    # controller, mainly for testing purposes
    elif verifyHostName in [config.agntHostName, "controller.shn.local"]:
        log.debug("HostName verified.")

        # Verify certificates present prior to displaying menu
        log.debug("Verifying certificates.")
        verifyCerts()

        # Start Agent's Listening Server
        log.debug("Starting agent listening server...")
        startServer()
        time.sleep(2)

        # Display Menu [repeatedly] for user
        while True:
            myMenu()
            time.sleep(1)

    else:
        log.error("Hostname incorrect. "
                  "Hostname Found: %s; Hostname "
                  "Required: %s." % (verifyHostName, config.agntHostName))
