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
    myscript = f"{os.path.basename(__file__)}"
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {myscript} [OPTION] <BACKUP_FOLDER>")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(errcode)


def is_sudoer():
    sudoer = False
    if os.getuid() != 0:
        listgrp_cmd = ['groups']
        issudo_cmd = ['grep', 'sudo']
        listgrp = subprocess.Popen(listgrp_cmd, stdout=subprocess.PIPE)
        try:
            subprocess.check_output(issudo_cmd, stdin=listgrp.stdout)
            sudoer = True
        except subprocess.CalledProcessError:
            print(f"{error} Cannot install requisite package(s).", end=" ")
            print("Need higher privileges.")
            exit(1)

    return sudoer


def prerequisites():
    reqpkgs = ["rsync"]
    missingpkg = False
    for pkg in reqpkgs:
        pkglist_cmd = ["dpkg", "-l"]
        filter_cmd = ["grep", pkg]
        pkglist = subprocess.Popen(pkglist_cmd, stdout=subprocess.PIPE)
        try:
            subprocess.check_output(filter_cmd, stdin=pkglist.stdout,
                                    universal_newlines=True).rstrip("\n")
        except subprocess.CalledProcessError:
            missingpkg = True

    if missingpkg:
        if is_sudoer():
            install = "sudo apt-get install"
        else:
            install = "apt-get install"
        print(f"{ci}Installing required packages...{c0}")
        inst_cmd = f"{install} -yy {' '.join(reqpkgs)}"
        os.system(inst_cmd)


def test_backupfolder(folder):
    forbiddens = ["/", "/bin", "/boot", "/dev", "/etc", "/home", "/initrd.img",
                  "/initrd.img.old", "/lib", "/lib32", "/lib64", "/libx32",
                  "/media", "/mnt", "/opt", "/proc", "/root", "/run", "/srv",
                  "/sys", "/tmp", "/usr", "/var"]
    if folder in forbiddens:
        print(f"{error} Invalid folder '{folder}'")
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
        print(f"{error} '{folder}' exists but is not a folder")
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
        morebackups = ["/volumes/speedix/Music"]

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

    errother = 0
    morebkpl = []
    for bkpsrc in morebackups:
        if os.path.exists(bkpsrc):
            morebkpl.append(bkpsrc)
            bkpsubfolder = os.path.dirname(bkpsrc)
            if not os.path.exists(f"{bkpfolder}{bkpsubfolder}"):
                os.makedirs(f"{bkpfolder}{bkpsubfolder}")
            bkpdst = f"{bkpfolder}{bkpsubfolder}"
            bkp_cmd = f"{rsynccmd} {bkpsrc} {bkpdst}"
            if os.system(bkp_cmd) != 0:
                errother += 1
    if errother == 0:
        ecol = "\33[32m"
    else:
        ecol = "\33[31m"

    if morebkpl != []:
        morebkp = "\, '".join(morebkpl)
        print(f"{done} '{morebkp}' backuped in '{bkpfolder}'", end=" ")
        print(f"with {ecol}{errother}{c0} error(s)")

    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if re.match('^-(h|-help)$', sys.argv[1]):
            usage(0)
        elif test_backupfolder(sys.argv[1]):
            backup(sys.argv[1])
        else:
            print(f"{error} Bad argument\n")
            usage(1)
    else:
        print(f"{error} Need an argument\n")
        usage(1)
