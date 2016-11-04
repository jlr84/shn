from xmlrpc.server import SimpleXMLRPCServer
import ssl
import logging
import config
import dbm
import subprocess
import datetime
import os


######################################
# Supporting Functions
######################################
# Return name of current VUD/VM
def getCurrentVUD():
    log = logging.getLogger(__name__)
    log.debug("Getting current VM/VUD name...")
    currentVUD = "NONE"
    try:
        with dbm.open('cache_agent_history', 'r') as db:
            currentVUD = (db.get('current')).decode("utf-8")
            log.debug("Name retreived: '%s'" % currentVUD)
    except:
        log.debug("No cache found or read failed")

    return currentVUD


# Remove entry from persistent memory
def removeEntryFromDB(entryName):
    log = logging.getLogger(__name__)
    log.debug("Removing entry from DB...")
    response = "NO ACTION TAKEN"
    try:
        with dbm.open('cache_agent_history', 'c') as db:
            del db[entryName]
            log.debug("Entry '%s' deleted" % entryName)
            response = "SUCCESS"
    except:
        log.debug("Unknown error. Delete failed")
        response = "ERROR"

    return response


# Return name to use for clone
def getCloneName(currentName):
    log = logging.getLogger(__name__)
    log.debug("Finding name for clone...")
    fileName = "ERROR"

    # Starting with 1, test if clone name exists until name is found
    # that does not exist
    exists = True
    num = 1
    while exists:
        # Create name
        fileName = ''.join([currentName, "_clone_", str(num)])
        log.debug("Trying name: %s" % fileName)
        try:
            with dbm.open('cache_agent_history', 'r') as db:
                oldClone = db.get(fileName)
                log.debug("Clone name tested as: %s" % oldClone)
                if oldClone is None:
                    exists = False
                else:
                    num = num + 1
        except:
            log.warning("No cache found or read failed")
            exists = False

    log.debug("Returning name: %s" % fileName)
    return fileName


# Return non-used name to use for VUD
def getVudName():
    log = logging.getLogger(__name__)
    log.debug("Finding name for VUD...")
    fileName = "ERROR"

    # Starting with 1, test if vud name exists until name is found
    # that does not exist
    exists = True
    num = 1
    while exists:
        # Create name
        fileName = ''.join(["vud", str(num)])
        # Create file path
        filePath = ''.join(["/etc/xen/", fileName, ".cfg"])
        log.debug("Trying name: %s" % fileName)
        log.debug("Trying filepath: %s" % filePath)
        exists = os.path.isfile(filePath)
        log.debug("Clone name %s tested as: %s" % (fileName, exists))
        if exists:
            num = num + 1

    log.debug("Returning name: %s" % fileName)
    return fileName


# Remove Snapshot
def removeOneSnap(snapName):
    log = logging.getLogger(__name__)
    log.debug("Removing Snapshot...")
    result = "NO ACTION TAKEN"

    # Make process call string
    callString = ''.join(["sudo lvremove -y /dev/xen1/", snapName])
    log.debug("Command: %s" % callString)

    rc = subprocess.call(callString, shell=True)
    if rc == 0:
        result = "Success"
    elif rc == 1:
        result = "Failed"
        print("Remove... FAILED")
        print("Is the Agent running as root/sudo as required?")
    else:
        result = "Failed"
        print("Remove... FAILED(2)")

    log.debug("Remove %s." % result)

    return result


# Rename Snapshots (remove but keep for forensic analysis)
def renameSnap(snapName, snapTime):
    log = logging.getLogger(__name__)
    log.debug("Renaming Snapshot...")
    result = "NO ACTION TAKEN"

    # Make process call string
    callString = ''.join(["sudo lvrename /dev/xen1/", snapName,
                          " /dev/xen1/OFFLINE_", snapName,
                          "_", snapTime])
    log.debug("Command: %s" % callString)

    rc = subprocess.call(callString, shell=True)
    if rc == 0:
        result = "Success"
    elif rc == 1:
        result = "Failed"
        print("Rename... FAILED")
        print("Is the Agent running as root/sudo as required?")
    else:
        result = "Failed"
        print("Rename... FAILED(2)")

    log.debug("Rename %s." % result)

    return result


# Remove all associated snapshots
def removeSnaps(currentName, dtime):
    log = logging.getLogger(__name__)
    log.debug("Removing related snapshots from DB...")
    fileName = "ERROR"

    # Starting with 1, test if vud name exists until name is found
    # that does not exist
    exists = True
    num = 1
    while exists:
        # Create name
        fileName = ''.join([currentName, "_snap_", str(num)])
        log.debug("Trying name: %s" % fileName)
        try:
            with dbm.open('cache_agent_history', 'c') as db:
                oldSnapshot = db.get(fileName)
                log.debug("Snapshot name tested as: %s" % oldSnapshot)
                if oldSnapshot is None:
                    exists = False
                else:
                    num = num + 1
                    removeEntryFromDB(fileName)
                    # Rename snapshot
                    result = renameSnap(fileName, dtime)
                    log.debug("Rename Result[%s]: %s" % (fileName, result))
        except:
            log.warning("No cache found or read failed")
            exists = False

    log.debug("Removed %d Entries" % (num - 1))
    result = num - 1
    return result


# Remove NEWER snapshots
def removeNewerSnaps(currentName, snapName):
    log = logging.getLogger(__name__)
    log.debug("Removing NEWER snapshots from DB...")
    fileName = "ERROR"

    # Starting with 1, test if vud name exists until name is found
    # that does not exist
    exists = True
    nameFound = False
    num = 1
    cnt = 0

    # FIRST, find name that matches snapName
    while not nameFound and num < 9999:
        # Create name
        fileName = ''.join([currentName, "_snap_", str(num)])
        log.debug("Does name match? %s" % fileName)
        if fileName == snapName:
            nameFound = True
            num = num + 1
        else:
            num = num + 1

    # SECOND, remove the remaining names that are present
    while exists:
        # Create name (this will first try one number above selected
        # snapName and then increase until no stored name found)
        fileName = ''.join([currentName, "_snap_", str(num)])
        log.debug("Trying name: %s" % fileName)
        try:
            with dbm.open('cache_agent_history', 'c') as db:
                oldSnapshot = db.get(fileName)
                log.debug("Snapshot name tested as: %s" % oldSnapshot)
                if oldSnapshot is None:
                    exists = False
                else:
                    num = num + 1
                    removeEntryFromDB(fileName)
                    # Rename snapshot
                    result = removeOneSnap(fileName)
                    log.debug("Remove Result[%s]: %s" % (fileName, result))
                    cnt = cnt + 1
        except:
            log.warning("No cache found or read failed")
            exists = False

    log.debug("Removed %d Entries" % (cnt))
    return cnt


# Return name to use for snapshot
def getSnapshotName(currentName):
    log = logging.getLogger(__name__)
    log.debug("Finding name for snapshot...")
    fileName = "ERROR"

    # Starting with 1, test if snapshot name exists until name is found
    # that does not exist
    exists = True
    num = 1
    while exists:
        # Create name
        fileName = ''.join([currentName, "_snap_", str(num)])
        log.debug("Trying name: %s" % fileName)
        try:
            with dbm.open('cache_agent_history', 'r') as db:
                oldSnapshot = db.get(fileName)
                log.debug("Snapshot name tested as: %s" % oldSnapshot)
                if oldSnapshot is None:
                    exists = False
                else:
                    num = num + 1
        except:
            log.warning("No cache found or read failed")
            exists = False

    log.debug("Returning name: %s" % fileName)
    return fileName


# Return array of clones already saved
def getCloneList(currentName):
    log = logging.getLogger(__name__)
    log.debug("Finding list of saved clone(s)...")
    fileName = "ERROR"
    cloneList = []

    # Starting with 1, test if clone name exists until name is found
    # that does not exist; save each name/time pair to send to user
    exists = True
    num = 1
    while exists:
        # Create name
        fileName = ''.join([currentName, "_clone_", str(num)])
        log.debug("Trying name: %s" % fileName)

        # Attempt to retrieve record
        try:
            with dbm.open('cache_agent_history', 'r') as db:
                oldClone = db.get(fileName)
                log.debug("Clone name tested as: %s" % oldClone)
                if oldClone is None:
                    exists = False
                else:
                    # Save name/time to list
                    pair = [fileName, (oldClone.decode("utf-8"))]
                    cloneList.append(pair)
                    num = num + 1
        except:
            log.warning("No cache found or read failed")
            exists = False

    log.debug("Returning %d records" % (num - 1))
    return cloneList


# Return array of snapshots already saved
def getSnapList(currentName):
    log = logging.getLogger(__name__)
    log.debug("Finding list of saved snapshot(s)...")
    fileName = "ERROR"
    snapList = []

    # Starting with 1, test if clone name exists until name is found
    # that does not exist; save each name/time pair to send to user
    exists = True
    num = 1
    while exists:
        # Create name
        fileName = ''.join([currentName, "_snap_", str(num)])
        log.debug("Trying name: %s" % fileName)

        # Attempt to retrieve record
        try:
            with dbm.open('cache_agent_history', 'r') as db:
                oldSnap = db.get(fileName)
                log.debug("Snapshot name tested as: %s" % oldSnap)
                if oldSnap is None:
                    exists = False
                else:
                    # Save name/time to list
                    pair = [fileName, (oldSnap.decode("utf-8"))]
                    snapList.append(pair)
                    num = num + 1
        except:
            log.warning("No cache found or read failed")
            exists = False

    log.debug("Returning %d records" % (num - 1))
    return snapList


# Save change to current VUD name persistent memory
def saveNewCurrentVUD(newName):
    log = logging.getLogger(__name__)
    log.debug("Saving new current VUD name to memory...")
    status = "FAILED"
    try:
        with dbm.open('cache_agent_history', 'c') as db:
            # Store name to memory
            db['current'] = newName
            log.debug("Saved current VUD name: %s" % newName)
            status = "SUCCESS"
    except:
        log.warning("ERROR writing to cache.")

    return status


# Save successful clone name to persistent memory
def saveCloneName(newName, timeSaved):
    log = logging.getLogger(__name__)
    log.debug("Saving clone name to memory...")
    status = "FAILED"
    try:
        with dbm.open('cache_agent_history', 'c') as db:
            # Store name and time pair to memory
            db[newName] = timeSaved
            log.debug("Saved clone name: %s" % newName)
            status = "SUCCESS"
    except:
        log.warning("ERROR writing to cache.")

    return status


# Save successful snapshot name to persistent memory
def saveSnapshotName(newName, timeSaved):
    log = logging.getLogger(__name__)
    log.debug("Saving snapshot name to memory...")
    status = "FAILED"
    try:
        with dbm.open('cache_agent_history', 'c') as db:
            # Store name and time pair to memory
            db[newName] = timeSaved
            log.debug("Saved snapshot name: %s" % newName)
            status = "SUCCESS"
    except:
        log.warning("ERROR writing to cache.")

    return status


######################################
# Define functions available to server
######################################
def add(x, y):
    return x+y


def subtract(x, y):
    return x-y


def multiply(x, y):
    return x*y


def divide(x, y):
    return x/y


# Get VM Status (of current VM listed in persistent memory)
def getVmStatus(key):
    log = logging.getLogger(__name__)
    log.debug("Getting Status of VM...")
    result = "NO ACTION TAKEN"
    header = ''.join(["Name                                        ID   Mem",
                      " VCPUs      State      Time\n"])

    # Get current VUD name
    vudName = getCurrentVUD()

    # Make process call string
    callString = ''.join(["/usr/sbin/xl list | grep ", vudName])
    log.debug("Command: %s" % callString)

    if key == "status":
        if not vudName == "NONE":
            log.debug("vudName is not 'NONE'")
            process = subprocess.Popen(callString, stdout=subprocess.PIPE,
                                       shell=True)
            (output, err) = process.communicate()
            output2 = output.decode("utf-8")
            rc = process.wait()
            if rc == 0:
                # VM is running; status in 'output'
                log.debug("RC code = 0")
                result = ''.join([vudName, "active. Current status is\n",
                                  header, output2])
            elif rc == 1:
                log.debug("RC code = 1")
                # VM is not running
                result = ''.join([vudName, " is NOT active [shutdown]"])
                print("No result returned; VM not running OR not enough",
                      "permissions.")
                print("Is the Agent running as root/sudo as required?")
            else:
                log.debug("RC code NOT 0 or 1")
                result = ''.join(["Finding Status for ", vudName, " FAILED; ",
                                  "Err: ", err, "Exit Code: ", rc])
                print("Finding Status FAILED. Unknown Error.")

            log.debug(result)
        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; Cannot have status of NO VUD!"
            log.debug("No VM Status: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    log.debug("Returning: %s" % result)
    return result


# Start VM (Based on current VM in persistent memory)
def startVM(key):
    log = logging.getLogger(__name__)
    log.debug("Starting up VM...")
    result = "NO ACTION TAKEN"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Make process call string
    callString = ''.join(["/usr/sbin/xl create /etc/xen/", vudName, ".cfg"])
    log.debug("Command: %s" % callString)

    # Execute Command
    if key == "start":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "Success"
            elif rc == 1:
                result = "Failed"
                print("Starting VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                log.debug("Starting VM: %s." % result)
        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to start"
            log.debug("No VM Started: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    return "Starting VM[%s]: %s." % (vudName, result)


# Stop VM (Based on current VM in persistent memory)
def stopVM(key):
    log = logging.getLogger(__name__)
    log.debug("Stopping VM...")
    result = "NO ACTION TAKEN"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Make process call string
    callString = ''.join(["/usr/sbin/xl shutdown ", vudName])
    log.debug("Command: %s" % callString)

    if key == "stop":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "Success"
            elif rc == 1:
                result = "Failed"
                print("Stopping VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                print("Stopping VM... FAILED")

            log.debug("Stopping VM %s." % result)
        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to stop"
            log.debug("No VM Stopped: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    return "Shutting down VM[%s]: %s." % (vudName, result)


# Pause VM (Based on current VM in persistent memory)
def pauseVM(key):
    log = logging.getLogger(__name__)
    log.debug("Pausing VM...")
    result = "NO ACTION TAKEN"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Make process call string
    callString = ''.join(["/usr/sbin/xl pause ", vudName])
    log.debug("Command: %s" % callString)

    # Execute Command
    if key == "pause":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "Success"
            elif rc == 1:
                result = "Failed"
                print("Pausing VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                log.debug("Pausing VM: %s." % result)
        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to pause"
            log.debug("No VM to Pause: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    return "Pausing VM[%s]: %s." % (vudName, result)


# Un-Pause VM (Based on current VM in persistent memory)
def unpauseVM(key):
    log = logging.getLogger(__name__)
    log.debug("Un-Pausing VM...")
    result = "NO ACTION TAKEN"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Make process call string
    callString = ''.join(["/usr/sbin/xl unpause ", vudName])
    log.debug("Command: %s" % callString)

    # Execute Command
    if key == "unpause":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "Success"
            elif rc == 1:
                result = "Failed"
                print("Un-Pausing VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                log.debug("Un-Pausing VM: %s." % result)
        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to pause"
            log.debug("No VM to Un-Pause: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    return "Un-Pausing VM[%s]: %s." % (vudName, result)


# Create complete backup (clone) of vm (based on current vm listed in p-memory)
def cloneVM(key):
    log = logging.getLogger(__name__)
    log.debug("Cloning VM...")
    result = "NO ACTION TAKEN"
    result2 = "NO RESULT FOR WRITE"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Get name for clone
    cloneName = getCloneName(vudName)

    # Make process call string
    callString = ''.join(["./scripts/clone.sh ", vudName, " ", cloneName])
    log.debug("Command: %s" % callString)
    log.info("WARNING: This may take a few minutes!")

    if key == "clone":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "SUCCESS"
            elif rc == 1:
                result = "Failed"
                print("Cloning VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                print("Cloning VM... FAILED")

            log.debug("Cloning VM %s." % result)

            # Save clone name in persistent memory
            saveTime = str((datetime.datetime.now()).isoformat())
            result2 = saveCloneName(cloneName, saveTime)
            log.debug("Saved to memory: %s saved at %s" % (cloneName, saveTime))
            log.info("Write to DB result: %s" % result2)

        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to clone"
            log.debug("No VM Cloned: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    # Summarize cloning result prior to sending back to user
    if result == "SUCCESS" and result2 == "SUCCESS":
        result3 = ''.join(["Cloning VM[", vudName, "]: Clone-", result,
                           ", DB Save-", result2, ", saved as '",
                           cloneName, "'"])
        log.debug("Result logged as: %s" % result3)
    else:
        result3 = ''.join(["Cloning VM[", vudName, "] FAILED: Clone-", result,
                           ", DB Save-", result2])
        log.debug("Result logged as: %s" % result3)

    return result3


# Report list of Saved clones for current vm listed in persistent memory
def cloneList(key):
    log = logging.getLogger(__name__)
    log.debug("Getting Clone List...")
    savedCloneList = []

    # Get current VUD name
    vudName = getCurrentVUD()

    if key == "cloneList":
        if not vudName == "NONE":

            # Get clone list
            savedCloneList = getCloneList(vudName)
            log.debug("Clone List: %s." % (savedCloneList))

        # If vudName == "NONE" THEN:
        else:
            log.debug("VM 'NONE' has no clones")

    else:
        log.debug("Key incorrect. Received: %s" % key)

    return savedCloneList


# Restore to clone based on name received and current vm listed in memory
def restoreClone(key, cloneName):
    log = logging.getLogger(__name__)
    log.debug("Restoring VM from Clone...")
    result = "NO ACTION TAKEN"
    result2 = "NO RESULT FOR WRITE"
    result3 = 0

    # Get current VUD name
    vudName = getCurrentVUD()

    # Set alternate name for current VUD (do NOT delete to
    # allow forensic analysis later)
    timeOff = datetime.datetime.now().strftime('%Y%b%d_%H%Mh')
    newName = ''.join(["OFFLINE_", vudName, "_", timeOff])

    # Make process call string
    callString = ''.join(["./scripts/restoreFromClone.sh ", vudName,
                          " ", cloneName, " ", newName])
    log.debug("Command: %s" % callString)

    if key == "restore":
        if not vudName == "NONE":
            log.debug("Executing restore now...")
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "SUCCESS"
            elif rc == 1:
                result = "Failed"
                print("Restore VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                print("Restore VM... FAILED")

            log.debug("Restore VM %s." % result)

            # Remove clone name from persistent memory
            result2 = removeEntryFromDB(cloneName)
            log.debug("Removed name: %s" % (cloneName))
            log.info("Write to DB result: %s" % result2)
            # Remove related snapshots
            result3 = removeSnaps(vudName, timeOff)
            log.debug("RemoveSnaps Complete; result: %d" % result3)

        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to restore"
            log.debug("No VM Restored: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    # Summarize cloning result prior to sending back to user
    if result == "SUCCESS" and result2 == "SUCCESS":
        result4 = ''.join(["VM[", vudName, "] Restored From Clone '",
                           cloneName, "'; Result:", result,
                           "\nDB Save Result: ", result2,
                           "; ", str(result3), " related snapshots removed",
                           "\nPRIOR DRIVE OFFLINE, stored as: '",
                           newName, "'"])
        log.debug("Result logged as: %s" % result4)
    else:
        result4 = ''.join(["Restore VM[", vudName, "] FAILED: Restore Result--",
                           result, ", DB Save Result--", result2])
        log.debug("Result logged as: %s" % result4)

    return result4


# Create snapshot of vm (based on current vm listed in persistent memory)
def snapshotVM(key):
    log = logging.getLogger(__name__)
    log.debug("Creating snapshot of VM...")
    result = "NO ACTION TAKEN"
    result2 = "NO RESULT FOR WRITE"

    # Get current VUD name
    vudName = getCurrentVUD()

    # Get name for clone
    snapName = getSnapshotName(vudName)

    # Make process call string
    callString = ''.join(["./scripts/snapshot.sh ", vudName, " ", snapName])
    log.debug("Command: %s" % callString)

    if key == "snapshot":
        if not vudName == "NONE":
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "SUCCESS"
            elif rc == 1:
                result = "Failed"
                print("Snapshot of VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                print("Snapshot of VM... FAILED")

            log.debug("Snapshot of VM %s." % result)

            # Save snapshot name in persistent memory
            saveTime = str((datetime.datetime.now()).isoformat())
            result2 = saveSnapshotName(snapName, saveTime)
            log.debug("Saved to memory: %s saved at %s" % (snapName, saveTime))
            log.info("Write to DB result: %s" % result2)

        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to snapshot"
            log.debug("No VM Snapshot created: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    # Summarize snapshot result prior to sending back to user
    if result == "SUCCESS" and result2 == "SUCCESS":
        result3 = ''.join(["Snapshot of VM[", vudName, "]: Snapshot-", result,
                           ", DB Save-", result2, ", saved as '",
                           snapName, "'"])
        log.debug("Result logged as: %s" % result3)
    else:
        result3 = ''.join(["Snapshot of VM[", vudName, "] FAILED: Snapshot-",
                           result, ", DB Save-", result2])
        log.debug("Result logged as: %s" % result3)

    return result3


# Report list of Saved snapshots for current vm listed in persistent memory
def snapshotList(key):
    log = logging.getLogger(__name__)
    log.debug("Getting Snapshot List...")
    savedSnapList = []

    # Get current VUD name
    vudName = getCurrentVUD()

    if key == "snapshotList":
        if not vudName == "NONE":

            # Get snapshot list
            savedSnapList = getSnapList(vudName)
            log.debug("Snapshot List: %s." % (savedSnapList))

        # If vudName == "NONE" THEN:
        else:
            log.debug("VM 'NONE' has no snapshots")

    else:
        log.debug("Key incorrect. Received: %s" % key)

    return savedSnapList


# Restore to snapshot based on name received and current vm listed in memory
def restoreSnap(key, snapName):
    log = logging.getLogger(__name__)
    log.debug("Restoring VM from Snapshot...")
    result = "NO ACTION TAKEN"
    result2 = "NO RESULT FOR WRITE"
    result3 = 0

    # Get current VUD name
    vudName = getCurrentVUD()

    # Make process call string
    callString = ''.join(["sudo lvconvert --merge /dev/xen1/", snapName])
    log.debug("Command: %s" % callString)

    if key == "restore":
        if not vudName == "NONE":
            log.debug("Executing restore now...")
            rc = subprocess.call(callString, shell=True)
            if rc == 0:
                result = "SUCCESS"
            elif rc == 1:
                result = "Failed"
                print("Restore VM... FAILED")
                print("Is the Agent running as root/sudo as required?")
            else:
                result = "Failed"
                print("Restore VM... FAILED")

            log.debug("Restore VM %s." % result)

            # Remove snapshot name from persistent memory
            result2 = removeEntryFromDB(snapName)
            log.debug("Removed name: %s" % (snapName))
            log.info("Write to DB result: %s" % result2)

            # Remove related snapshots newer than this one
            result3 = removeNewerSnaps(vudName, snapName)
            log.debug("RemoveNewerSnaps Complete; result: %d" % result3)

        # If vudName == "NONE" THEN:
        else:
            result = "VUD=NONE; NO VUD to restore"
            log.debug("No VM Restored: %s" % result)

    else:
        log.debug("Key incorrect. Received: %s" % key)

    # Summarize restore result prior to sending back to user
    if result == "SUCCESS" and result2 == "SUCCESS":
        result4 = ''.join(["VM[", vudName, "] Restored From Snapshot '",
                           snapName, "'; Result:", result,
                           "; DB Save Result: ", result2,
                           "\nALSO REMOVED ", result3,
                           " more-recent snapshot(s)"])
        log.debug("Result logged as: %s" % result4)
    else:
        result4 = ''.join(["Restore VM[", vudName, "] FAILED: Restore Result--",
                           result, ", DB Save Result--", result2])
        log.debug("Result logged as: %s" % result4)

    return result4


# Receive report of FAILED Agent Registration
def failed(name):
    log = logging.getLogger(__name__)
    log.debug("Agent registration with %s FAILED." % name)
    return "Failed registration acknowledged."


# Receive report of good / confirmed Agent Registration
def confirm(name, port, idnum, time):
    log = logging.getLogger(__name__)
    log.debug("Agent Registered to "
              "%s:%d [Conf# %d] at %s." % (name, port, idnum, time))

    log.debug("Values Received: %s, %d, %d, %s" % (name, port, idnum, time))
    storeName = str(name)
    storePort = str(port)
    storeID = str(idnum)
    storeTime = str(time)
    log.debug("Values Storing: %s, %s, %s, %s" % (storeName, storePort,
                                                  storeID, storeTime))

    try:
        with dbm.open('cache_agent', 'w') as db:
            # Get current total and add 1 with type conversions
            newtotal = str(int((db.get('total')).decode("utf-8")) + 1)
            # Store new total in persistent storage
            db['total'] = newtotal
            # Create names based on connection number
            savename = "%s.name" % (newtotal)
            saveport = "%s.port" % (newtotal)
            saveid = "%s.id" % (newtotal)
            savetime = "%s.time" % (newtotal)
            # Save connection info to persistent storage
            db[savename] = storeName
            db[saveport] = storePort
            db[saveid] = storeID
            db[savetime] = storeTime
            log.debug("Cache found. Values stored in old cache.")
            log.debug("Saved: %s, %s, %s, %s" % (storeName, storePort,
                                                 storeID, storeTime))
    except:
        log.debug("No cache file found; creating new file.")
        with dbm.open('cache_agent', 'c') as db:
            db['total'] = "1"
            savename = "1.name"
            saveport = "1.port"
            saveid = "1.id"
            savetime = "1.time"
            db[savename] = storeName
            db[saveport] = storePort
            db[saveid] = storeID
            db[savetime] = storeTime
            log.debug("Saved: %s, %s, %s, %s" % (storeName, storePort,
                                                 storeID, storeTime))

    returnMessage = ''.join(["Conf# ", str(idnum), " Acknowledged."])
    print("Registration Acknowledged (ID#%d)" % (idnum))
    return returnMessage


#########################################
# Main server function: An xml rpc server
# for responding to client requests.
#########################################
def runServer(ipAdd, portNum, serverCert, serverKey):
    log = logging.getLogger(__name__)
    log.info("Starting runServer Module")
    log.debug("serverCert: %s" % (serverCert))
    log.debug("serverKey: %s" % (serverKey))

    # Create XMLRPC Server, based on ipAdd/port received
    log.debug("Trying socket now...")
    foundPort = False
    loopNumber = 1
    config.AgentServerUp = False
    while not foundPort and loopNumber < 3:
        try:
            server = SimpleXMLRPCServer((ipAdd, portNum))
            foundPort = True
            config.agentServerUp = True

        except OSError:
            log.debug("Port [%d] already in use." % portNum)
            # Keep port range between 35000 and 39000
            if portNum < 39000:
                portNum = portNum + 1
            else:
                portNum = 35000
                loopNumber = loopNumber + 1

    if loopNumber > 2:
        log.exception("NO open ports found!!!")
        raise SystemExit

    # Set global var in agent to portNum used
    config.agntServerPort = portNum

    # Create/Wrap server socket with ssl
    try:
        server.socket = ssl.wrap_socket(server.socket,
                                        certfile=serverCert,
                                        keyfile=serverKey,
                                        do_handshake_on_connect=True,
                                        server_side=True)
        # Register available functions
        log.debug("Registering Functions")
        server.register_multicall_functions()
        server.register_function(add, 'add')
        server.register_function(subtract, 'subtract')
        server.register_function(multiply, 'multiply')
        server.register_function(divide, 'divide')
        server.register_function(confirm, 'confirm')
        server.register_function(failed, 'failed')
        server.register_function(startVM, 'startVM')
        server.register_function(stopVM, 'stopVM')
        server.register_function(cloneVM, 'cloneVM')
        server.register_function(snapshotVM, 'snapshotVM')
        server.register_function(pauseVM, 'pauseVM')
        server.register_function(unpauseVM, 'unpauseVM')
        server.register_function(getVmStatus, 'getVmStatus')
        server.register_function(cloneList, 'cloneList')
        server.register_function(restoreClone, 'restoreClone')
        server.register_function(snapshotList, 'snapshotList')
        server.register_function(restoreSnap, 'restoreSnap')

        # Start server listening [forever]
        log.info("Server listening on port %d..." % (portNum))
        print("Server listening on port %d..." % (portNum))
        server.serve_forever()

    except FileNotFoundError:
        log.warning("CERT or KEY FILE not found.")
        log.warning("Verify CERT/KEY Files and try again.")
