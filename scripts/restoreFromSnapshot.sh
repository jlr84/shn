#!/bin/bash
# Restore from Snapshot: This is a script to restore from  
# a snapshot given a snapshot name and currentVM name 

# SETTINGS:
# Note: Currently set to take the name of the current vm, and the 
# name of the snapshot to restore to as the first/second
# command line arguments. Comment out the next two lines  
# and remove "#" from the third/fourth lines
# to specify names here instead of via command line. 
CURRENTVM=$1
SNAPNAME=$2
#CURRENTVM="vud2"
#SNAPNAME="vud2_snap_1"

# Step 1: STOP current VUD/VM
echo "Stopping Current VUD/VM, $CURRENTVM..."
sudo xl shutdown $CURRENTVM


# Step 2: Perform Merge 
echo "Performing Merge / reverting to snapshot"
sudo lvconvert --merge /dev/xen1/$SNAPNAME

# Verify name change
echo "VERIFY Changes:"
sudo lvs


# Step 3: Start Newly restored VUD/VM 
echo "Starting restored VM now, named $CURRENTVM."
sudo xl create /etc/xen/$CURRENTVM.cfg
