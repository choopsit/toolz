#!/usr/bin/env python3

import sys
import os
import shutil
import re
import subprocess
import datetime
import socket
import pathlib
import getpass
import toolzlib

__description__ = "Backup important files and folders from home folder and \
some configuration files"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def usage(errcode):
    myscript = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {myscript} [OPTION] <BACKUP_FOLDER>")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(errcode)


def test_backupfolder(folder):
    forbiddens = ["/", "/bin", "/boot", "/dev", "/etc", "/home", "/initrd.img",
                  "/initrd.img.old", "/lib", "/lib32", "/lib64", "/libx32",
                  "/media", "/mnt", "/opt", "/proc", "/root", "/run", "/srv",
                  "/sys", "/tmp", "/usr", "/var"]
    if folder in forbiddens:
        print(f"{error} Invalid folder '{folder}'\n")
        exit(1)

    okcreate=""
    if not os.path.exists(folder):
        print(f"{warning} '{folder}' does not exist yet")
        okcreate = input("Create it [Y/n] ? ")
        if re.match('^(n|no)', okcreate.lower()):
            exit(0)
        else:
            os.makedirs(folder)
            os.chmod(folder, 0o777)

    if not os.path.isdir(folder):
        print(f"{error} '{folder}' exists but is not a folder\n")
        exit(1)

    return True


def backup(destfolder):
    homebackups = [".profile", ".face", ".kodi", ".mozilla", ".vim", ".steam",
                   ".config/autostart", ".config/bash", ".config/conky",
                   ".config/dconf", ".config/evince", ".config/gedit",
                   ".config/GIMP", ".config/libvirt", ".config/Mousepad",
                   ".config/openvpn", ".config/plank", ".config/picom",
                   ".config/pitivi", ".config/remmina", ".config/terminator",
                   ".config/transmisson-daemon", ".config/Thunar",
                   ".config/xfce4", ".local/bin", ".local/share/applications",
                   ".local/share/fonts", ".local/share/gedit",
                   ".local/share/gtksourceview-3.0",
                   ".local/share/gtksourceview-4", ".local/share/lollypop",
                   ".local/share/plank", ".local/share/remmina",
                   ".local/share/rhythmbox", ".local/share/xfce4", "Documents",
                   "Music", "Pictures", "Videos", "Work", "Games"]
    cfgfiles = ["/etc/fstab", "/etc/exports", "/etc/hosts",
                "/etc/ssh/sshd_config", "/etc/sysctl.d/99-swappiness.conf",
                "/etc/pulse/daemon.conf", "/etc/apt/sources.list",
                "/usr/share/lightdm/lightdm.conf.d/01_my.conf",
                "/usr/share/X11/xorg.conf.d/10-nvidia.conf"]
    morebackups = []
    if socket.gethostname() == "mrchat":
        morebackups = ["/volumes/speedix/Music", "/volumes/speedix/Games"]

    today = datetime.datetime.today().strftime("%y%m")
    bkpfolder = f"{destfolder}/{today}_{socket.gethostname()}"

    if not os.path.exists(bkpfolder):
        os.makedirs(bkpfolder)

    myuser = getpass.getuser()
    myhome = pathlib.Path.home()

    rsynccmd = "rsync -qOatzulr --delete --exclude='*~'"

    errhome = 0
    for bkpelement in homebackups:
        bkpsrc = f"{myhome}/{bkpelement}"
        if os.path.exists(bkpsrc):
            bkpsubfolder = os.path.dirname(bkpsrc)
            if not os.path.exists(f"{bkpfolder}{bkpsubfolder}"):
                os.makedirs(f"{bkpfolder}{bkpsubfolder}")
            bkpdst = f"{bkpfolder}/{bkpsubfolder}"
            bkp_cmd = f"{rsynccmd} {bkpsrc} {bkpdst}"
            if os.system(bkp_cmd) != 0:
                errhome += 1
    if errhome == 0:
        ecol = "\33[32m"
    else:
        ecol = "\33[31m"

    print(f"{done} {myuser}'s home backuped in '{bkpfolder}{myhome}'", end=" ")
    print(f"with {ecol}{errhome}{c0} error(s)")

    errcfg = 0
    for bkpsrc in cfgfiles:
        if os.path.exists(bkpsrc):
            bkpsubfolder = os.path.dirname(bkpsrc)
            if not os.path.exists(f"{bkpfolder}{bkpsubfolder}"):
                os.makedirs(f"{bkpfolder}{bkpsubfolder}")
            bkpdst = f"{bkpfolder}/{bkpsubfolder}"
            bkp_cmd = f"{rsynccmd} {bkpsrc} {bkpdst}"
            if os.system(bkp_cmd) != 0:
                errcfg += 1
    if errcfg == 0:
        ecol = "\33[32m"
    else:
        ecol = "\33[31m"

    print(f"{done} Config files backuped in '{bkpfolder}'", end=" ")
    print(f"with {ecol}{errcfg}{c0} error(s)")

    for bkpsrc in morebackups:
        if os.path.exists(bkpsrc):
            errother = 0
            ecol = "\33[32m"
            bkpsubfolder = os.path.dirname(bkpsrc)
            if not os.path.exists(f"{bkpfolder}{bkpsubfolder}"):
                os.makedirs(f"{bkpfolder}{bkpsubfolder}")
            bkpdst = f"{bkpfolder}{bkpsubfolder}"
            bkp_cmd = f"{rsynccmd} {bkpsrc} {bkpdst}"
            if os.system(bkp_cmd) != 0:
                errother += 1
            if errother != 0:
                ecol = "\33[31m"
            print(f"{done} '{bkpsrc}' backuped in '{bkpfolder}'", end=" ")
            print(f"with {ecol}{errother}{c0} error(s)")

    print()


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) == 1:
        print(f"{error} Need an argument\n")
        usage(1)
    elif len(sys.argv) == 2 and test_backupfolder(sys.argv[1]):
        reqpkgs = ["rsync"]
        toolzlib.prerequisites(reqpkgs)
        backup(sys.argv[1])
    else:
        print(f"{error} Bad argument\n")
        usage(1)
