import xmlrpc.client
import ssl
import socket     # Required for network/socket connections
import os         # Required for Forking/child processes
import time       # Required for sleep call
import threading  # Required for communication sub-threads
import server_agent as myServer
import certs.gencert as gencert


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
    CERTFILE = ''.join([certPath, rootDomain, ".cert"])
    KEYFILE = ''.join([certPath, rootDomain, ".key"])
    print("CERTFILE: %s\nKEYFILE: %s" % (CERTFILE, KEYFILE))

    # If cert or key file not present, create new certs
    if not os.path.isfile(CERTFILE) or not os.path.isfile(KEYFILE):
        gencert.gencert(rootDomain)
        print("Certfile(s) NOT present; new certs created.")
        print("Note: You may need to quit & restart Agent.")

    else:
        print("Certfiles Verified Present")


# Start a thread child to run server connection as a daemon
def startServer():

    # Verify certificates present prior to starting server
    verifyCerts()

    # Now, start thread
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


# Simple test function to ensure communication is working
def mathTest():
    myContext = ssl.create_default_context()
    myContext.load_verify_locations(CACERTFILE)

    with xmlrpc.client.ServerProxy("https://controller.shn.local:35353/",
                                   context=myContext) as proxy:
        print("3 + 7 is %d" % (proxy.add(3, 7)))
        print("11 x 9 is: %d" % (proxy.multiply(11, 9)))


# Quit gracefully after terminting all child processes
def myQuit():
    print("Agent Exiting. Goodbye.\n")
    raise SystemExit


def invalid():
    print("INVALID CHOICE!")


def menu():
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
        invalid()


# Start of Main
if __name__ == '__main__':
    print("Starting AGENT")
    hostIP = getMyIP()
    verifyHostName = findHostName(hostIP)
    pid = os.getpid()
    print("Host IP: %s\nHostname: %s" % (hostIP, verifyHostName))
    print("Parent PID: %d" % (pid))

    if verifyHostName == "None":
        print("\nHostname/FQDN not found:\n   > Hostname/FQDN Required.")
        print("   > Correct by adding record in DNS server or within local")
        print("   hosts file (/etc/hosts) and then restart controller.\n")

    elif verifyHostName in [hostName, "controller.shn.local"]:
        # Display Menu [repeatedly] for user
        while True:
            myMenu()
            time.sleep(3)

    else:
        print("\nHostname incorrect:")
        print("   > Hostname Found: %s" % (verifyHostName))
        print("   > Hostname Required: %s" % (hostName))
