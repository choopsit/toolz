#!/usr/bin/env python3

import sys
import re
import os
import pathlib
import toolzlib

__description__ = "Manage VirtualBox VM Groups"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def usage(errcode):
    myscript = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {myscript} [OPTION]")
    print(f"{ci}Options{c0}:")
    print("  -h,--help:       Print this help")
    print("  list:            Display running VMs")
    vboxdef = "(default: 'choopsit')"
    print("  start [VBOXGRP]: Start essential VMs of VBOXGRP {vboxdef}")
    print("  stop [VBOXGRP]:  Stop essential machines of VBOXGRP {vboxdef}")
    print()
    exit(errcode)


def is_vboxgrp(folder, vboxstock):
    ret = False

    for vboxgrp in os.listdir(vboxstock):
        if folder == vboxgrp:
            ret = True

    return ret


def is_vm(vm):
    ret = False
    runningvms = os.popen("vboxmanage list vms").read()
    if vm in runningvms:
        ret = True

    return ret


def is_running(vm):
    ret = False
    runningvms = os.popen("vboxmanage list runningvms").read()
    if vm in runningvms:
        ret = True

    return ret


def start_vboxgrp(vms, vboxgrp):
    print(f"{ci}Starting VBox group '{vboxgrp}'...{c0}")
    for vm in vms:
        print(f"{ci}Starting VM '{vm}'...{c0}")
        if not is_vm(vm):
            print(f"{error} No VM '{vm}' in '{vboxgrp}'")
        elif not is_running(vm):
            startvm = f"VBoxManage startvm {vm} --type headless"
            if os.system(startvm) == 0:
                print(f"{done} '{vm}' started")
            else:
                print(f"{error} Failed to start '{vm}'")
        else:
            print(f"{warning} '{vm}' is already running")
    print()


def stop_vboxgrp(vms, vboxgrp):
    print(f"{ci}Stopping VBox group '{vboxgrp}'...{c0}")
    for vm in vms:
        print(f"{ci}Stopping VM '{vm}'...{c0}")
        if not is_vm(vm):
            print(f"{error} No VM '{vm}' in '{vboxgrp}'")
        elif is_running(vm):
            # stopvm = f"VBoxManage controlvm {vm} acpipowerbutton"
            stopvm = f"VBoxManage controlvm {vm} poweroff"
            if os.system(stopvm) == 0:
                print(f"{done} '{vm}' stopped")
            else:
                print(f"{error} Failed to stop '{vm}'")
        else:
            print(f"{warning} '{vm}' is already down") 
    print()


def list_vms():
    print(f"{ci}Running VMs{c0}:")
    if os.popen("vboxmanage list runningvms").read() == "":
        print(f"{cw}None{c0}")
    else:
        os.system("vboxmanage list runningvms")
    print()


if __name__ == "__main__":
    home = pathlib.Path.home()

    if not toolzlib.pkg.is_installed("virtualbox"):
        print(f"{error} VirtualBox not installed\n")
        exit(1)

    if len(sys.argv) > 3:
        print(f"{error} Too many aguments")
        usage(1)
        
    myvboxstock = f"{home}/Work/vbox"

    myvboxgrp = ""
    if len(sys.argv) >= 2:
        for arg in sys.argv:
            if re.match('^-(h|-help)$', arg):
                usage(0)
        if sys.argv[1] == "list":
            if len(sys.argv) == 2:
                list_vms()
                exit(0)
            else:
                print(f"{error} 'list' option does not take arguments")
                usage(1)
        elif re.match('^st(art|op)$', sys.argv[1]):
            vboxcmd = sys.argv[1]
            if len(sys.argv) == 2:
                myvboxgrp = "choopsit"
            elif is_vboxgrp(sys.argv[2], myvboxstock):
                myvboxgrp = sys.argv[2]
            else:
                print(f"{error} No VBox group '{sys.argv[2]}'")
                exit(1)
    else:
        print(f"{error} Need arguments")
        usage(1)
    
    myvms = []
    if myvboxgrp == "HouseOfZeMinous":
        myvms = ["dhcp"]
    if myvboxgrp == "choopsit":
        myvms = ["router", "pxe", "salt"]
    
    if vboxcmd == "start":
        start_vboxgrp(myvms, myvboxgrp)
    elif vboxcmd == "stop":
        stop_vboxgrp(myvms, myvboxgrp)
