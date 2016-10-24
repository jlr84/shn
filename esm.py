import xmlrpc.client
import ssl
import socket     # Required for network/socket connections
import os         # Required for Forking/child processes
import sys        # Required for getting command-line arguments
import time       # Required for sleep call
import datetime
import dbm
import certs.gencert as gencert
import config
import logging
from logging.config import fileConfig

# Load logging config
fileConfig('logging.conf')
log = logging.getLogger(__name__)

# ALIAS for this Agent; change as needed
AGENT_ALIAS = "My Identifier 2"

# Global Variables -- Don't change. [No need to change.]
CERTFILE = "certs/domains/local.cert"   # Placeholder; updated when executed
KEYFILE = "certs/domains/local.key"     # Placeholder; updated when executed
hostIP = "localhost"                    # Default; updated when executed
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


# Test connection with Monitor
def testConnection(remoteName=config.mntrHostName,
                   remotePort=config.mntrServerPort):

    log.debug("Start of Test Connection Function...")
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(config.CACERTFILE)

    myurl = ''.join(['https://', remoteName, ':', str(remotePort)])
    testResult = False

    with xmlrpc.client.ServerProxy(myurl,
                                   context=myContext) as proxy:
        # Test Connection
        try:
            print("Testing connection with Monitor:")
            testResult = proxy.testConnection()

        except ConnectionRefusedError:
            log.warning("Connection to Monitor FAILED")
            log.debug("Connection settings used: %s" % (myurl))
            print("Connection to Monitor FAILED:\n",
                  "Is Monitor listening? Confirm connection",
                  "settings and try again.")
            print("Connection settings used:\n    '%s'" % (myurl))

    if testResult:
        log.info("Connection Test SUCCESSFUL!")
        print("Connection Test SUCCESSFUL!")
    else:
        log.info("Connection Test FAILED!")
        print("Connection Test FAILED!")


# Check currently-recorded status of ESM/VM
def checkStatus():
    log.debug("Checking current ESM/VM Status...")
    print("TODO: Implement this!")
    # TODO: Implement this


# Change/Update the Monitor's connection settings
def updateMonitor():
    log.debug("Updating Monitor connection settings")
    print("TODO: Implement this!")
    # TODO: Implement this


# View current monitor connection settings
def viewConnection():
    log.debug("Checking current Monitor Connection Settings...")

    print("\nMonitor Settings:")
    print("HostName: %s" % config.mntrHostName)
    print("Port: %d" % config.mntrServerPort)
    log.debug("Reading last successful transmit time...")
    try:
        with dbm.open('cache_esm', 'w') as db:
            lastUpdate = (db.get('last_update')).decode("utf-8")
            log.debug("Cache found. Value retrieved.")
    except:
        log.debug("No cache found or read failed.")
        lastUpdate = "NONE recorded!!"

    print("Last Successful Transmit: %s" % lastUpdate)

    log.debug("End of View Connection Function")


# Simple test function to ensure communication is working
def mathTest():

    log.debug("Start of Math Test Function...")
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(config.CACERTFILE)

    myurl = ''.join(['https://', config.mntrHostName, ':',
                     str(config.mntrServerPort)])
    with xmlrpc.client.ServerProxy(myurl,
                                   context=myContext) as proxy:
        try:
            print("3 + 7 is %d" % (proxy.add(3, 7)))
            print("11 x 9 is: %d" % (proxy.multiply(11, 9)))

        except ConnectionRefusedError:
            log.warning("Connection to Monitor Server FAILED")
            print("Connection to Monitor Server FAILED:\n",
                  "Is Monitor listening? Confirm connection",
                  "settings and try again.")


# Send status update
def sendStatus():

    log.debug("Start of Send Status Function...")
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(config.CACERTFILE)

    print("Enter Current Status:")
    print("1) CLEAN[1]")
    print("2) Compromised[999]")
    answer = input("Make a choice\n>>>")
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
            response = proxy.reportStatus(hostIP, mystatus,
                                          AGENT_ALIAS)
            log.debug("Response: %s" % response)
            print(response)

        except ConnectionRefusedError:
            log.warning("Connection to Monitor Server FAILED")
            print("Connection to Monitor Server FAILED:\n",
                  "Is Monitor listening? Confirm connection",
                  "settings and try again.")


def deleteHistory(no_confirmation=False):
    log.info("Delete History Function starting...")
    confirm = False
    if no_confirmation:
        confirm = True
    else:
        # Get confirmation from user
        print("Confirm you wish to DELETE ALL SAVED HISTORY:")
        answer = input("Confirm YES['y'] or NO['n']:\n>>>")

        if answer in ["y", "Y", "YES", "yes", "Yes"]:
            log.debug("Request for deletion confirmed.")
            confirm = True
        else:
            log.debug("Request for deletion cancelled.")
            log.debug("Answer selected: %s" % answer)
            confirm = False

    # Delete history, if confirmed
    if confirm:
        log.debug("Removing history now.")
        os.remove("cache_esm")
        log.info("History Deleted.")
    else:
        log.debug("History was NOT deleted.")


# Quit gracefully after terminting all child processes
def myQuit():
    log.info("ESM Exiting. Goodbye.")

    print("ESM Exiting. Goodbye.\n")
    raise SystemExit


def invalid(choice):
    log.debug("Invalid choice: %s" % choice)
    print("INVALID CHOICE!")


def adminMenu():
    log.debug("Displaying admin menu")
    print("Admin Menu:")
    print("a) Connection Test (simple math test)")
    print("b) SSL Verification (verify certificates")
    print("c) CHANGE/UPDATE Monitor Settings")
    print("d) Delete ESM History")
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
        updateMonitor()
    elif adminChoice() == "d":
        deleteHistory()
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
    print("MENU:")
    print("1) Check current ESM status")
    print("2) View Monitor Connection Settings")
    print("3) Send Status* to Monitor [user-provided status]")
    print("4) Test Connection with Monitor")
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
        viewConnection()
    elif choice == "3":
        sendStatus()
    elif choice == "4":
        testConnection()
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
        log.debug("Using monitor hostname: %s" % (sys.argv[1]))
        print("Using monitor hostname: \n%s" % (sys.argv[1]))
        config.mntrHostName = sys.argv[1]

    else:
        print("usage: %s <hostname>" % sys.argv[0])
        print("Example:\n$ %s monitor.shn.local" % sys.argv[0])

        # If too many arguments, exit
        if len(sys.argv) > 2:
            log.debug("Too many arguments. Exiting.")
            sys.exit(1)

        # If zero arguments, use default monitor hostname
        else:
            log.debug("Using default monitor hostname")
            print("No monitor hostname provided.")
            print("Using default setting: %s" % config.mntrHostName)

    log.info("Starting Main [ESM]")
    hostIP = getMyIP()
    pid = os.getpid()
    print("Host IP: %s" % (hostIP))
    log.debug("PID: %d" % (pid))
    AGENT_ALIAS = hostIP

    # Verify certificates present prior to displaying menu
    log.debug("Verifying certificates.")
    verifyCerts()

    # Display Menu [repeatedly] for user
    while True:
        myMenu()
        time.sleep(1)
