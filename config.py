'''
    System-wide global configurations for shn

'''

# Global Settings [same across all modules]:
rootDomain = "shn.local"
certPath = "certs/domains/"
CACERTFILE = "certs/ca.cert"


# CONTROLLER settings
ctlrServerPort = 35353                  # Declare what port the server will use
ctlrHostName = "controller.shn.local"   # Default; VERIFIED when executed.


# MONITOR settings
mntrServerPort = 36363
mntrHostName = "monitor.shn.local"


# AGENT settings
agntServerPort = 38000
agntHostName = "agent.shn.local"


# SYSTEM-WIDE Variables -- DO NOT CHANGE
agentServerUp = False
