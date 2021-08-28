#!/usr/bin/env python3

import sys
import os
import re
import socket
import datetime
import time
import pathlib
import toolzlib

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


def usage(errcode=0):
    myscript = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {myscript} [OPTION]")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help:           Print this help")
    print(f"  -o,--clean-obsolete: Remove local and obsolete packages")
    print()
    exit(errcode)


def system_upgrade(rmobs):
    print(f"{ci}System upgrade{c0}:")

    sudo = ""
    if not toolzlib.user.is_sudo():
        sudo = "sudo "

    toolzlib.pkg.upgrade()

    if rmobs:
        toolzlib.pkg.rm_obsoletes()

    toolzlib.pkg.clean()

    for file in os.listdir(home):
        if file.startswith(".xsession"):
            os.remove(f"{home}/{file}")

    print()


def themes_upgrade():
    if os.path.exists("/usr/local/bin/themesupdate"):
        print(f"{ci}Themes upgrade{c0}:")
        os.system("sudo themesupdate")


def user_conf_backup():
    dobackup = True

    if os.path.exists("/usr/local/bin/backup"):
        print(f"{ci}Backup{c0}:")

        folder = "/backup"

        if os.system(f"mount | grep -q {folder}") != 0:
            dobackup = False
            print(f"{error} '{folder}' not mounted\n")
    else:
        dobackup = False

    if dobackup:
        os.system(f"backup {folder}")


def show_git_status(folder):
    for mygit in os.listdir(folder):
        if os.path.isdir(f"{folder}/{mygit}/.git"):
            print(f"{ci}Git repos status{c0}:")
            os.system(f"statmygits {folder}")
            break


def system_informations(home):
    repopath = f"{home}/Work/git"

    print(f"{ci}System informations{c0}:")
    print(datetime.datetime.today().strftime("%a %b %d, %H:%M:%S"))
    binpath = "/usr/local/bin"
    userbin = f"{home}/.local/bin"
    scripts = {"pyfetch": "", "tsm": "-t", "pydf": ""}

    if not toolzlib.pkg.is_installed("transmission-daemon"):
        scripts.pop("tsm", None)

    for script, opt in scripts.items():
        if os.path.exists(f"{binpath}/{script}"):
            cmd = f"{script} {opt}"
            os.system(cmd.rstrip())

    if os.path.exists("/usr/local/bin/statmygits"):
        show_git_status(repopath)


if __name__ == "__main__":
    cleanobs = False
    home = pathlib.Path.home()

    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) == 2 and sys.argv[1] in ["-o","--clean-obsolete"]:
        cleanobs = True
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument\n")
        usage(1)

    system_upgrade(cleanobs)
    themes_upgrade()
    user_conf_backup()
    system_informations(home)
