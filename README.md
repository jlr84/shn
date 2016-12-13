# SHNet (Self-healing Network) Project 
[GA Tech CS6266, Fall 2016]

The goal of this project is to produce a “self-healing” network (SHNet) that provides the capability to automatically respond to and remediate security vulnerabilities detected among end-host systems within the network.

SHNet operation is supported by the use of a hypervisor and virtualized user desktop (VUD) for each [user, non-server] end-host within the network. This structure allows each end-user to operate a virtualized desktop, while SHNet-related communication remains at the hypervisor level, one layer below the end-user. 

This project consists of four main components: A **Monitor** node receives regular updates from each VUD operated on the network via an **End-host Security Monitor (ESM)** running on each VUD. The ESM identifies the associated health/security status of the VUD as either 'CLEAN' or 'COMPROMISED' and transmits this status to the Monitor node. (Note: In this project the ESM is simply simulating the detection of a compromised end-host, whereas a full-fledged commercial product would be used in a real-world setting.) A **Controller** node reads the network health/security status maintained by the Monitor and takes action as necessary to mitigate any concerns. The Controller takes necessary action by communicating with an **SHNet Agent** running at the hypervisor level of each end-host. By communicating with the Agent, the Controller takes action to restore, snapshot, or otherwise roll back each VUD to a time period prior to suspected compromise.

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
(See 'Installing Ubuntu 16.04 LTS,' below under 'Additional References', for more detail.)

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

The above step completes initial setup, which includes:
* Install of necessary supporting packages
* Install of all packages included in requirements.txt
* Install of MariaDB
* Configuration of MariaDB: Database, Tables, and users required for SHN were added/created/updated.
* Configuration of '/etc/hosts' file for default SHN setup

Recommendation: Change mysql root password, as this is not needed after this point of the SHNet installation. (Non-root mysql users with limited privileges were created in the install script for use by SHNet.) The last two output lines from the 'run_setup.sh' script display the current root password so you can change it as desired.

**Step 5: Verify Install**  
This is a step-by step example that will verify everything is operating as expected:  

**OPEN four (4) different terminals (change directory to the 'shn/' folder in each terminal).**

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
$ python3 agent.py NONE --NO_VUD
NO_VUD Mode selected: Agent running without full functionality. (No access to VUD.)
Using default controller hostname: controller.shn.local
Using default controller port#: 35353
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
Host IP: 1##.##.##.112
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

Select Choice '3' to report 'CLEAN' status to the monitor; then select Choice '1' to view the current status.
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

These are the main limitations of this limited install:  
* The Agent Module is NOT running within a Xen-based hypervisor. This results in any functionality related to actually controlling VUD's (VMs) **being non-functional**. 
* The ESM Module is NOT running inside a VUD, as designed and described above. Correct implementation would include the ESM automatically running upon the start of each VUD. 


## Deployment

To set up SHNet for full functionality, start with the above basic setup. Perform the basic setup on the host you intend to run the Monitor and Controller modules. With that complete, do the following: 

### Agent Setup

**Step 1: Install Ubuntu with Xen**  
On a second host, follow the directions listed below under *Additional References: Xen Project Hypervisor Install* to set up an Ubuntu Xen Machine.

**Step 2: Create Base VM (VUD) Image**  
(Reference the *Manually Create a PV Guest VM* section of https://help.ubuntu.com/community/Xen for more detail.)

List your existing volume groups (VG) and choose where you'd like to create the new logical volume. 
```
$ sudo vgs
  VG  #PV #LV #SN Attr   VSize   VFree
  xen   1   1   1 wz--n- 276.23g 164.84g
```

In this example, the VG is named "xen"; this is used within the following *lvcreate* commmand.  
Now, create the logical volume (LV) you will use as the drive for the VM. We will create a LV named *vud1* with a size of 10 GB for demonstration & testing purposes.
```
$ sudo lvcreate -L 10G -n vud1 /dev/xen
  Logical volume "vud1" created.
```

Confirm the new LV was successfully created.
```
$ sudo lvs
  LV    VG  Attr        LSize ...
  vud1  xen -wi-a-----  10.00g
```

Download a netboot ubuntu image. (We'll use a mirror from RIT.edu.)
```
$ sudo mkdir -p /var/lib/xen/images/ubuntu-netboot/trusty14LTS
$ cd /var/lib/xen/images/ubuntu-netboot/trusty14LTS
$ wget http://mirrors.rit.edu/ubuntu/ubuntu/dists/trusty/main/installer-amd64/current/images/netboot/xen/vmlinuz
$ wget http://mirrors.rit.edu/ubuntu/ubuntu/dists/trusty/main/installer-amd64/current/images/netboot/xen/initrd.gz
```

Set up initial guest configuration:
```
$ cd /etc/xen
$ cp xlexample.pvlinux vud1.cfg
$ vi vud1.cfg
```

Change the file to match the following, save, and close the file:
```
name = "vud1"

kernel = "/var/lib/xen/images/ubuntu-netboot/trusty14LTS/vmlinuz"
ramdisk = "/var/lib/xen/images/ubuntu-netboot/trusty14LTS/initrd.gz"
#bootloader = "pygrub"

memory = 1024
vcpus = 1

vif = [ 'bridge=xenbr0' ]

disk = [ '/dev/xen/vud1,raw,xvda,rw' ]

vfb = [ 'type=vnc,vncdisplay=77' ]
```

Boot the VM for the first time with the following command. Follow the typical setup for a normal operating system install once connected to the VM via the terminal console. (The -c flag automatically connects to the console upon VM start.) Note: *CTRL* + *]* will disconnect you from the console; *sudo xl console vud1* will reconnect you to the VM console, if required. 
```
$ sudo xl create -c /etc/xen/vud1.cfg
```

Once install is complete, shut down the VM. First disconnect from the console, then shut down the VM.
```
[Press CTRL + ] to disconnect from console]
$ sudo xl shutdown vud1
Shutting down domain 1
```

Now that the VM operating system is installed, change the guest configuration file to look like the following. (Note: You are simply changing the VM to boot using pygrub instead of from the download netboot disks.)
```
name = "vud1"

#kernel = "/var/lib/xen/images/ubuntu-netboot/trusty14LTS/vmlinuz"
#ramdisk = "/var/lib/xen/images/ubuntu-netboot/trusty14LTS/initrd.gz"
bootloader = "pygrub"

memory = 1024
vcpus = 1

vif = [ 'bridge=xenbr0' ]

disk = [ '/dev/xen/vud1,raw,xvda,rw' ]

vfb = [ 'type=vnc,vncdisplay=77' ]
```

Boot the VM one more time to ensure it starts successfully from the hard disk:
```
$ sudo xl create -c /etc/xen/vud1.cfg
```

At this point, the base VM image is complete. 


**Step 3: Install and Configure Agent Module**  
At the hypervisor level, follow these instructions to setup the Agent module:

Install Git 
```
$ sudo apt-get install git
```

Clone the SHNet Repository
```
$ git clone https://github.com/jlr84/shn.git
```

Change directory to the *esm_auto* folder; view the *run_setup.sh* file and edit to specify the correct IP Address for the Monitor and Controller (unless using a local dns server for your network). 
```
cd /shn/esm_auto/
vi run_setup.sh
...
MONITOR_IP=1##.##.##.###         # CHANGE this line to match the IP Address for your Monitor host
CONTROLLER_IP=1##.##.##.###      # CHANGE this line to match the IP Address for your Controller host
...
```

After saving the file, run the setup script (within the *esm_auto* folder) to finalize the setup:
```
$ ./run_setup.sh
```

### ESM Setup   
Starting from the hypervisor level, follow these instructions to set up the ESM module:

Start the VM/VUD that was initially created above (or connect to the terminal/console if it is already running):
```
$ sudo xl create -c /etc/xen/vud1.cfg
```
OR
```
$ sudo xl console vud1
```

Login to the VUD using the same credentials you created during the VM/VUD OS installation. 
After logging into the VUD, do the following inside the VUD:

Install Git 
```
$ sudo apt-get install git
```

Clone the SHNet Repository
```
$ git clone https://github.com/jlr84/shn.git
```

Change directory to the *esm_auto* folder; view the *run_setup.sh* file and edit to specify the correct IP Address for the Monitor and Controller (unless using a local dns server for your network). 
```
cd /shn/esm_auto/
vi run_setup.sh
...
MONITOR_IP=1##.##.##.###         # CHANGE this line to match the IP Address for your Monitor host
CONTROLLER_IP=1##.##.##.###      # CHANGE this line to match the IP Address for your Controller host
...
```

After saving the file, run the setup script (within the *esm_auto* folder).
```
$ ./run_setup.sh
```

View the *auto_esm.conf* file and change the folder path on line 4 to match the path to the *esm.py* file found in the *shn* folder.
```
$ vi auto_esm.conf
start on runlevel [12345]
stop on runlevel [!12345]

exec python3.5 /home/shnuser/coding/shn/esm.py -S -B -t 15
```

Copy the *auto_esm.conf* file from this folder into */etc/systemd/*. 
By placing this conf file here, you hook into Ubuntu's upstart service that runs services on startup. Manual starting/stopping is done with ```sudo service auto_esm start``` and ```sudo service auto_esm stop```
```
$ cp auto_esm.conf /etc/systemd/
```

Return to the *shn* directory, and view the *config.py* file; change the paths located on lines 11 and 12 from the relative paths, to the absolute paths, for your specific VM/OS/VUD configuration.
```
$ cd ../
$ vi config.py ./config.py
...
certPath = "/home/shnuser/coding/shn/certs/domains/"
CACERTFILE = "/home/shnuser/coding/shn/certs/ca.cert"
...
```

View the *esm.py* file; change the path located on line 18 from the relative path, to the absolute path, for your specific VM/OS/VUD configuration.
```
$ cd ../
$ vi esm.py ./esm.py
...
fileConfig('/home/shnuser/coding/shn/setup/logging.conf')
...
```

At this point, the VUD/VM is configured to run the ESM Module in basic simulation mode every time the system boots/starts. (Change the flags used within the *auto_esm.conf* file to adjust the specific configuration of the simulation mode utilized within the ESM module.)

### Post-Install   
At this point, you've configured the Agent and ESM modules for operation. 
Start the three modules (Controller, Monitor, Agent) in a similar manner as shown in the basic setup; the only difference is the start command used for the Agent. Use the following Agent start command:
```
$ sudo python3 agent.py vud1
```

NOTE, there are presently no backups of your VUD on initial startup. Recommend you send a command from the Controller to the Agent to create a backup (or multiple, if desired). The SHNet system will be unable to revert to a non-compromised/non-infected state if there are no backups present within the system that it can use for restoring the system state. 
EXAMPLE:
```
MENU[Controller]:
1) Check CONTROLLER server status
2) Display Connected Agents
3) Send Command to Agent
9) ADMIN MENU
q) QUIT
Make a Choice
>>> 3

Send a command to which Agent?
1) Host: test.shn.local; Alias: testAlias; ID: 13
2) Host: agent1.shn.local; Alias: agent1; ID: 15
Select a number:
>>> 2

Available Options: 
0) Check VUD Status
1) Start VUD
2) Shutdown VUD
3) Pause VUD
4) UN-Pause VUD
5) Take Snapshot of VUD
6) Restore from Snapshot
7) Backup [Clone] VUD (WARNING: Time-intensive)
8) Restore from Backup
Select a number:
>>> 7
You selected Command#7
'Complete CLone' Command Executing...
...
```


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

Optionally, you may want to consider installing in parallel with your current version of Python; if so, reference the instructions found here:
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

(6) Set up Network Configuration
Disable the Network Manager
```
$ sudo stop network-manager
$ echo "manual" | sudo tee /etc/init/network-manager.override
```

Install Bridge-Utils
```
sudo apt-get install bridge-utils
```

Configure your network interfaces (this is what I used successfully):
```
$ sudo vi /etc/network/interfaces
auto lo enp0s25
iface lo inet loopback

iface xenbr0 inet dhcp
  bridge_ports enp025

inface enp0s25 inet static
address 1##.##.117 # insert your own static ip address on this line
netmask 255.255.0.0
```

Restart networking to enable xenbr0 bridge
```
$ sudo ifdown eth0 && sudo ifup xenbr0 && sudo ifup eth0
```

(7) Configuration complete. See other portions of documentation for setup of VMs/VUDs.
