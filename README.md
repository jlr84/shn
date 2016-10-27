# SHNet (Self-healing Network) Project 
[GA Tech CS6266, Fall 2016]

The goal of this project is to produce a “self-healing” network (SHNet) that provides the capability to automatically respond to and remediate security vulnerabilities detected among end-host systems within the network.

SHNet operation is supported by the use of a hypervisor and virtualized user desktop (VUD) for each [user, non-server] end-host within the network. This structure allows each end-user to operate a virtualized desktop, while SHNet-related communication remains at the hypervisor level, one layer below the end-user. 

This project consists of four main components: A (1) Monitor node receives regular updates from each VUD operated on the network via an (2) End-host Security Monitor (ESM) running on each VUD. The ESM identifies the associated health/security status of the VUD as either 'CLEAN' or 'COMPROMISED' and transmits this status to the Monitor node. (Note: In this project the ESM is simply simulating the detection of a compromised end-host, whereas a full-fledged commercial product would be used in a real-world setting.) A (3) Controller node reads the network health/security status maintained by the Monitor and takes action as necessary to mitigate any concerns. The Controller takes necessary action by communicating with an (4) SHNet Agent running at the hypervisor level of each end-host. By communicating with the Agent, the Controller takes action to restore, snapshot, or otherwise roll-back each VUD to a time-period prior to suspected compromise.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine --with some limitations, mentioned below -- for development and testing purposes. See deployment section for notes on how to deploy the project for full functionality.

### Prerequisites

Unless stated specifically elsewhere, for individual components, this project requires:

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

These instructions will get you a copy of the project up and running on your local machine -- with some limitations, mentioned below -- for development and testings purposes. Continue with the deployment section folling these steps for notes on how reconfigure the project for full functionality.

TODO: Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

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
* Burn the above-reference .iso to DVD; 
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
