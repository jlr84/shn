import socket
import sys

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
    server_address = (ipAddress, 10000)
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

def my_quit_fn():
    raise SystemExit

def invalid():
    print "INVALID CHOICE!"

def myMenu():
    m = {"1":("Connect",runServer),
         "2":("Quit",my_quit_fn)
           }
    for key in sorted(m.keys()):
        print key+":" + m[key][0]
    ans = raw_input("Make a Choice\n>>> ")
    m.get(ans,[None,invalid])[1]()

##################
# Start of Program
##################

print "Detecting IP Address..."
myIP = getMyIP()
print "Host IP: %s\n" % (myIP)

# Run Menu for user
myMenu()

