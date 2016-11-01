#!/bin/bash
# CLONE VM: This is a script to clone a VM for the SHNet project

#SETTINGS:
CURRENTVM="ubud2"
CLONEDVM="vud2"

# Step 1: Create new LVS Partition (named 'vud2')
sudo lvcreate -y -L 10G -n $CLONEDVM /dev/xen1

# Verify Created with:
echo "VERIFY LVS PARTITION $CLONEDVM CREATED:"
sudo lvs


# Step 2: Shutdown lvs if in use
echo "Shutdown Current LVS, $CURRENTVM"
sudo xl shutdown $CURRENTVM


# Step 3: Copy OLD Disk (vud1) to NEW Disk (vud2)
echo "Copying Disks... this may take a few minutes"
sudo dd if=/dev/xen1/$CURRENTVM of=/dev/xen1/$CLONEDVM bs=32768


# Step 4: Create config file to use new lvs disk
# a) Copy old config to new config
echo "Updating config file"
sudo cp /etc/xen/$CURRENTVM.cfg /etc/xen/$CLONEDVM.cfg

# b) Swap old name (vud1) for new name (vud2)
grep -rl "$CURRENTVM" /etc/xen/$CLONEDVM.cfg | xargs sudo sed -i "s/$CURRENTVM/$CLONEDVM/g"


# Step 5: Start Old lvs back up. (New remains as clone.) 
echo "Re-starting old (original/cloned) VM now."
sudo xl create /etc/xen/$CURRENTVM.cfg


