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
ctlrMysqlUser = 'controller_admin'
ctlrMysqlPwd = 'controlPassword'
ctlrdb = 'shn_controller'


# MONITOR settings
mntrServerPort = 36363
mntrHostName = "monitor.shn.local"
mntrMysqlUser = "monitor_admin"
mntrMysqlPwd = "monitorPassword"
mntrdb = "shn_monitor"


# AGENT settings
agntServerPort = 38000
agntHostName = "agent.shn.local"


# MySQL Settings
mysqlHost = 'localhost'
mysqlPort = 3306
mysqlRootUser = 'root'
mysqlRootPwd = 'J1051006'


# SYSTEM-WIDE Variables -- DO NOT CHANGE
agentServerUp = False
