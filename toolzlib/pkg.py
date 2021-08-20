#!/usr/bin/env python3

import os
import shutil
from . import file
from . import sys
from . import user

__description__ = "Package management module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def update_sourceslist(distro):
    """Add contrib and non-free branches to Debian repos"""

    if distro == "debian":
        sourceslist = "/etc/apt/sources.list"
        tmpfile = "/tmp/sources.list"

        file.overwrite(sourceslist, tmpfile)
        with open(tmpfile, "r") as oldf, open(sourceslist, "w") as tmpf:
            for line in oldf:
                okline = True
                if "cdrom" in line or line == "#\n" or line.isspace():
                    okline = False

                if okline:
                    lineend = ""
                    if line.endswith("main\n"):
                        lineend = " contrib non-free"
                    tmpf.write(f"{line.strip()}{lineend}\n")


def is_installed(pkg):
    """Check if a package is installed"""

    instpkgs = []
    listpkgs_cmd = f"dpkg -l | grep ^ii"
    listpkgs = os.popen(listpkgs_cmd)

    for line in listpkgs:
        instpkg = line.split()[1]
        if instpkg.endswith(':amd64'):
            instpkg = instpkg.replace(':amd64','')
        instpkgs.append(instpkg)

    if pkg in instpkgs:
        return True
    else:
        return False


def install(pkgs, forceyes=False):
    """Install a list of packages"""

    high = "" if user.is_sudo() else "sudo "
    fyes = " -y" if forceyes else ""

    cmds = []
    cmds.append(f"{high}{srcupdate}")
    cmds.append(f"{high}{pkginstall}{fyes} {' '.join(pkgs)}")

    for cmd in cmds:
        os.system(cmd)


def remove(pkgs, forceyes=False):
    """Remove a list of packages"""

    high = "" if user.is_sudo() else "sudo "
    fyes = " -y" if forceyes else ""

    os.system(f"{high}{pkgremove}{fyes} {' '.join(pkgs)}")


def purge(pkgs, forceyes=False):
    """Purge a list of packages"""

    high = "" if user.is_sudo() else "sudo "
    fyes = " -y" if forceyes else ""

    cmds = []
    cmds.append(f"{high}{pkgpurge}{fyes} {' '.join(pkgs)}")
    cmds.append(f"{high}{unneededremove}{fyes}")

    for cmd in cmds:
        os.system(cmd)


def rm_obsoletes():
    """emove obsolete packages"""

    getobs = f"apt list ?obsolete 2>/dev/null | "
    getobs += "awk  -F'/' '/\/now/ {print $1}'"
    obsout = os.popen(getobs).read()
    obspkgs = [ pkg.split(":")[0] for pkg in obsout.split("\n") ]

    if obspkgs:
        purge(obspkgs)


def clean(forceyes=False):
    """Remove residual configurations and clean repo cache"""

    high = "" if user.is_sudo() else "sudo "
    fyes = " -y" if forceyes else ""

    rcpkgs = []
    listrcpkgs_cmd = f"dpkg -l | grep ^rc"
    listrcpkgs = os.popen(listrcpkgs_cmd)

    for line in listrcpkgs:
        rcpkgs.append(line.split()[1])

    cmds = []
    if rcpkgs != []:
        cmds.append(f"{high}{pkgpurge}{fyes} {' '.join(rcpkgs)}")
    cmds.append(f"{high}{unneededremove}{fyes}")
    cmds.append(f"{high}{srcsoftclean}")
    cmds.append(f"{high}{srcclean}")

    for cmd in cmds:
        os.system(cmd)


def upgrade(forceyes=False):
    """Upgrade distro"""

    high = "" if user.is_sudo() else "sudo "
    fyes = " -y" if forceyes else ""

    cmds = []
    cmds.append(f"{high}{srcupdate}")
    cmds.append(f"{high}{fullupgrade}{fyes}")

    for cmd in cmds:
        os.system(cmd)


distro = sys.get_distro()
debianderivatives = ["debian", "ubuntu", "linuxmint"]

if distro in debianderivatives:
    srcupdate = "apt update"
    srcsoftclean = "apt autoclean 2>/dev/null"
    srcclean = "apt clean 2>/dev/null"

    fullupgrade = "apt full-upgrade"
    unneededremove = "apt autoremove --purge"

    pkginstall = "apt install"
    pkgremove = "apt remove"
    pkgpurge = "apt purge"

    listpkgs = "dpkg -l | grep ^ii"
    listresidualconf = f"dpkg -l | grep ^rc"
else:
    print(f"{error} Unsupported distribution '{distro}'")
