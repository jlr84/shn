import socket   # Required for network/socket connections
import sys      # Required for standard errors used
import os       # Required for Forking/child processes
import time     # Required for sleep call
import multiprocessing as mp    # Required for child process via multiprocessing
import xmlrpcserver_module as myServer

# Definitions
serverPort = 35353  # Declare what port the server will use
children = []       # Used to track child processes

def getMyIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",53))
    ipAdd = s.getsockname()[0]
    s.close()
    return ipAdd

def runServer():
    # Determine IP Address
    ipAddress = getMyIP()

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (ipAddress, serverPort)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()

        try:
            print >>sys.stderr, 'connection from', client_address

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print >>sys.stderr, 'received "%s"' % data
                if data:
                    print >>sys.stderr, 'sending data back to the client'
                    connection.sendall(data)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
        finally:
            # Clean up the connection
            connection.close()

# Start a multiprocess child to run server connection as a daemon
def childServer():
    p = mp.Process(name="ServerDaemon",target=myServer.runServer)
    children.append(p)
    p.daemon = True
    p.start()

def myQuit():
    print children

    # Terminate all child processes
    for j in children:
        print "Alive? >> %s" % (j.is_alive())
        print "PID: %d" % (j.pid)
        print "Terminating child now..."
        j.terminate()
        print "Child terminated.\nController Exiting. Goodbye."

    # End Program
    raise SystemExit

def checkStatus():
    print "\nRunning Process(es): %d" % (len(children))
    k=1
    for j in children:
        print "Process #%d:" % (k)
        print "Name: %s" % (j.name)
        print "PID: %d" % (j.pid)
        ans = "unknown"
        if j.is_alive():
            ans = "YES"
        else:
            ans = "NO"
        print "Alive? %s" % (ans)
        k = k+1

def invalid():
    print "INVALID CHOICE!"

def myMenu():
    m = {"1":("Start Server",childServer),
         "2":("Check Status",checkStatus),
         "q":("Quit",myQuit)
           }
    print "\nMENU:"
    for key in sorted(m.keys()):
        print key+":" + m[key][0]
    ans = raw_input("Make a Choice\n>>> ")
    m.get(ans,[None,invalid])[1]()

# Start of Main
if __name__ == '__main__':
    myIP = getMyIP()
    pid = os.getpid()
    print "Host IP: %s\nParent PID: %d" % (myIP,pid)

    # Display Menu [repeatedly] for user
    while True:
        myMenu()
        time.sleep(3)
