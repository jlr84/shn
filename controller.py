import socket   # Required for network/socket connections
import os       # Required for Forking/child processes
import time     # Required for sleep call
from pathlib import Path        # Required for determine file paths
import multiprocessing as mp    # Required for child process via multiprocessing
import server_module as myServer
import certs.gencert as gencert


# Definitions
serverPort = 35353      # Declare what port the server will use
hostIP = "localhost"    # Default; updated when program is executed.
hostName = "localhost"  # Default; updated when program is executed.
children = []           # Used to track child processes
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
    CERTFILE = ''.join([certPath, hostName, ".cert"])
    KEYFILE = ''.join([certPath, hostName, ".key"])
    print("CERTFILE: %s\nKEYFILE: %s" % (CERTFILE, KEYFILE))

    # Change to file path format
    file1 = Path(CERTFILE)
    file2 = Path(KEYFILE)

    # If cert or key file not present, create new certs
    if not (file1.is_file()) or not (file2.is_file()):
        gencert.gencert(hostName)
        print("Certfile(s) NOT present; new certs created.")

    else:
        print("Certfiles Verified Present")


# Start a multiprocess child to run server connection as a daemon
def startServer():

    # Verify certificates present prior to starting server
    verifyCerts()

    # Now, start daemon server
    p = mp.Process(name="ServerDaemon",
                   target=myServer.runServer,
                   args=("localhost",
                         serverPort,
                         CERTFILE,
                         KEYFILE
                         )
                   )
    children.append(p)
    p.daemon = True
    p.start()


# Check and Display the status of all child processes
def checkStatus():
    print("\nRunning Process(es): %d" % (len(children)))
    k = 1
    for j in children:
        print("Process #%d:" % (k))
        print("Name: %s" % (j.name))
        print("PID: %d" % (j.pid))
        ans = "unknown"
        if j.is_alive():
            ans = "YES"
        else:
            ans = "NO"
        print("Alive? %s" % (ans))
        k = k+1


# Quit gracefully after terminting all child processes
def myQuit():
    # Terminate all child processes
    for j in children:
        print("Name: %s" % (j.name))
        print("PID: %d" % (j.pid))
        ans = "unknown"
        if j.is_alive():
            ans = "YES"
        else:
            ans = "NO"
        print("Alive? %s" % (ans))
        print("Terminating child...")
        j.terminate()
        print("Child terminated.\n")
    # End Program
    print("All children terminated.\nController Exiting. Goodbye.\n")
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
    hostName = findHostName(hostIP)
    pid = os.getpid()
    print("Host IP: %s\nHostname: %s\nParent PID: %d" % (hostIP, hostName, pid))

    if hostName == "None":
        print("\nHostname/FQDN not found:\n   > Hostname/FQDN Required.")
        print("   > Correct by adding record in DNS server or within local")
        print("   hosts file and then restart controller.\n")
    else:

        # Display Menu [repeatedly] for user
        while True:
            myMenu()
            time.sleep(3)
