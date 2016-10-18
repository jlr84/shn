import xmlrpc.client
import ssl
import socket     # Required for network/socket connections
import os         # Required for Forking/child processes
import time       # Required for sleep call
import threading  # Required for communication sub-threads
import server_agent as myServer
import certs.gencert as gencert
import logging
from logging.config import fileConfig

# Load logging config
fileConfig('logging.conf')
log = logging.getLogger(__name__)

# Adjustable Settings:
serverPort = 27878                  # Declare what port the server will use
hostName = "agent.shn.local"        # Default; VERIFIED when executed.
rootDomain = "shn.local"            # Default
certName = "shn.local"              # Default

# Declarations: Do not change
certPath = "certs/domains/"                 # Path for ip-based ssl cert files
CACERTFILE = "certs/ca.cert"                # Location of CA Cert
CERTFILE = "certs/domains/localhost.cert"   # Default; updated when executed
KEYFILE = "certs/domains/localhost.key"     # Default; updated when executed
hostIP = "localhost"                # Default; updated when program is executed.


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
    CERTFILE = ''.join([certPath, rootDomain, ".cert"])
    KEYFILE = ''.join([certPath, rootDomain, ".key"])
    log.debug("CERTFILE: %s" % CERTFILE)
    log.debug("KEYFILE: %s" % KEYFILE)

    # If cert or key file not present, create new certs
    if not os.path.isfile(CERTFILE) or not os.path.isfile(KEYFILE):
        gencert.gencert(rootDomain)
        log.info("Certfile(s) NOT present; new certs created.")
        print("Certfile(s) NOT present; new certs created.")
        print("Note: You may need to quit & restart Agent.")

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
                               serverPort,
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


# Simple test function to ensure communication is working
def mathTest():

    log.debug("Start of Math Test Function...")
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(CACERTFILE)

    with xmlrpc.client.ServerProxy("https://controller.shn.local:35353/",
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
    print("4) Math Test")
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
        mathTest()
    elif choice == "q":
        myQuit()
    else:
        invalid(choice)


# Start of Main
if __name__ == '__main__':
    log.info("Starting Main [Agent]")
    hostIP = getMyIP()
    verifyHostName = findHostName(hostIP)
    pid = os.getpid()
    print("Host IP: %s" % (hostIP))
    print("Hostname: %s" % (verifyHostName))
    log.debug("PID: %d" % (pid))

    if verifyHostName == "None":
        log.debug("Hostname not found: Returned 'None'")

    elif verifyHostName in [hostName, "controller.shn.local"]:
        log.debug("HostName verified.")

        # Verify certificates present prior to displaying menu
        log.debug("Verifying certificates.")
        verifyCerts()

        # Display Menu [repeatedly] for user
        while True:
            myMenu()
            time.sleep(3)

    else:
        log.error("Hostname incorrect. "
                  "Hostname Found: %s; "
                  "Hostname Required: %s." % (verifyHostName, hostName))
