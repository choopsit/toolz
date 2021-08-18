#!/usr/bin/env python3

import os
import shutil
from . import file
from . import sys

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


def install(pkgs):
    """Install a list of packages"""

    cmds = []
    cmds.append(srcupdate)
    cmds.append(f"{pkginstall} {' '.join(pkgs)}")

    for cmd in cmds:
        os.system(cmd)


def remove(pkgs):
    """Remove a list of packages"""

    os.system(f"{pkgremove} {' '.join(pkgs)}")


def purge(pkgs):
    """Purge a list of packages"""

    cmds = []
    cmds.append(f"{pkgpurge} {' '.join(pkgs)}")
    cmds.append(unneededremove)

    for cmd in cmds:
        os.system(cmd)


def clean():
    """Remove residual configurations and clean repo cache"""

    rcpkgs = []
    listrcpkgs_cmd = f"dpkg -l | grep ^rc"
    listrcpkgs = os.popen(listrcpkgs_cmd)

    for line in listrcpkgs:
        rcpkgs.append(line.split()[1])

    if rcpkgs != []:
        os.system(f"{pkgpurge} {' '.join(rcpkgs)}")

    os.system(unneededremove)
    os.system(srcsoftclean)
    os.system(srcclean)


def upgrade():
    """Upgrade distro"""

    os.system(srcupdate)
    os.system(fullupgrade)


distro = sys.get_distro()
debianderivatives = ["debian", "ubuntu", "linuxmint"]

if distro in debianderivatives:
    srcupdate = "apt update"
    srcsoftclean = "apt autoclean 2>/dev/null"
    srcclean = "apt clean 2>/dev/null"

    fullupgrade = "apt full-upgrade -y"
    unneededremove = "apt autoremove --purge -y"

    pkginstall = "apt install -y"
    pkgremove = "apt remove -y"
    pkgpurge = "apt purge -y"

    listpkgs = "dpkg -l | grep ^ii"
    listresidualconf = f"dpkg -l | grep ^rc"
else:
    print(f"{error} Unsupported distribution '{distro}'")
