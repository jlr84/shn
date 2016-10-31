# SHNet (Self-healing Network) Project 
[GA Tech CS6266, Fall 2016]

The goal of this project is to produce a “self-healing” network (SHNet) that provides the capability to automatically respond to and remediate security vulnerabilities detected among end-host systems within the network.

SHNet operation is supported by the use of a hypervisor and virtualized user desktop (VUD) for each [user, non-server] end-host within the network. This structure allows each end-user to operate a virtualized desktop, while SHNet-related communication remains at the hypervisor level, one layer below the end-user. 

This project consists of four main components: A **Monitor** node receives regular updates from each VUD operated on the network via an **End-host Security Monitor (ESM)** running on each VUD. The ESM identifies the associated health/security status of the VUD as either 'CLEAN' or 'COMPROMISED' and transmits this status to the Monitor node. (Note: In this project the ESM is simply simulating the detection of a compromised end-host, whereas a full-fledged commercial product would be used in a real-world setting.) A **Controller** node reads the network health/security status maintained by the Monitor and takes action as necessary to mitigate any concerns. The Controller takes necessary action by communicating with an **SHNet Agent** running at the hypervisor level of each end-host. By communicating with the Agent, the Controller takes action to restore, snapshot, or otherwise roll-back each VUD to a time-period prior to suspected compromise.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine -- with some limitations, mentioned below -- for development and testing purposes. See deployment section for notes on how to deploy the project for full functionality.

### Prerequisites

Unless stated specifically elsewhere (for individual components) this project requires:  
(1) Ubuntu 16.04 LTS

Download and install from the Ubuntu website:  
http://releases.ubuntu.com/16.04.1/ubuntu-16.04.1-desktop-amd64.iso


(2) Python 3.5

Download and install from the Python website:    
https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tar.xz   
(See 'Additional References' for more detail.)


(3) Xen Project Hypervisor 
Reference the Xen Project website and the Ubuntu Xen community page:   
https://www.xenproject.org/   
https://help.ubuntu.com/community/Xen   
(See 'Additional References' for more detail.)


### Installing

These instructions will get you a copy of the project up and running on your local machine -- with some limitations, mentioned below -- for development and testing purposes. Continue with the deployment section folling these steps for notes on how to reconfigure the project for full functionality.

**Step 1: Install Ubuntu 16.04 LTS**   
(See 'Installing Ubuntu 16.04 LTS,' below, for more detail.)

**Step 2: Install Git**
```
$ sudo apt-get install git
```

**Step 3: Clone the SHNet Repository**
```
$ git clone https://github.com/jlr84/shn.git
```

**Step 4: Complete the following to finish the basic install.**  
Note, the two configuration files are:
* shn/config.py
* shn/setup/dbsetup.sql

If you make any changes to the default settings, ensure your changes match in both files, as required.  

Change Directory to the setup folder, and execute 'run_setup.sh' to begin setup.

```
$ cd shn/setup;

$ ./run_setup.sh
```

Initial Setup is complete, which included:
* Install of necessary supporting packages
* Install of all packages included in requirements.txt
* Install of MariaDB
* Configuration of MariaDB: Database, Tables, and users required for SHN were added/created/updated.
* Configuration of '/etc/hosts' file for default SHN setup

Recommendation: Change mysql root password, as this is not needed after this point of the SHNet installation. (Non-root mysql users with limited privileges were created in the install script for use by SHNet.) The last two output lines from the 'run_setup.sh' script display the current root password so you can change it as desired.

**Step 5: Verify Install**  
This is a step-by step example that will verify everything is operating as expected:  

OPEN four (4) different terminals (change directory to the 'shn/' folder in each terminal).

**TERMINAL 1**  
Start the CONTROLLER.
```
$ python3 controller.py

Host IP: 1##.##.##.112
Hostname: controller.shn.local
Certfiles Verified Present.
Server listening on port 35353.


MENU[Controller]:
1) Check CONTROLLER server status
2) Display Connected Agents
3) Send Command to Agent
9) ADMIN MENU
q) QUIT
Make a Choice
>>> 
```

**TERMINAL 2**  
Start the MONITOR.
```
$ python3 monitor.py 
Host IP: 1##.##.##.112
Hostname: controller.shn.local
Certfiles Verified Present.
Server listening on port 36363.


MENU[Monitor]:
1) Check MONITOR server status
2) Display Current Status
9) ADMIN MENU
q) QUIT
Make a Choice
>>> 
```

**TERMINAL 3**  
Start the AGENT. 
```
$ python3 agent.py controller.shn.local
Using controller hostname: 'controller.shn.local'
Host IP: 1##.##.##.112
Alias: agent1
Certfiles Verified Present
Server listening on port 38000...
Register with controller: Registering Agent 'agent1.shn.local'...
Registration Acknowledged (ID#1)
1##.##.##.112 - - [31/Oct/2016 13:20:30] "POST /RPC2 HTTP/1.1" 200 -


MENU[Agent]:
1) Check AGENT server status
2) View External Connections
9) ADMIN MENU
q) QUIT
Make a Choice
>>> 
```
When the Agent starts, it will connect to the CONTROLLER and establish/register a connection from the Controller to the Agent. After the Agent is started in Terminal 3, you will see the following in Terminal 1 if the connection is successful:
```
1##.##.##.112 - - [31/Oct/2016 13:26:26] "POST /RPC2 HTTP/1.1" 200 -
ControlAgent Daemon Started
Connection to Agent ESTABLISHED
```

**TERMINAL 4**  
Start the ESM.
```
$ python3 esm.py 
Using default monitor hostname: monitor.shn.local
Using default monitor port#: 36363
Using alias: agent1
Host IP: 172.31.31.112
Certfiles Verified Present


MENU[ESM]:
1) Check current ESM status
2) View Monitor Connection Settings
3) Send 'CLEAN' Status to Monitor
4) Send 'COMPROMISED' Status to Monitor
5) Start BASIC Simulation [in background]
6) Test Connection with Monitor
9) ADMIN MENU
q) QUIT
Make a Choice
>>> 
```

Select Choice '3' to report 'CLEAN' status to the monitor; then select Choice '1' to view the 
```
>>> 3
Status '1' Sent to Monitor; Confirmed at 2016-10-31 14:08:52.108358.
```
```
>>> 1
ESM/VM Status:
CLEAN ['1'] (as of 2016-10-31 14:08:52.108358)
```
After selecting Choice '3', the ESM will send the current status to the Monitor. The Controller will read this updated status from the list maintained by the Monitor. As such, in Terminal 1 you will see the following at this point:
```
Host NOT FOUND in status database!! 	# This will display PRIOR TO the ESM sending its first status
Host 'agent1.shn.local' CLEAN as of '2016-10-31 14:02:34'.	# This will display after the status is sent.
```

If all of the above worked successfully, the SHNet local install is confirmed successful at this point.  

Running SHNet in this configuration will work for development and (basic) testing; however, full functionality is not present.  

These are the main limitations of this, limited, install:  
* The Agent Module is NOT running within a Xen-based hypervisor. This results in any functionality related to actually controlling VUD's (VMs) **being non-functional**. 
* The ESM Module is NOT running inside a VUD, as designed and described above. Correct implementation would include the ESM automatically running upon the start of each VUD. 


## Running the tests

TODO: Explain how to run the automated tests for this system

### Break down into end to end tests

TODO: Explain what these tests test and why

```
Give an example
```

### And coding style tests

TODO: Explain what these tests test and why

```
Give an example
```

## Deployment

TODO: Add more notes here

## Built With

* [Xen Project](https://www.xenproject.org/) - Hypervisor
* [Ubuntu 16.04 LTS](https://wiki.ubuntu.com/XenialXerus/ReleaseNotes) - Operating System
* [Python 3.5](https://docs.python.org/3/) - Primary Programming Language

## Contributing

This is an individual project, so contributions are not expected. Contact me directly at 'jroberts302' --at-- 'gatech.edu' for questions. 

## Authors

* **J. Roberts** - [jlr84](https://github.com/jlr84)

## License

This project is licensed under the MIT License - see the [LICENSE.md](License.md) file for details


## Additional References

### Installing Ubuntu 16.04 LTS

(1) Option 1: Install on your host machine.

(2) Option 2: Install as a virtual machine inside a Type-2 Hypervisor (such as VirtualBox).

(3) I used 'Option 2', with the following information provided as additional detail: 
* My host computer is a Windows 10 64-bit, with an 8-core, 2.80GHz processor, and 32GB RAM
* I used [VirtualBox](https://www.virtualbox.org/wiki/Downloads) as my hypervisor. (See their website for install instructions.)
* I downloaded the above-referenced [Ubuntu 16.04 LTS iso](http://releases.ubuntu.com/16.04.1/ubuntu-16.04.1-desktop-amd64.iso) and installed this fresh inside VirtualBox using the following configuration: 16GB RAM, 1 CPU, and 1 Network Adapter installed (set as a 'Bridged Adapter'). All other selections used the 'default' options.
* Start the VM; install the OS. 
* After install, perform an update to ensure all the latest updates are applied. 

```
sudo apt-get update 	# Fetches the list of availble updates
sudo apt-get upgrade	# Upgrades the current packages
```

### Installing Python 3.5

Download from the Python website 
```
wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tar.xz
```

Untar and Install
```
tar xf Python-3.5.2.tar.xz
cd Python-3.5.2/
./configure
make
make test
sudo make install
```

Optionally, you may want to consider installing in parralel with your current version of Python; if so, reference the instructions found here:
```
http://askubuntu.com/questions/680824/how-do-i-update-python-from-3-4-3-to-3-5
```

### Xen Project Hypervisor Install

(1) Start install of Ubuntu 16.04 (on a physical computer)
* Burn the above-referenced .iso to DVD; 
* Insert into DVD drive; 
* Restart computer and follow directions to start the installation.

(2) DURING install, for the partitioning method choose "Guided - use the entire disk and setup LVM."

(3) When prompted to enter "Amount of volume group to use for guided partitioning," enter a value just large enough for the Xen Dom0 system, leaving the rest for the virtual disks. (Recommend: 10-20GB for the Xen Dom0 system.)

(4) Complete the rest of the Hypervisor Install

(5) Install Xen (Once logged into the Ubuntu-Xen system, do the following:)
Install a 64-bit hypervisor (this works with a 32-bit dom0 kernal also, but allows you to run 64-bit guests as well.
```
$ sudo apt-get install xen-hypervisor-amd64
```

Reboot.
```
$ sudo reboot
```

Verify the installation has succeeded:
```
$ sudo xl list
Name                                        ID   Mem VCPUs      State   Time(s)
Domain-0                                     0   945     1     r-----      11.3
```

(6) Setup Network Configuration
Disable the Network Manager
```
$ sudo stop network-manager
$ echo "manual" | sudo tee /etc/init/network-manager.override
```

Install Bridge-Utils
```
sudo apt-get install bridge-utils
```

Configure your network interfaces (this is what I used successfully:)
```
$ sudo vi /etc/network/interfaces
!!!
TODO: Insert my configuration here
!!!
```

Restart networking to enable xenbr0 bridge
```
$ sudo ifdown eth0 && sudo ifup xenbr0 && sudo ifup eth0
```

(7) Configuration complete. See other portions of documentation for setup of VMs/VUDs.
