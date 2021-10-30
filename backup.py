#!/usr/bin/env python3

import sys
import os
import shutil
import subprocess
import datetime
import socket
import pathlib
import getpass
import toolz

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


def usage(err_code=0):
    my_script = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {my_script} [OPTION] <BACKUP_FOLDER>")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(err_code)


def test_backupfolder(folder):
    forbiddens = ["/", "/bin", "/boot", "/dev", "/etc", "/home", "/initrd.img",
            "/initrd.img.old", "/lib", "/lib32", "/lib64", "/libx32", "/media",
            "/mnt", "/opt", "/proc", "/root", "/run", "/srv", "/sys", "/tmp",
            "/usr", "/var"]

    if folder in forbiddens:
        print(f"{error} Invalid folder '{folder}'\n")
        exit(1)

    okcreate=""

    if not os.path.exists(folder):
        print(f"{warning} '{folder}' does not exist yet")
        okcreate = input("Create it [Y/n] ? ")

        if okcreate.lower() in ["n", "no"]:
            exit(0)
        else:
            os.makedirs(folder)
            os.chmod(folder, 0o777)

    if not os.path.isdir(folder):
        print(f"{error} '{folder}' exists but is not a folder\n")
        exit(1)

    return True


def backup(dest_folder):
    home_backups = [".profile", ".face", ".kodi", ".mozilla", ".vim", ".steam",
            ".config/autostart", ".config/bash", "BraveSoftware",
            ".config/dconf", ".config/evince", ".config/GIMP",
            ".config/libvirt", ".config/Mousepad", ".config/openvpn",
            ".config/plank", ".config/terminator", ".config/transmisson-daemon",
            ".config/Thunar", ".config/xfce4", ".local/bin",
            ".local/share/applications", ".local/share/fonts",
            ".local/share/gtksourceview-3.0", ".local/share/gtksourceview-4",
            ".local/share/lollypop", ".local/share/plank",
            ".local/share/rhythmbox", ".local/share/xfce4", "Documents",
            "Music", "Pictures", "Videos", "Work", "Games"]

    cfg_files = ["/etc/fstab", "/etc/exports", "/etc/hosts",
            "/etc/ssh/sshd_config", "/etc/sysctl.d/99-swappiness.conf",
            "/etc/pulse/daemon.conf", "/etc/apt/sources.list",
            "/usr/share/lightdm/lightdm.conf.d/01_my.conf",
            "/usr/share/X11/xorg.conf.d/10-nvidia.conf"]

    more_backups = []

    if socket.gethostname() == "mrchat":
        more_backups = ["/volumes/speedix/Music", "/volumes/speedix/Games"]

    today = datetime.datetime.today().strftime("%y%m")
    bkp_folder = f"{dest_folder}/{today}_{socket.gethostname()}"

    if not os.path.exists(bkp_folder):
        os.makedirs(bkp_folder)

    my_user = getpass.getuser()
    my_home = pathlib.Path.home()

    rsync_cmd = "rsync -qOatzulr --delete --exclude='*~'"

    err_home = 0

    for bkp_element in home_backups:
        bkp_src = f"{my_home}/{bkp_element}"

        if os.path.exists(bkp_src):
            bkp_subfolder = os.path.dirname(bkp_src)

            if not os.path.exists(f"{bkp_folder}{bkp_subfolder}"):
                os.makedirs(f"{bkp_folder}{bkp_subfolder}")

            bkp_dst = f"{bkp_folder}/{bkp_subfolder}"
            bkp_cmd = f"{rsync_cmd} {bkp_src} {bkp_dst}"

            if os.system(bkp_cmd) != 0:
                err_home += 1

    if err_home == 0:
        ecol = "\33[32m"
    else:
        ecol = "\33[31m"

    home_bkp_ret = f"{done} {my_user}'s home backuped in '{bkp_folder}"
    home_bkp_ret += f"{my_home}' with {ecol}{err_home}{c0} error(s)"
    
    print(home_bkp_ret)

    err_cfg = 0

    for bkp_src in cfg_files:
        if os.path.exists(bkp_src):
            bkp_subfolder = os.path.dirname(bkp_src)

            if not os.path.exists(f"{bkp_folder}{bkp_subfolder}"):
                os.makedirs(f"{bkp_folder}{bkp_subfolder}")

            bkp_dst = f"{bkp_folder}/{bkp_subfolder}"
            bkp_cmd = f"{rsync_cmd} {bkp_src} {bkp_dst}"

            if os.system(bkp_cmd) != 0:
                err_cfg += 1

    if err_cfg == 0:
        ecol = "\33[32m"
    else:
        ecol = "\33[31m"

    cfg_bkp_ret = f"{done} Config files backuped in '{bkp_folder}' with "
    cfg_bkp_ret += f"{ecol}{err_cfg}{c0} error(s)"

    print(cfg_bkp_ret)

    for bkp_src in more_backups:
        if os.path.exists(bkp_src):
            err_other = 0
            ecol = "\33[32m"
            bkp_subfolder = os.path.dirname(bkp_src)

            if not os.path.exists(f"{bkp_folder}{bkp_subfolder}"):
                os.makedirs(f"{bkp_folder}{bkp_subfolder}")

            bkp_dst = f"{bkp_folder}{bkp_subfolder}"
            bkp_cmd = f"{rsync_cmd} {bkp_src} {bkp_dst}"

            if os.system(bkp_cmd) != 0:
                err_other += 1

            if err_other != 0:
                ecol = "\33[31m"

            more_bkp_ret = f"{done} '{bkp_src}' backuped in '{bkp_folder}'"
            more_bkp_ret += f"with {ecol}{err_other}{c0} error(s)"

            print(more_bkp_ret)

    print()


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) == 1:
        print(f"{error} Need an argument\n")
        usage(1)
    elif len(sys.argv) == 2 and test_backupfolder(sys.argv[1]):
        req_pkgs = ["rsync"]
        toolz.pkg.prerequisites(req_pkgs)
        backup(sys.argv[1])
    else:
        print(f"{error} Bad argument\n")
        usage(1)
