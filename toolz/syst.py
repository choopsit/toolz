#!/usr/bin/env python3

import os

from .base import yesno

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

    if not yesno("Reboot now", "y"):
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
        print(f"{error} OS is not Debian\n")
        exit(1)

    olddebian = ["buster", "stretch", "jessie", "wheezy", "squeeze", "lenny"]
    codename = get_codename()
    if codename in olddebian:
        print(f"{error} '{codename}' is a too old Debian version\n")
        exit(1)

    if os.getuid() != 0:
        print(f"{error} Need higher privileges\n")
        exit(1)


def is_vm():
    """Check if machine is virtual"""

    testkvm = "lspci | grep -q paravirtual"
    testvbox = "lspci | grep -iq virtualbox"

    return os.system(testkvm) == 0 or os.system(testvbox) == 0


def add_to_fstab(label, uuid, mntpoint, fstype, options):
    """Add partition to fstab"""

    mntline = f"\n#{label}\n"
    mntline += f"UUID={uuid}\t{mntpoint}\t{fstype}\t{options}\t0\t0"

    with open("/etc/fstab", "a+") as f:
        if label not in f.read():
            f.write(mntline)


def is_valid_hostname(hostname):
    """Check validity of a string to be used as hostname"""

    if len(hostname) > 255:
        return False

    if hostname[-1] == ".":
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)

    return all(allowed.match(x) for x in hostname.split("."))


def decompose_fqdn(fqdn):
    """Split FQDN in hostname and domain"""

    hostname = fqdn.split(".")[0]
    domain = ".".join(fqdn.split(".")[1:])

    return hostname, domain


def set_hostname():
    """Define a machine hostname"""

    fqdn = socket.getfqdn()
    if yesno(f"Keep current hostname: '{fqdn}'", "y"):
        hostname, domain = decompose_fqdn(fqdn)
    else:
        newhostname = input("New hostname (or FQDN) ? ")
        if newhostname == "":
            print(f"{error} No hostname given")
            hostname, domain = set_hostname()
        elif is_valid_hostname(newhostname):
            hostname, domain = decompose_fqdn(newhostname)
        else:
            print(f"{error} Invalid hostname '{newhostname}'")
            hostname, domain = set_hostname()

    return hostname, domain


def renew_hostname(fqdn):
    """Apply machine naming"""

    hostname, domain = decompose_fqdn(fqdn)

    with open("/etc/hostname", "w") as f:
        f.write(f"{hostname}\n")

    hostline = f"127.0.1.1\t{hostname}"
    if domain != "":
        hostline += f".{domain}\t{hostname}"

    file.overwrite("/etc/hosts", "/tmp/hosts")
    with open("/tmp/hosts", "r") as oldf, open("/etc/hosts", "w") as newf:
        for line in oldf:
            if line.startswith("127.0.1.1"):
                newf.write(hostline)
            else:
                newf.write(line)

    os.system(f"hostname {hostname}")


def list_users():
    """List users having their home directory at '/home/{user}'"""

    userslist = []
    potential_users = os.listdir("/home")
    for user in potential_users:
        with open("/etc/passwd") as f:
            for line in f:
                if line.startswith(f"{user}:"):
                    userslist.append(user)

    return userslist
