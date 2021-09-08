#!/usr/bin/env python3

import os
import sys
import socket

import toolz
import themesupdate

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
    print(f"  -h,--help: Print this help")
    print()
    exit(errcode)


def personalization(home):
    toolz.conf.bash(home)
    toolz.conf.vim(home)
    toolz.conf.xfce(home)

    if home.startswith("/home/"):
        user = home.split("/")[-1]
        with open("/etc/passwd", "r") as f:
            for line in f:
                if line.startswith(f"{user}:"):
                    group = line.split(":")[4]
                    group = group.replace(",,,","")
                    toolz.file.rchown(home, user, group)


def install_xfce(distro, i386, req_pkgs, useless_pkgs):
    toolz.pkg.update_sourceslist(distro)

    if i386:
        os.system("dpkg --add-architecture i386")

    toolz.pkg.install(req_pkgs, True)
    toolz.pkg.purge(useless_pkgs, True)

    themesupdate.mcmojave_cursors("/tmp")
    themesupdate.catalina_gtk()
    toolz.conf.gruvbox_gtk()

    toolz.pkg.clean(True)

    toolz_path = os.path.dirname(__file__)
    exec(open(f"{toolz_path}/deploy_toolz.py").read())


def configure_system(fqdn):
    if socket.getfqdn() != fqdn:
        renew_hostname(fqdn)

    toolz.conf.swap()
    toolz.conf.ssh()

    toolz.conf.root()

    toolz.conf.lightdm()
    toolz.conf.networkmanager()
    toolz.conf.pulseaudio()
    toolz.conf.redshift()

    personalization("/etc/skel")


def specials(hostname):
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
    distro = toolz.syst.get_distro()

    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif distro != "debian":
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

    i386 = False
    grp_list = ["sudo"]
    
    req_pkgs = ["vim", "git", "ssh", "rsync", "tree", "htop"]
    req_pkgs += ["task-xfce-desktop", "task-desktop", "slick-greeter"]
    req_pkgs += ["xfce4-appfinder", "xfce4-appmenu-plugin"]
    req_pkgs += ["xfce4-clipman-plugin", "xfce4-power-manager"]
    req_pkgs += ["xfce4-pulseaudio-plugin", "xfce4-screenshooter"]
    req_pkgs += ["xfce4-weather-plugin", "xfce4-whiskermenu-plugin"]
    req_pkgs += ["xfce4-xkb-plugin", "catfish", "redshift-gtk"]
    req_pkgs += ["gvfs-backends", "network-manager-gnome", "gnome-calculator"]
    req_pkgs += ["cups printer-driver-escpr system-config-printer"]
    req_pkgs += ["synaptic", "deborphan", "gnome-system-monitor"]
    req_pkgs += ["plank", "terminator", "file-roller", "evince"]
    req_pkgs += ["gthumb", "gimp", "imagemagick", "simple-scan"]
    req_pkgs += ["mpv", "lollypop", "soundconverter", "easytag"]
    req_pkgs += ["fonts-noto", "ttf-mscorefonts-installer"]
    req_pkgs += ["libreoffice-gtk3", "libreoffice-style-sifr"]
    req_pkgs += ["papirus-icon-theme", "greybird-gtk-theme"]

    ff_pkg = "firefox-esr"
    if codename == "sid":
        ff_pkg = "firefox"
    req_pkgs.append(ff_pkg)

    if os.system("lspci | grep -qi nvidia") == 0:
        i386 = True
        req_pkgs += ["nvidia-driver", "nvidia-settings", "nvidia-xconfig"]

    hostname, domain = toolz.syst.set_hostname()
    fqdn = f"{hostname}.{domain}" if domain else hostname

    more_pkgs = ""
    if not toolz.syst.is_vm():
        if toolz.yesno("Install Virtual Machine Manager"):
            grp_list.append("libvirt")
            req_pkgs.append("virt-manager")
            more_pkgs += f"  {cw}-{c0} virt-manager\n"

    if toolz.yesno("Install transmission-daemon (torrent client)"):
        req_pkgs.append("transmission-daemon")
        more_pkgs += f"  {cw}-{c0} transmission-daemon\n"

    if toolz.yesno("Install Kodi (media center)"):
        req_pkgs.append("kodi")
        more_pkgs += f"  {cw}-{c0} kodi\n"

    if toolz.yesno("Install Steam"):
        i386 = True
        req_pkgs.append("steam")
        more_pkgs += f"  {cw}-{c0} steam\n"

    useless_pkgs = ["xfce4-terminal", "xterm", "termit", "hv3", "xarchiver"]
    useless_pkgs += ["parole", "quodlibet", "exfalso", "atril*", "xsane*"]
    useless_pkgs += ["nano"]

    user_list = toolz.syst.list_users()
    users_to_add = []
    xfce_users = []
    for user in user_list:
        for grp in grp_list:
            if not toolz.user.is_in_group(user, grp):
                if toolz.yesno(f"Add user '{user}' to '{grp}'", "y"):
                    users_to_add.append((user,grp))
        if toolz.yesno(f"Apply Xfce personalization for {user}"):
            xfce_users.append(user)

    print()

    my_conf = ""
    if socket.getfqdn() not in [hostname, f"{hostname}.{domain}"]:
        fqdn = f"{hostname}.{domain}" if domain else hostname
        my_conf += f"{ci}New hostname/FQDN{c0}: {fqdn}\n"

    if more_pkgs:
        my_conf += f"{ci}Chosen additional applications{c0}:\n{more_pkgs}"

    if users_to_add:
        my_conf += f"{ci} Users to add to groups{c0}:\n"
        for user, grp in users_to_add:
            my_conf += f"  {cw}-{c0} '{user}' to '{grp}'\n"

    if xfce_users:
        my_conf += f"{ci}Users applying Xfce personalization{c0}:\n"
        for user in xfce_users:
            my_conf += f"  {cw}-{c0} {user}\n"

    if my_conf:
        print(my_conf)
        if not toolz.yesno("Confirm your choices"):
            exit(0)

    print()

    install_xfce(distro, i386, req_pkgs, useless_pkgs)

    configure_system(fqdn)

    for user, grp in users_to_add:
        os.system(f"adduser {user} {grp}")

    for user in xfce_users:
        home = f"/home/{user}"
        personalization(home)

        if toolz.user.is_in_group(user, "libvirt") or \
                (user, "libvirt") in users_to_add:
            toolz.conf.tansmissiond(user, home)

    specials(hostname)

    toolz.syst.reboot()
