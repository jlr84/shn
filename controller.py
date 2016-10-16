import socket     # Required for network/socket connections
import os         # Required for Forking/child processes
import time       # Required for sleep call
import threading  # Required for communication sub-threads
from pathlib import Path        # Required for determine file paths
import server_module as myServer
import certs.gencert as gencert


# Adjustable Settings:
serverPort = 35353                  # Declare what port the server will use
hostName = "controller.shn.local"   # Default; VERIFIED when executed.
rootDomain = "shn.local"            # Default
certName = "shn.local"              # Default

# Declarations: Do not change
hostIP = "localhost"                # Default; updated when program is executed.
certPath = "certs/domains/"                 # Path for ip-based ssl cert files
CERTFILE = "certs/domains/localhost.cert"   # Default; updated when executed
KEYFILE = "certs/domains/localhost.key"     # Default; updated when executed


# Return ip address of local host where server is running
def getMyIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    ipAdd = s.getsockname()[0]
    s.close()
    return ipAdd


# Return host name/fqdn of based on give ip address
def findHostName(ipAddress):
    try:
        name, alias, addresslist = socket.gethostbyaddr(ipAddress)
        return name
    except socket.herror:
        return "None"


# Create SSL certs for current ip address if not already present
def verifyCerts():
    global CERTFILE
    global KEYFILE

    # Determine file path based on current ip address
    print("CERTFILE: %s\nKEYFILE: %s" % (CERTFILE, KEYFILE))
    CERTFILE = ''.join([certPath, rootDomain, ".cert"])
    KEYFILE = ''.join([certPath, rootDomain, ".key"])
    print("CERTFILE: %s\nKEYFILE: %s" % (CERTFILE, KEYFILE))

    # Change to file path format
    file1 = Path(CERTFILE)
    file2 = Path(KEYFILE)

    # If cert or key file not present, create new certs
    if not (file1.is_file()) or not (file2.is_file()):
        gencert.gencert(rootDomain)
        print("Certfile(s) NOT present; new certs created.")

    else:
        print("Certfiles Verified Present")


# Start a thread child to run server connection as a daemon
def startServer():

    # Verify certificates present prior to starting server
    verifyCerts()

    # Now, start thread
    t = threading.Thread(name="ServerDaemon",
                         target=myServer.runServer,
                         args=(hostIP,
                               serverPort,
                               CERTFILE,
                               KEYFILE
                               )
                         )
    t.daemon = True
    t.start()


# Check and Display the status of all child processes
def checkStatus():
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


# Main Logic for Controller communicating to Agent(s)
def controlAgent(hostName, portNum):

    # Connect to Agent's server daemon

    # Run check on system status

    # Send Command to Agent

    while True:
        print("ControlAgent: Sleeping 30...")
        time.sleep(30)


# Quit gracefully after terminting all child processes
def myQuit():
    print("Controller Exiting. Goodbye.\n")
    raise SystemExit


def invalid():
    print("INVALID CHOICE!")


def myMenu():
    m = {"1": ("Start Server", startServer),
         "2": ("Check Status", checkStatus),
         "3": ("Verify Certs", verifyCerts),
         "q": ("Quit", myQuit)
         }
    print("\nMENU:")
    for key in sorted(m.keys()):
        print(key+":" + m[key][0])
    ans = input("Make a Choice\n>>> ")
    m.get(ans, [None, invalid])[1]()


# Start of Main
if __name__ == '__main__':
    hostIP = getMyIP()
    verifyHostName = findHostName(hostIP)
    pid = os.getpid()
    print("Host IP: %s\nHostname: %s" % (hostIP, verifyHostName))
    print("Parent PID: %d" % (pid))

    if verifyHostName == "None":
        print("\nHostname/FQDN not found:\n   > Hostname/FQDN Required.")
        print("   > Correct by adding record in DNS server or within local")
        print("   hosts file and then restart controller.\n")

    elif verifyHostName == hostName:
        # Display Menu [repeatedly] for user
        while True:
            myMenu()
            time.sleep(3)

    else:
        print("\nHostname incorrect:")
        print("   > Hostname Found: %s" % (verifyHostName))
        print("   > Hostname Required: %s" % (hostName))
