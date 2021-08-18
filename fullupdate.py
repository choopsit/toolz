#!/usr/bin/env python3

import sys
import os
import re
import socket
import datetime
import time
import pathlib

__description__ = "Do a full upgrade conclued by system informations"
__author__ = "Choops <choopsbd@gmail.com>"


def usage():
    myscript = f"{os.path.basename(__file__)}"
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {myscript} [OPTION]")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help:           Print this help")
    print(f"  -o,--clean-obsolete: Remove local and obsolete packages")
    print()


def system_upgrade(rmobs):
    print(f"{ci}System upgrade{c0}:")
    os.system("sudo apt update >/dev/null 2>&1")
    os.system("sudo apt full-upgrade 2>/dev/null")

    rcpkgs = os.popen("dpkg -l | awk '/^rc/ {print $2}'").read()
    rcpkgsl = ""
    for pkg in rcpkgs.split("\n"):
        rcpkgsl += pkg.split(":")[0]
    if rcpkgsl != "":
        os.system(f"sudo apt purge {rcpkgsl} 2>/dev/null")

    if rmobs:
        getobs = "apt list ?obsolete 2>/dev/null | "
        getobs += "awk  -F'/' '/\/now/ {print $1}'"
        obspkgs = os.popen(getobs).read()
        obspkgsl = ""
        for pkg in obspkgs.split("\n"):
            obspkgsl += pkg.split(":")[0]
        if obspkgsl != "":
            os.system(f"sudo apt purge -y {obspkgsl} 2>/dev/null")

    cleancmds = ["sudo apt autoremove --purge 2>/dev/null",
                 "sudo apt autoclean 2>/dev/null",
                 "sudo apt clean 2>/dev/null"]
    for cmd in cleancmds:
        os.system(cmd)

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
        #if socket.gethostname() == "mrchat":
        #    folder = "/volumes/backup"

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
    scripts = {"pyfetch": "", "tsm": "-t", "vbox": "list", "pydf": ""}

    for script, opt in scripts.items():
        if os.path.exists(f"{binpath}/{script}"):
            cmd = f"{script} {opt}"
            os.system(cmd.rstrip())

    if os.path.exists("/usr/local/bin/statmygits"):
        show_git_status(repopath)


c0 = "\33[0m"
ce = "\33[31m"
ci = "\33[36m"

error = f"{ce}E{c0}:"

if __name__ == "__main__":
    cleanobs = False
    home = pathlib.Path.home()

    if len(sys.argv) > 1:
        if re.match('^-(h|-help)$', sys.argv[1]):
            usage()
            exit(0)
        elif re.match('^-(o|-clean-obsolete)$', sys.argv[1]):
            cleanobs = True
        else:
            print(f"{error} Bad argument")
            usage()
            exit(1)

    system_upgrade(cleanobs)
    themes_upgrade()
    user_conf_backup()
    system_informations(home)
