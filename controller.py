import socket   # Required for network/socket connections
import sys      # Required for standard errors used
import os       # Required for Forking/child processes
import multiprocessing as mp    # Required for child process via multiprocessing
import xmlrpcserver_module as myServer

# Definitions
serverPort = 35353
children = []

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

def childServer():
#    while True:
        pid = os.fork()
        children.append(pid)
        print "childServer Loop PID: %d" % (pid)
        if pid == 0:
            myServer.runServer()

        else:
            print "Parent Process"
#        break

def worker():
    """worker function"""
    print "Worker"
    return

def multServer():
#    jobs = []
 #   for i in range(5):
        p = mp.Process(target=myServer.runServer)
        children.append(p)
        p.daemon = True
        p.start()

def my_quit_fn():
    raise SystemExit

def invalid():
    print "INVALID CHOICE!"

def myMenu():
    m = {"1":("Connect",runServer),
         "2":("Child Server",childServer),
         "3":("Multiprocess Server",multServer),
         "4":("Quit",my_quit_fn)
           }
    for key in sorted(m.keys()):
        print key+":" + m[key][0]
    ans = raw_input("Make a Choice\n>>> ")
    m.get(ans,[None,invalid])[1]()

##################
# Start of Program
##################
if __name__ == '__main__':
    print "Detecting IP Address and PID..."
    myIP = getMyIP()
    pid = os.getpid()
    print "Host IP: %s\nParent PID: %d\n" % (myIP,pid)

    # Create MultiProcess for Server to use
#    s = mp.Process(target=myServer.runServer())
#    s.daemon = True

    # Run Menu for user
    myMenu()
    print children
    for j in children:
        print "Alive? >> %s\n" % (j.is_alive)
        print "PID: %d\n" % (j.pid)
        print "Terminating now..."
        j.terminate()
#        j.join()


