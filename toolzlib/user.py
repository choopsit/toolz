#!/usr/bin/env python3

import os
import toolzlib

__description__ = "User management functions module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"
info = f"{ci}I{c0}:"


def get_list():
    """List users having their home directory at '/home/{user}'"""

    userslist = []
    potential_users = os.listdir("/home")
    for user in potential_users:
        with open("/etc/passwd") as f:
            for line in f:
                if line.startswith(f"{user}:"):
                    userslist.append(user)

    return userslist


def is_in_group(user, grp):
    """Check if user '{user}' is in group '{grp}'"""

    ret = False

    grplist = os.popen(f"groups {user}").read()
    if grp in grplist:
        ret = True

    return ret


def add_to_group(user, grp):
    """Add '{user}' to group '{grp}'"""
    
    if toolzlib.yesno(f"Add '{user}' to '{grp}'", "y"):
        os.system(f"adduser {user} {grp}")


def is_sudo():
    """Check if script is launched as 'root' or using 'sudo'"""

    ret = False

    if os.getuid() == 0:
        ret = True

    return ret
