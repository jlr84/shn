#!/bin/bash
# This is an initial setup sript for my SHN project (See: https://github.com/jlr84/shn )

# SET MYSQL ROOT PASSWORD HERE (Optional; Default='rootpass')
ROOTPWD="rootpass"

echo "--SHN-- Starting Setup Script."

# Ensure necessary files are present prior to executing script
echo "--SHN-- Checking to ensure necessary files are present prior to executing..."
if [ -f ./dbsetup.sql ]; then
    echo "--SHN-- File1: 'dbsetup.sql' confirmed present where expected."
    file1=true
else
    echo "--SHN-- File1: 'dbsetup.sql' MISSING or NOT present where expected ('./dbsetup.sql')."
    file1=false
fi
if [ -f ../requirements.txt ]; then
    echo "--SHN-- File2: 'requirements.txt' confirmed present where expected."
    file2=true
else
    echo "--SHN-- File2: 'requirements.txt' MISSING or NOT present where expected ('../requirements.txt')."
    file2=false
fi
if ! $file1 -o ! $file2 ; then
    echo "--SHN-- EXITING. Correct missing file(s) and restart script."
    exit
fi

# Ensure Python version 3.5 is present
echo "--SHN-- Verifying Python 3.5 is installed..."
PYVERSION1=$(python --version 2>&1)
PYVERSION2=$(python3 --version 2>&1)
echo $PYVERSION1
echo $PYVERSION2

echo "--SHN-- Your Python version(s): '$PYVERSION1' and/or '$PYVERSION2'"
if [[ "$PYVERSION1" == "Python 3.5"* ]] || [[ "$PYVERSION2" == "Python 3.5"* ]]; then
    echo "--SHN-- Python 3.5 Verified."
else
    echo "--SHN-- WARNING: SHN Requires Python 3.5! This version NOT found. If this is an error, continue. If Python 3.5 is NOT installed on your system, install prior to using SHN."	
fi     

# Update packages
echo "--SHN-- Updating host's packages with 'apt-get update'."
sudo apt-get update

# Install pip | debconf
echo "--SHN-- Installing pip (for python3) & debconf-utils."
sudo apt-get -y install python3-pip debconf-utils

# Install packages required for https
#echo "--SHN-- Installing crypto-related packages."
#sudo apt-get -y install build-essential libssl-dev libffi-dev python-dev

# Install project requirements using pip (based on 'requirements.txt')
# Note: Assumption that 'requipments.txt' is in parent directory
echo "--SHN-- Installing project requirements using pip."
sudo -H pip3 install -r ../requirements.txt

# Install Mariadb (replacement for mysql)
echo "--SHN-- Installing MariaDB."
sudo debconf-set-selections <<< 'mariadb-server mysql-server/root_password password $ROOTPWD'
sudo debconf-set-selections <<< 'mariadb-server mysql-server/root_password_again password $ROOTPWD'
sudo apt-get -y install mariadb-server


# Perform normal "mysql_secure_installation" queries
# Save sql queries in variable 'sql'
SQL="$(cat <<-END
	UPDATE mysql.user SET Password=PASSWORD('$ROOTPWD') WHERE User='root';
	DELETE FROM mysql.user WHERE User='';
	DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
	DROP DATABASE IF EXISTS test;
	DELETE FROM mysql.db WHERE Db='test' OR Db='test_%';
	FLUSH PRIVILEGES;
END
)"

# Permform sql queries to secure MySQL
echo "--SHN-- Performing 'mysql_secure_installation' queries."
echo $SQL | sudo mysql -uroot -p$ROOTPWD


# Execute mysql initial SHN setup
echo "--SHN-- Configuring MariaDB (MySQL) for SHN; adding database, tables, users."
cat dbsetup.sql | sudo mysql -uroot -p$ROOTPWD
echo "--SHN-- MariaDB (MySQL) SHN Configuration Complete."


# This section adds default controller/monitor/agent values to /etc/hosts file
# NOTE: This assigns the local hosts' local ip address to all three; 
# !CHANGE! the ip address values below (by replacing '$ipadd' with the correct
# ip address of each or change manually (in /etc/hosts) after setup is complete.
echo "--SHN-- Adding default values for controller, monitor, and agent1 to '/etc/hosts' file."
echo "--SHN-- NOTE: Original hosts file saved as '/etc/hosts.shnbackup'."

# Get current local ip address and store in variable 'IPADD'
IPADD="$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1 -d'/')"
echo "--SHN-- Your current local ip address is '$IPADD'; using this as default for controller, monitor, and agent1 (unless already adjusted manually in this script file)."

# Backup ORIGINAL hosts file
sudo cp /etc/hosts /etc/hosts.shnbackup

# Add default values to shntemp file (along with copy of current /etc/hosts)
sudo echo "$IPADD   agent1.shn.local       agent1" | cat - /etc/hosts > shntemp && sudo mv shntemp shntemp2
sudo echo "$IPADD   monitor.shn.local      monitor" | cat - shntemp2 > shntemp && sudo mv shntemp shntemp2
sudo echo "$IPADD   controller.shn.local   controller" | cat - shntemp2 > shntemp && sudo rm shntemp2

# Change permissions / owndership of temp file to match /etc/hosts file
echo "--SHN-- New/updated [temporary] hosts file created; adjusting ownership/permission to match original hosts flie."
sudo chown --reference=/etc/hosts shntemp
sudo chmod --reference=/etc/hosts shntemp

# Move temp file to replace /etc/hosts file
echo "--SHN-- Saving new/updated hosts file to '/etc/hosts'."
sudo mv shntemp /etc/hosts

## End of Script
echo "--SHN-- Initial setup complete."
echo "--SHN-- RECOMMEND Changing mysql root password."
echo "--SHN-- (Current Password: '$ROOTPWD')"
