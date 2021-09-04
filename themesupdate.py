#!/usr/bin/env python3

import socket
import sys
import os
import subprocess
import shutil
import toolz

__description__ = "Update GTK themes and icon themes from github"
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
    print(f"  '{myscript} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(errcode)


def mojave_gtk(gitfolder):
    thurl = "https://github.com/vinceliuice/Mojave-gtk-theme.git"
    thfolder = f"{gitfolder}/mojave-gtk"
    toolz.git.update(thurl, thfolder)

    os.chdir(thfolder)
    thinst_cmd = ["./install.sh"]
    subprocess.check_output(thinst_cmd)

    print(f"{done} Mojave-Gtk theme updated")


def catalina_gtk():
    thname = "Os-Catalina-Gtk-night"
    thurl = f"https://github.com/zayronxio/{thname}.git"
    thtarget = f"/usr/share/themes/{thname}"
    toolz.git.update(thurl, thtarget)

    print(f"{done} {thname} theme updated")


def mcmojave_cursors(gitfolder):
    thurl = "https://github.com/vinceliuice/McMojave-cursors.git"
    thfolder = f"{gitfolder}/mcmojave-cursors"
    toolz.git.update(thurl, thfolder)

    os.chdir(thfolder)
    thinst_cmd = ["./install.sh"]
    subprocess.check_output(thinst_cmd)

    print(f"{done} McMojave cursors updated")


def obsidian_icons(gitfolder):
    thurl = "https://github.com/madmaxms/iconpack-obsidian.git"
    thfolder = f"{gitfolder}/obsidian-icons"
    toolz.git.update(thurl, thfolder)

    iconth = "Obsidian"
    mytarget = f"/usr/share/icons/{iconth}"
    mysource = f"{thfolder}/{iconth}"

    if os.path.isdir(mytarget):
        shutil.rmtree(mytarget)
    shutil.copytree(mysource, mytarget, symlinks=True)

    updcache_cmd = ["gtk-update-icon-cache", mytarget]
    subprocess.check_call(updcache_cmd, stderr=subprocess.DEVNULL)

    print(f"{done} Obsidian icons updated")


def fluent_icons(gitfolder):
    thurl = "https://github.com/vinceliuice/Fluent-icon-theme.git"
    thfolder = f"{gitfolder}/fluent-icons"
    toolz.git.update(thurl, thfolder)

    os.chdir(thfolder)
    thinst_cmd = ["./install.sh"]
    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(thinst_cmd, stdout=devnull,
                              stderr=subprocess.STDOUT)

    print(f"{done} Fluent icons updated")


def kora_icons(gitfolder):
    thurl = "https://github.com/bikass/kora.git"
    thfolder = f"{gitfolder}/kora-icons"
    toolz.git.update(thurl, thfolder)

    mytarget = f"/usr/share/icons/kora"
    mysource = f"{thfolder}/kora"

    if os.path.isdir(mytarget):
        shutil.rmtree(mytarget)
    shutil.copytree(mysource, mytarget, symlinks=True)

    updcache_cmd = ["gtk-update-icon-cache", mytarget]
    subprocess.check_call(updcache_cmd, stderr=subprocess.DEVNULL)

    print(f"{done} Kora icons updated")


if __name__ == "__main__":
    tmpfolder = "/tmp"

    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif os.getuid() != 0:
        print(f"{error} Need higher privileges\n")
        exit(1)
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument\n")
        exit(1)

    reqpkgs = ["sassc", "libcanberra-gtk-module", "libglib2.0-dev",
               "libxml2-utils"]
    toolz.pkg.prerequisites(reqpkgs)

    #mojave_gtk(tmpfolder)
    mcmojave_cursors(tmpfolder)
    catalina_gtk()
    #obsidian_icons(tmpfolder)
    #fluent_icons(tmpfolder)
    #kora_icons(tmpfolder)
    print()
