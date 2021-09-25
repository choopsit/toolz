#!/usr/bin/env python3

import sys
import os
import re
import socket
import datetime
import time
import pathlib
import toolz

__description__ = "Do a full upgrade conclued by system informations"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def usage(err_code=0):
    my_script = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {my_script} [OPTION]")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help:           Print this help")
    print(f"  -o,--clean-obsolete: Remove local and obsolete packages")
    print()
    exit(err_code)


def system_upgrade(rm_obs):
    print(f"{ci}System upgrade{c0}:")

    toolz.pkg.upgrade()

    if rm_obs:
        toolz.pkg.rm_obsoletes()

    toolz.pkg.clean()

    for file in os.listdir(home):
        if file.startswith(".xsession"):
            os.remove(f"{home}/{file}")

    print()


def themes_upgrade():
    if os.path.exists("/usr/local/bin/themesupdate"):
        print(f"{ci}Themes upgrade{c0}:")

        os.system("sudo themesupdate")


def user_conf_backup():
    do_backup = True

    if os.path.exists("/usr/local/bin/backup"):
        print(f"{ci}Backup{c0}:")

        folder = "/backup"

        if os.system(f"mount | grep -q {folder}") != 0:
            do_backup = False

            print(f"{error} '{folder}' not mounted\n")
    else:
        do_backup = False

    if do_backup:
        os.system(f"backup {folder}")


def show_git_status(folder):
    for mygit in os.listdir(folder):
        if os.path.isdir(f"{folder}/{mygit}/.git"):
            print(f"{ci}Git repos status{c0}:")

            os.system(f"statmygits {folder}")

            break


def system_informations(home):
    repo_path = f"{home}/Work/git"

    print(f"{ci}System informations{c0}:")
    print(datetime.datetime.today().strftime("%a %b %d, %H:%M:%S"))

    bin_path = "/usr/local/bin"
    scripts = {"pyfetch": "", "tsm": "-t", "pydf": ""}

    if not toolz.pkg.is_installed("transmission-daemon"):
        scripts.pop("tsm", None)

    for script, opt in scripts.items():
        if os.path.exists(f"{bin_path}/{script}"):
            cmd = f"{script} {opt}"

            os.system(cmd.rstrip())

    if os.path.exists("/usr/local/bin/statmygits") and \
            os.path.isdir(repo_path):
        show_git_status(repo_path)


if __name__ == "__main__":
    rm_obs = False
    home = pathlib.Path.home()

    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) == 2 and sys.argv[1] in ["-o","--clean-obsolete"]:
        rm_obs = True
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument\n")
        usage(1)

    system_upgrade(rm_obs)
    themes_upgrade()
    user_conf_backup()
    system_informations(home)
