#!/bin/bash
# SNAPSHOT VM: This is a script to adjust lvm
# functionality so snapshots will automatically 
# increase in size as necessary for user.

# SETTINGS:
# NONE

# Step 1: Change lvs.conf file to allow autoextend
echo "Adjusting lvs.conf to allow autoextend..."
grep -rl "snapshot_autoextend_threshold = 100" /etc/lvm/lvm.conf | xargs sudo sed -i "s/snapshot_autoextend_threshold = 100/snapshot_autoextend_threshold = 80/g"

echo "END OF SCRIPT"
