'''
    System-wide global configurations for shn
    NOTE: ENSURE ANY Changes made here ALSO
    match the configurations in the mysql
    database setup file located here:
        ./setup/dbsetup.sql
'''

# Global Settings [same across all modules]:
rootDomain = "shn.local"
certPath = "certs/domains/"
CACERTFILE = "certs/ca.cert"


# CONTROLLER settings
ctlrServerPort = 35353
ctlrHostName = "controller.shn.local"
ctlrMysqlUser = 'controller_admin'
ctlrMysqlPwd = 'controlPassword'


# MONITOR settings
mntrServerPort = 36363
mntrHostName = "monitor.shn.local"
mntrMysqlUser = "monitor_admin"
mntrMysqlPwd = "monitorPassword"


# AGENT settings
agntServerPort = 38000
agntHostName = "agent1.shn.local"


# MySQL Settings
mysqlHost = 'localhost'
mysqlPort = 3306
mysqlDB = "shn_database"
mysqlRootUser = 'root'
mysqlRootPwd = 'J1051006'


# SYSTEM-WIDE Variables -- DO NOT CHANGE
agentServerUp = False
