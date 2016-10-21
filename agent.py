import xmlrpc.client
import ssl
import socket     # Required for network/socket connections
import os         # Required for Forking/child processes
import sys        # Required for getting command-line arguments
import time       # Required for sleep call
import threading  # Required for communication sub-threads
import server_agent as myServer
import certs.gencert as gencert
import config
import logging
from logging.config import fileConfig

# Load logging config
fileConfig('logging.conf')
log = logging.getLogger(__name__)

# ALIAS for this Agent; change as needed
AGENT_ALIAS = "My Identifier 1"

# Global Variables -- Don't change. [No need to change.]
CERTFILE = "certs/domains/local.cert"   # Placeholder; updated when executed
KEYFILE = "certs/domains/local.key"     # Placeholder; updated when executed
hostIP = "localhost"                    # Default; updated when executed


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


# Start a thread child to run server connection as a daemon
def startServer():

    log.info("Starting Server...")

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
            print("3 + 7 is %d" % (proxy.add(3, 7)))
            print("11 x 9 is: %d" % (proxy.multiply(11, 9)))

        except ConnectionRefusedError:
            log.warning("Connection to Controller Server FAILED")
            print("Connection to Controller Server FAILED:\n",
                  "Is Controller listening? Confirm connection",
                  "settings and try again.")


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


# Quit gracefully after terminting all child processes
def myQuit():
    log.info("Agent Exiting. Goodbye.")

    # Delete agent cache file
    os.remove("cache_agent")
    print("Agent Exiting. Goodbye.\n")
    raise SystemExit


def invalid(choice):
    log.debug("Invalid choice: %s" % choice)
    print("INVALID CHOICE!")


def menu():
    log.debug("Displaying menu")
    print("MENU:")
    print("1) Start AGENT Server")
    print("2) Check Status")
    print("3) Verify Certs")
    print("4) Re-establish Connection with Controller")
    print("9) Connection Test [Simple Math Test]")
    print("q) QUIT")
    return input("Make a Choice\n>>> ")


def myMenu():
    choice = 0
    choice = menu()
    if choice == "1":
        startServer()
    elif choice == "2":
        checkStatus()
    elif choice == "3":
        verifyCerts()
    elif choice == "4":
        establishConnection(config.ctlrHostName, config.ctlrServerPort)
    elif choice == "9":
        mathTest()
    elif choice in ["q", ":q"]:
        myQuit()
    else:
        invalid(choice)


# Start of Main
if __name__ == '__main__':

    # Verify argument provided; if not provided use default,
    # if too many exit, if provided use provided
    if len(sys.argv) == 2:
        log.debug("Using controller hostname: %s" % (sys.argv[1]))
        print("Using controller hostname: \n%s" % (sys.argv[1]))
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
    print("Hostname: %s" % (verifyHostName))
    log.debug("PID: %d" % (pid))

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
        while not config.agentServerUp:
            time.sleep(1)
            log.debug("Waiting for Agent Server to Start")
            log.debug("Agent Port: %d" % config.agntServerPort)
        log.debug("[Main] Agent server listening"
                  " on port %d." % config.agntServerPort)

        # Connect to Controller to establish connection
        log.debug("Connecting to Controller %s" % config.ctlrHostName)
        establishConnection(config.ctlrHostName, config.ctlrServerPort)

        # Display Menu [repeatedly] for user
        while True:
            myMenu()
            time.sleep(3)

    else:
        log.error("Hostname incorrect. "
                  "Hostname Found: %s; Hostname "
                  "Required: %s." % (verifyHostName, config.agntHostName))
