#!/usr/bin/env python3

import os
import shutil

from . import file
from . import syst
from . import user
from .base import yesno

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
                    if line.endswith(" main\n"):
                        lineend = " contrib non-free"
                    tmpf.write(f"{line.strip()}{lineend}\n")


def is_installed(pkg):
    """Check if a package is installed"""

    inst_pkgs = []
    list_pkgs_cmd = f"dpkg -l | grep ^ii"
    list_pkgs = os.popen(list_pkgs_cmd)

    for line in list_pkgs:
        inst_pkg = line.split()[1]
        if inst_pkg.endswith(':amd64'):
            inst_pkg = inst_pkg.replace(':amd64','')

        inst_pkgs.append(inst_pkg)

    return pkg in inst_pkgs


def install(pkgs, force_yes=False):
    """Install a list of packages"""

    high = "" if user.is_sudo() else "sudo "
    force_yes_opt = " -y" if force_yes else ""

    cmds = []
    cmds.append(f"{high}{src_update}")
    cmds.append(f"{high}{pkg_install}{force_yes_opt} {' '.join(pkgs)}")

    for cmd in cmds:
        os.system(cmd)


def remove(pkgs, force_yes=False):
    """Remove a list of packages"""

    high = "" if user.is_sudo() else "sudo "
    force_yes_opt = " -y" if force_yes else ""

    os.system(f"{high}{pkg_remove}{force_yes_opt} {' '.join(pkgs)}")


def purge(pkgs, force_yes=False):
    """Purge a list of packages"""

    high = "" if user.is_sudo() else "sudo "
    force_yes_opt = " -y" if force_yes else ""

    cmds = []
    cmds.append(f"{high}{pkg_purge}{force_yes_opt} {' '.join(pkgs)}")
    cmds.append(f"{high}{unneeded_remove}{force_yes_opt}")

    for cmd in cmds:
        os.system(cmd)


def rm_obsoletes():
    """Remove obsolete packages"""

    get_obs = f"apt list ?obsolete 2>/dev/null | "
    get_obs += "awk  -F'/' '/\/now/ {print $1}'"
    obs_out = os.popen(get_obs).read()
    obs_pkgs = [ pkg.split(":")[0] for pkg in obs_out.split("\n") ]

    if obs_pkgs:
        purge(obs_pkgs)


def clean(force_yes=False):
    """Remove residual configurations and clean repo cache"""

    high = "" if user.is_sudo() else "sudo "
    force_yes_opt = " -y" if force_yes else ""

    rc_pkgs = []
    list_rc_pkgs_cmd = f"dpkg -l | grep ^rc"
    list_rc_pkgs = os.popen(list_rc_pkgs_cmd)

    for line in list_rc_pkgs:
        rc_pkgs.append(line.split()[1])

    cmds = []
    if rc_pkgs != []:
        cmds.append(f"{high}{pkg_purge}{force_yes_opt} {' '.join(rc_pkgs)}")
    cmds.append(f"{high}{unneeded_remove}{force_yes_opt}")
    cmds.append(f"{high}{src_soft_clean}")
    cmds.append(f"{high}{src_clean}")

    for cmd in cmds:
        os.system(cmd)


def upgrade(force_yes=False):
    """Upgrade distro"""

    high = "" if user.is_sudo() else "sudo "
    force_yes_opt = " -y" if force_yes else ""

    cmds = []
    cmds.append(f"{high}{src_update}")
    cmds.append(f"{high}{fullupgrade}{force_yes_opt}")

    for cmd in cmds:
        os.system(cmd)


def prerequisites(req_pkgs):
    """Install needed packages if not already installed"""

    missing_pkgs = []
    for req_pkg in req_pkgs:
        if not is_installed(req_pkg):
            missing_pkgs.append(req_pkg)

    if missing_pkgs:
        print(f"{warning} Missing package(s): {', '.join(missing_pkgs)}")
        p_count = "it"

        if len(missing_pkgs) > 1:
            p_count = "them"

        if user.is_sudo():
            if yesno(f"Install {p_count}"):
                install(req_pkgs, True)
            else:
                exit(1)
        else:
            exit(1)

        for req_pkg in missing_pkgs:
            if not is_installed(req_pkg):
                print(f"{error} Needed package not installed\n")
                exit(1)


distro = syst.get_distro()
debian_derivatives = ["debian", "ubuntu"]

if distro in debian_derivatives:
    src_update = "apt update"
    src_soft_clean = "apt autoclean 2>/dev/null"
    src_clean = "apt clean 2>/dev/null"

    fullupgrade = "apt full-upgrade"
    unneeded_remove = "apt autoremove --purge"

    pkg_install = "apt install"
    pkg_remove = "apt remove"
    pkg_purge = "apt purge"

    list_pkgs = "dpkg -l | grep ^ii"
    list_residual_conf = f"dpkg -l | grep ^rc"
else:
    print(f"{error} Unsupported distribution '{distro}'")
    exit(1)
