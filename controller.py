import socket   # Required for network/socket connections
import os       # Required for Forking/child processes
import time     # Required for sleep call
import multiprocessing as mp    # Required for child process via multiprocessing
import server_module as myServer

# Definitions
serverPort = 35353      # Declare what port the server will use
hostIP = "localhost"    # Default; updated when program is executed.
children = []           # Used to track child processes
CERTFILE = "certs/domains/localhost.cert"   # Default; updated when executed
KEYFILE = "certs/domains/localhost.key"     # Default; updated when executed


def getMyIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    ipAdd = s.getsockname()[0]
    s.close()
    return ipAdd


# Start a multiprocess child to run server connection as a daemon
def startServer():
    p = mp.Process(name="ServerDaemon",
                   target=myServer.runServer,
                   args=("localhost",   # CHANGE BACK TO hostIP after testing
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
    pid = os.getpid()
    print("Host IP: %s\nParent PID: %d" % (hostIP, pid))

    # Display Menu [repeatedly] for user
    while True:
        myMenu()
        time.sleep(3)
