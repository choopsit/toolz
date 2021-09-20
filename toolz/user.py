#!/usr/bin/env python3

import os

from .base import yesno

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

    users_list = []
    potential_users = os.listdir("/home")

    for user in potential_users:
        with open("/etc/passwd") as f:
            for line in f:
                if line.startswith(f"{user}:"):
                    users_list.append(user)

    return users_list


def is_in_group(user, grp):
    """Check if user '{user}' is in group '{grp}'"""

    grp_list = os.popen(f"groups {user}").read()
    if grp in grp_list:
        return True

    return False


def add_to_group(user, grp):
    """Add '{user}' to group '{grp}'"""

    if yesno(f"Add '{user}' to '{grp}'", "y"):
        os.system(f"adduser {user} {grp}")


def is_sudo():
    """Check if script is launched as 'root' or using 'sudo'"""

    return os.getuid() == 0
