#!/usr/bin/env python3

import os
import sys
import socket
import toolz
from . import themesupdate

__description__ = "Install and configure a fully functional XFCE desktop"
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
    print()
    exit(errcode)


def specials():
    if hostname == "mrchat":
        disks ={
                "grodix": ["d498cab6-0d80-4b11-9c78-c422cc8ef983",
                    "/volume/grodix", "btrfs", "defaults"],
                "speedix": ["40b3c512-b22e-4842-b9e1-aa3262c4d1d8",
                    "/volumes/speedix", "btrfs", "defaults"],
                "backup": ["5a127881-4326-411d-a8a8-30d5b9271b12",
                    "/backup", "btrfs", "defaults,auto"]
                }

        for label, params in disks.items():
            part_line = f"#{label}\nUUID={params[0]}\t{params[1]}\t"
            part_line += f"{param[2]}\t{params[3]}\t0\t0\n"

            with open("/etc/fstab", "a+") as f:
                if label not in f.read():
                    f.write(part_line)

    else:
        pass


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif toolz.syst.get_distro()!= "debian":
        print(f"{error} OS is not Debian\n")                                     
        exit(1)          
    elif os.getuid() != 0:
        print(f"{error} Need higher privileges\n")
        exit(1)
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument")
        usage(1)

    codename = toolz.syst.get_codename()
    valid_codenames = ["bullseye", "bookworm", "sid"]
    if codename not in valid_codenames:
        print(f"{error} '{codename}' is a too old Debian version\n")
        exit(1)          

    i386needed = False
    grp_list = ["sudo"]
    
    inst_pkgs = ["vim", "git", "ssh", "rsync", "tree", "htop"]
    inst_pkgs += ["task-xfce-desktop", "task-desktop", "slick-greeter"]
    inst_pkgs += ["xfce4-appfinder", "xfce4-appmenu-plugin"]
    inst_pkgs += ["xfce4-clipman-plugin", "xfce4-power-manager"]
    inst_pkgs += ["xfce4-pulseaudio-plugin", "xfce4-screenshooter"]
    inst_pkgs += ["xfce4-weather-plugin", "xfce4-whiskermenu-plugin"]
    inst_pkgs += ["xfce4-xkb-plugin", "catfish", "redshift-gtk"]
    inst_pkgs += ["gvfs-backends", "network-manager-gnome", "gnome-calculator"]
    inst_pkgs += ["cups printer-driver-escpr system-config-printer"]
    inst_pkgs += ["synaptic", "gnome-system-monitor"]
    inst_pkgs += ["plank", "terminator", "file-roller", "evince"]
    inst_pkgs += ["gthumb", "gimp", "imagemagick", "simple-scan"]
    inst_pkgs += ["mpv", "lollypop", "soundconverter", "easytag"]
    inst_pkgs += ["fonts-noto", "ttf-mscorefonts-installer"]
    inst_pkgs += ["libreoffice-gtk3", "libreoffice-style-sifr"]
    inst_pkgs += ["papirus-icon-theme", "greybird-gtk-theme"]

    ff_pkg = "firefox-esr"
    if codename = "sid":
        ff_pkg = "firefox"
    inst_pkg.append(ff_pkg)

    if os.system("lspci | grep -qi nvidia") == 0:
        i386needed = True
        inst_pkgs += ["nvidia-driver", "nvidia-settings", "nvidia-xconfig"]

    hostname = toolz.syst.set_hostname()

    more_pkgs = ""
    if not toolz.syst.is_vm():
        if toolz.yesno("Install Virtual Machine Manager"):
            grp_list.append("libvirt")
            inst_pkgs.append("virt-manager")
            more_pkgs += f"  - {ci}virt-manager{c0}\n"

    if toolz.yesno("Install Kodi (media center)"):
        inst_pkgs.append("kodi")
        more_pkgs += f"  - {ci}kodi{c0}\n"

    if toolz.yesno("Install Steam"):
        i386needed = True
        inst_pkgs.append("steam")
        more_pkgs += f"  - {ci}steam{c0}\n"

    useless_pkgs = ["xfce4-terminal", "xterm", "termit", "hv3", "xarchiver"]
    useless_pkgs += ["parole", "quodlibet", "exfalso", "atril*", "xsane*"]

    user_list = toolz.syst.get-users()
    userstoadd_list = []
    for user in user_list:
        for grp in grp_list:
            if toolz.yesno("Add user '{user}' to '{grp}'", "y"):
                userstoadd_list.append((user,grp))

    if more_pkgs:
        print(f"{ci}Chosen additional applications{c0}:\n{more_pkgs}")

    if userstoadd_list:
        print(f"{ci} Users to add to groups{c0}:")
        for user, grp in userstoadd_list:
            print(f"  - {ci}'{user}' to '{grp}'{c0}")
    else:
        print(f"{cw}No user added to 'sudo'{c0}")

    if not toolz.yesno("Confirm your choices"):
        exit(0)

    if i386needed:
        os.system("dpkg --add-architecture i386")

    toolz.pkg.update_sourceslist(distro)
    toolz.pkg.install(inst_pkgs)

    toolz.pkg.purge(useless_pkgs)

    themesupdate.mcmojave_cursors("/tmp")
    themesupdate.catalina_gtk()

    toolz.conf.root()

    specials()

    for user, grp in userstoadd_list:
        os.system(f"adduser {user} {grp}")

    toolz.syst.reboot()
