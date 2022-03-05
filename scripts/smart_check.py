#!/usr/lib/python2.7
#####!/usr/bin/env python
import subprocess
import os
import glob
import re
import sys

if sys.version_info[0] > 2:
    print('Python Detected: ', sys.version_info[0])
else:
    try:
        import commands  # py2
    except NameError:
        pass

# Global variables
WEAR_WARN_860_PRO_1TB = 5500
WEAR_CRIT_860_PRO_1TB = 5750
WEAR_WARN = 5
WEAR_CRIT = 2
SSDREMAP = 400
disk_list = []


# function to grab output from a shell command
def fetch(cmd, arg):
    command = [cmd, arg]
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    text = p.stdout.read()
    retcode = p.wait()
    return str(text)


# Simpler function to fetch output of shell command, but may not work on Python3+
def shell(cmd):
    (retval, output) = commands.getstatusoutput(cmd)
    return output


# self-contained function to check the disk
# mode = sata or nvme
def disk_check(smart, file_name_pattern, mode):
    for sdx in glob.iglob(file_name_pattern):
        device = sdx.split("/")[3]
        if mode == 'sata':
            model = str(shell(smart + ' -i /dev/' + device + ' | grep "Device Model" | cut -c 19-'))
        elif mode == 'nvme':
            model = str(shell(smart + ' -i /dev/' + device + ' | grep "Model Number" |  awk "{print $4}"'))
        else:
            print("2 check_smart_ " + device + " ERROR: Unrecognized device mode: " + mode + ".")
            return

        # Spinning disks, which key on pending sectors and remap count.
        if (model.startswith('WDC') or model.startswith('TOSHIBA') or model.startswith('ST1') or model.startswith(
                'ST3') or model.startswith('ST5') or model.startswith('ST9') or model.startswith('GB1000')):
            remap = int(shell(smart + ' -a /dev/' + device + " | grep Reallocated_Sector_Ct | awk \'{print $10}\'"))
            pend = int(shell(smart + ' -a /dev/' + device + " | grep Current_Pending_Sector | awk \'{print $10}\'"))
            hours = int(shell(smart + ' -a /dev/' + device + " | grep Power_On_Hours | awk \'{print $10}\'"))

            if (remap > 50) or (pend > 0):
                print("2 Check_Smart_" + device + " - CRITICAL - " + device + " SMART failure Hours=" + str(
                    hours) + " Remap=" + str(remap) + " Pending=" + str(pend))
            else:
                print("0 Check_Smart_" + device + " - OK - " + device + " clean Hours=" + str(hours))

        # Fetch NVMe data
        elif mode == 'nvme':
            # Normalize wear to mean life remaining, like is true for SATA
            wear = 100 - int(
                shell(smart + ' -a /dev/' + device + " | grep 'Percentage Used' | awk '{print $3}' | cut -d '%' -f1"))
            # No rsvd block count exposed for NVMe, so put a 0 which is always less than the threshold for SATA disks
            entry = {'device': device, 'wear': wear, 'rsvd': 0}
            disk_list.append(entry)

        # SSD relying on raw data due to normalized smartctl output data being too conservative. Tests wear level and
        # thus cares about raid locality
        elif '860 PRO 1TB' in model:
            wear = int(shell(smart + ' -a /dev/' + device + " | grep Wear_Level | awk '{print $10}'"))
            rsvd = int(shell(smart + ' -a /dev/' + device + " | grep Used_Rsvd | awk '{print $10}'"))

            # Normalize manually
            wear = 100 - (wear / WEAR_CRIT_860_PRO_1TB)
            entry = {'device': device, 'wear': wear, 'rsvd': rsvd}
            disk_list.append(entry)

        # Other SSD models that have acceptable SMART values
        elif ('SSD' in model or model.startswith('Kingston SKC') or model.startswith('Micro_1100') or model.startswith(
                'SAMSUNG MZ7LM') or model.startswith('SAMSUNG MZ7LH')):
            wear = int(shell(smart + ' -a /dev/' + device + " | grep Wear_Level | awk '{print $4}'"))
            rsvd = int(shell(smart + ' -a /dev/' + device + " | grep Used_Rsvd | awk '{print $10}'"))

            entry = {'device': device, 'wear': wear, 'rsvd': rsvd}
            disk_list.append(entry)
    # end of for looping over the disks

    # Fetch RAID info from mdadm about these devices and integrate with the smartctl data
    populate_raid_info(disk_list)

    # Iterate over each disk and mark it good or bad based on thresholds
    for disk in disk_list:

        # Fail if too many remaps. The good/ok gets overwritten by wear leveling checks if needed
        if disk['rsvd'] > SSDREMAP:
            disk['status'] = "prefail"
            disk['warn_type'] = "WARNING"
        else:
            disk['status'] = "good"
            disk['warn_type'] = "OK"

        # Fail independently if too much wear: permits a crit here to override a simple warn from remaps
        # Wear values are 99 (Best) down to 0 (no predicted write life left), so <= is the proper check
        if disk['wear'] <= WEAR_CRIT:
            disk['status'] = "prefail"
            disk['warn_type'] = "CRITICAL"
        elif disk['wear'] <= WEAR_WARN:
            disk['status'] = "prefail"
            disk['warn_type'] = "WARNING"

    # Now that health data on all disks are populated, run through each disk again and determine
    # whether to alert it as good or bad.
    # As long as one of the disks in a set is OK, both shall report OK (policy reasons)

    for disk in disk_list:
        if disk['status'] == "good":
            print("0 Check_Smart_" + disk['device'] + " wear_life_remaining=" + str(disk['wear']) + ";" + str(
                WEAR_WARN) + ";" + str(WEAR_CRIT) + " remaps=" + str(disk['rsvd']) + " " + disk['device'] + " OK")
        # If status is not good, find its pair and see if it is in prefail also
        else:
            # Report bad but with 0 code (meaning OK) if one disk in the pair has problems
            # Report bad and NOT ok if both disks in the pair have problems
            pair = find_pair(disk, disk_list)
            if pair['status'] == "good":
                print("0 Check_Smart_" + disk['device'] + " wear_life_remaining=" + str(disk['wear']) + ";" + str(
                    WEAR_WARN) + ";" + str(WEAR_CRIT) + " remaps=" + str(disk['rsvd']) + " " + disk['device'] + " " + \
                      disk['warn_type'])
            else:
                print("2 Check_Smart_" + disk['device'] + " wear_life_remaining=" + str(disk['wear']) + ";" + str(
                    WEAR_WARN) + ";" + str(WEAR_CRIT) + " remaps=" + str(disk['rsvd']) + " " + disk['device'] + " " + \
                      disk['warn_type'])


# Fetch the list of md arrays from the system and populates devices dictionary with them
# Finds the first raid10 device and uses it to determine which disks are in what sets.
# Area for future improvement: check all arrays instead of just the first, for sanity
# Also, it relies on adjacency to determine set info. In a 4x R10 there are two set-As
# and two set-Bs and it presumes that near=2 is the setting for deciding which to check.

def populate_raid_info(devices):
    arrays = shell("mdadm --detail --scan")
    for array in arrays.splitlines():
        device = array.split(' ')[1]
        raid_type = shell("mdadm --detail " + device + " | grep 'Raid Level' | awk '{print $4}'")

        if raid_type != 'raid10':
            continue

        # Fetch detailed set information
        for dev in devices:
            raid_device = shell("mdadm --detail " + device + " | grep " + dev['device'] + " | awk '{print $4}'")
            dev['RaidDevice'] = int(raid_device)
            set_info = shell("mdadm --detail " + device + " | grep " + dev['device'] + " | awk '{print $7}'")
            dev['set'] = set_info


# Finds the R10 pair in a set
# Presumes near=2
def find_pair(disk, devices):
    set_name = disk['set']
    raid_device = disk['RaidDevice']

    # If even, pair is +1 id
    if (raid_device % 2) == 0:
        return fetch_disk_by_id(disk['RaidDevice'] + 1, devices)
    else:
        return fetch_disk_by_id(disk['RaidDevice'] - 1, devices)


def fetch_disk_by_id(id, devices):
    for d in devices:
        if d['RaidDevice'] == id:
            return d
    return []


## MAIN CODE

# determine which disk type the machine uses
sdx = os.path.isfile("/sys/block/sda/size")
nvme_x = os.path.isfile("/sys/block/nvme0n1/size")

# Fail silently and early out of devices that lack both. These would be VMs with
# xvda and such, which ought to neither have SMARTmontools nor physical disks to check
if not sdx and not nvme_x:
    exit()

# check for smartmontools
smart = fetch("which", "smartctl").split("\n")[0]
if not smart:
    print("2 check_smart_sda ERROR: Unable to detect smartmontools. Is it installed?")
    exit()

# execute appropriate check
if sdx and nvme_x:
    disk_check(smart, '/sys/block/sd?', 'sata')
    disk_check(smart, '/sys/block/nvme?n1', 'nvme')
elif sdx:
    disk_check(smart, '/sys/block/sd?', 'sata')

elif nvme_x:
    disk_check(smart, '/sys/block/nvme?n1', 'nvme')
