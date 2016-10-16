import xmlrpc.client
import ssl

CACERTFILE = "certs/ca.cert"

myContext = ssl.create_default_context()
myContext.load_verify_locations(CACERTFILE)

with xmlrpc.client.ServerProxy("https://controller.shn.local:35353/", context=myContext) as proxy:
    print("3 + 7 is: %d" % (proxy.add(3,7)))
    print("11 x 9 is: %d" % (proxy.multiply(11,9)))
