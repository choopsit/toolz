#!/usr/bin/env python3

import os
import toolzlib

__description__ = "System functions module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def reboot():
    """Ask for reboot"""

    if not toolzlib.yesno("Reboot now", "y"):
        os.system("reboot")


def get_distro():
    """Return distro name based on '/etc/os-release' content"""

    distro = ""

    with open("/etc/os-release", "r") as f:
        for line in f:
            if line.startswith("ID="):
                distro = line.split("=")[1].rstrip()

    return distro


def get_codename():
    """Return codename based on '/etc/os-release' content"""

    codename = ""

    with open("/etc/os-release", "r") as f:
        for line in f:
            if line.startswith("VERSION_CODENAME="):
                codename = line.split("=")[1].rstrip()

    if get_distro() == "debian":
        stable = "bullseye"
        testing = "bookworm"

        if codename != stable:
            testsid = "apt search firefox 2>/dev/null | grep ^firefox/"

            if os.popen(testsid).read() != "":
                codename = "sid"
            else:
                codename = testing

    return codename


def prereq():
    """Test prerequisites: Debian stable or later"""

    distro = get_distro()
    if distro != "debian":
        print(f"{error} OS is not Debian")
        exit(1)

    olddebian = ["buster", "stretch", "jessie", "wheezy", "squeeze", "lenny"]
    codename = get_codename()
    if codename in olddebian:
        print(f"{error} '{codename}' is a too old Debian version")
        exit(1)

    if os.getuid() != 0:
        print(f"{error} Need higher privileges")
        exit(1)


def is_vm():
    """Check if machine is virtual"""

    testkvm = "lspci | grep -q paravirtual"
    testvbox = "lspci | grep -iq virtualbox"
    if os.system(testkvm) == 0 or os.system(testvbox) == 0:
        return True
    else:
        return False


def add_to_fstab(label, uuid, mntpoint, fstype, options):
    """Add partition to fstab"""

    mntline = f"\n#{label}\n"
    mntline += f"UUID={uuid}\t{mntpoint}\t{fstype}\t{options}\t0\t0"

    with open("/etc/fstab", "a+") as f:
        if label not in f.read():
            f.write(mntline)
