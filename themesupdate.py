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


def usage(err_code=0):
    my_script = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  '{my_script} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(err_code)


def vinceliuice_theme(th_name, color=None):
    tmp_folder = "/tmp"

    th_url = f"https://github.com/vinceliuice/{th_name}.git"
    th_folder = os.path.join(tmp_folder, th_name)
    toolz.git.update(th_url, th_folder)

    th_inst_cmd = [os.path.join(th_folder, "install.sh")]

    if "gtk" in th_name:
        req_pkgs = ["gtk2-engines-murrine", "gtk2-engines-pixbuf",
                "libglib2.0-dev"]

        toolz.pkg.prerequisites(req_pkgs)

        if color in ["dark", "light"]:
            th_inst_cmd += ["-c", color]
        elif color:
            print(f"{error} Invalid color\n")
            exit(1)

    subprocess.call(th_inst_cmd, stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL)

    print(f"{done} {th_name} updated")


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

    print(f"{ci}Themes upgrade{c0}:")
    gtk_themes = ["Mojave-gtk-theme"]
    #gtk_themes = ["WhiteSur-gtk-theme"]
    #gtk_themes = ["WhiteSur-gtk-theme", "Mojave-gtk-theme"]
    for gtk_th in gtk_themes:
        vinceliuice_theme(gtk_th, "dark")

    #icon_themes = ["WhiteSur-icon-theme"]
    #for icon_th in icon_themes:
    #    vinceliuice_theme(icon_th)

    cursor_themes = ["McMojave-cursors"]
    #cursor_themes = ["WhiteSur-cursors"]
    #cursor_themes = ["WhiteSur-cursors", "McMojave-cursors"]
    for curs_th in cursor_themes:
        vinceliuice_theme(curs_th)

    print()
