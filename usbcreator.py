#!/usr/bin/env python3

import sys
import os
import shutil
import re
import subprocess
import urllib.request
import time
import datetime
import toolzlib

__description__ = "Create a bootable USB key to install Debian"
__author__ = "Choops <choopsbd@gmail.com>"


def usage(errcode):
    myscript = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  '{myscript} [OPTION] <DEVICE>' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(errcode)


def test_device(device):
    reqpkgs = ["btrfs-progs", "lvm2", "isolinux", "live-build", "live-manual",
               "live-tools"]
    toolzlib.prerequisites(reqpkgs)

    mydev = f"/dev/{device}"
    if not os.path.exists(mydev):
        print(f"{error} No device '{device}' available\n")
        exit(1)

    with open("/proc/mounts", "r") as f:
        if mydev in f.read():
            print(f"{error} '{device}' is mounted\n")
            exit(1)

    chklvm = os.popen("pvs").read()
    if mydev in chklvm:
        print(f"{error} '{device}' is used for LVM\n")
        exit(1)

    chkbtrfs = os.popen("btrfs fi show").read()
    if mydev in chkbtrfs:
        print(f"{error} '{device}' is used for btrfs volume\n")
        exit(1)

    return True


def choose_debian_version():
    vlist = ["stable", "oldstable", "testing"]
    baseurl = "https://cdimage.debian.org/cdimage"

    # check latest stable version at:
    #  https://cdimage.debian.org/cdimage/release/current/amd64/iso-cd
    last_stable = "11.0.0"
    # check latest oldstable version at:
    #  https://cdimage.debian.org/cdimage/archive/latest-oldstable/amd64/iso-cd
    last_oldstable = "10.10.0"

    isos = ["", "", ""]
    isos[0] = f"release/current/amd64/iso-cd/debian-{last_stable}"
    isos[1] = f"archive/latest-oldstable/amd64/iso-cd/debian-{last_oldstable}"
    isos[2] = f"weekly-builds/amd64/iso-cd/debian-testing"

    version = ""
    isourl = ""

    vchoice = int()
    print(f"{ci}Available versions{c0}:")
    for i in range(len(vlist)):
        print(f"  {i}) {ci}{vlist[i]}{c0}")
    vchoicestr = input("Your choice ? ")
    try:
        vchoice = int(vchoicestr)
    except ValueError:
        print(f"{error} Invalid choice '{vchoicestr}'\n")
        version, isourl = choose_debian_version()

    for i in range(len(vlist)):
        if vchoice == i:
            version = vlist[vchoice]
            isourl = f"{baseurl}/{isos[vchoice]}-amd64-netinst.iso"
    if version == "":
        print(f"{error} Out of range choice '{vchoice}'\n")
        version, isourl = choose_debian_version()

    return version, isourl


def create_usbkey(device, distro):
    if distro == "Debian":
        version, url = choose_debian_version()
        
        iso = "/tmp/debian.iso"
    elif distro == "Clonezilla":
        # check latest version at:
        #  https://clonezilla.org/downloads/download.php?branch=stable
        version = "2.7.2-39"

        url = "https://sourceforge.net/projects/clonezilla/files/"
        url += f"clonezilla_live_stable/{version}/"
        url += f"clonezilla-live-{version}-amd64.iso/download"
        iso = "/tmp/clonezilla.iso"
    elif distro == "Xubuntu LTS":
        # check latest LTS codename (version) and version number at:
        #  https://cdimages.ubuntu.com/xubuntu/releases
        codename = "focal"
        version = "20.04.2.0"
        
        url = f"https://cdimages.ubuntu.com/xubuntu/releases/{codename}/"
        url += f"release/xubuntu-{version}-desktop-amd64.iso"
        iso = "/tmp/xubuntu.iso"

    if os.path.isfile(iso):
        os.remove(iso)

    print(f"{ci}Downloading {distro} {version} ISO...{c0}")
    urllib.request.urlretrieve(url, iso)

    print(f"{ci}Creating {distro} {version} bootable USB key...{c0}")
    if os.system(f"dd bs=4M if={iso} of=/dev/{device} conv=fdatasync") == 0:
        print(f"{done} Bootable {distro} {version} USB key created\n")
    else:
        print(f"{error} Failed to create {distro} {version} USB key\n")


def custom_live_codename():
    stable = "bullseye"
    testing = "bookworm"
    okcodenames = [stable, testing, "sid"]

    print(f"{ci}Available Debian codenames{c0}:")
    for i in range(len(okcodenames)):
        print(f"  {i}) {ci}{okcodenames[i]}{c0}")
    cchoicestr = input(f"Your choice [default: '{okcodenames[0]}'] ? ")

    if cchoicestr == "":
        codename = okcodenames[0]
    else:
        try:
            cchoice = int(cchoicestr)
        except ValueError:
            print(f"{error} Invalid choice '{cchoicestr}'\n")
            codename = custom_live_codename()

        for i in range(len(okcodenames)):
            if cchoice == i:
                codename = okcodenames[cchoice]
        if codename == "":
            print(f"{error} Out of range choice '{cchoice}'\n")
            codename = custom_live_codename()

    return codename


def custom_live_hostname(codename):
    hostname = input(f"Custom live hostname [default: '{codename}-custom'] ? ")
    if hostname == "":
        hostname = f"{codename}-custom"

    if not toolzlib.is_valid_hostname(hostname):
        print(f"{error} Invalid hostname '{hostname}'\n")
        hostname = custom_live_hostname()

    return hostname


def custom_live_user():
    user = input("Custom live username [default: 'liveuser'] ? ")
    if user == "":
        user = "liveuser"

    if not re.match('^[a-z0-9][a-z0-9_]{0,30}', user):
        print(f"{error} Invalid username '{user}'\n")
        user = custom_live_user()

    return user


def configure_custom_live():
    codename = custom_live_codename()
    hostname = custom_live_hostname(codename)
    user = custom_live_user()

    print(f"{ci}Custom Debian live settings{c0}:")
    print(f"  - {ci}Codename{c0}: {codename}")
    print(f"  - {ci}Hostname{c0}: {hostname}")
    print(f"  - {ci}User{c0}:     {user}")

    confconf = input("Confirm configuration [Y/n] ? ")
    if re.match('^(n|no)$', confconf):
        codename, user, hostname = configure_custom_live()

    return codename, user, hostname


def build_iso(codename, user, hostname):
    print(f"{cw}Grab a tea. It will take some time...{c0}")
    time.sleep(1)
    print(f"{ci}Preparing build...{c0}")

    #build = datetime.datetime.today().strftime("%y%m%d-%H")
    build = datetime.datetime.today().strftime("%y%m%d")
    workfolder = f"/tmp/{codename}_livebuild_{build}"

    if os.path.isdir(workfolder):
        shutil.rmtree(workfolder)

    os.makedirs(f"{workfolder}/config/package-lists")
    clpkgs = ["live-boot", "live-config", "live-config-systemd",
              "task-desktop", "task-xfce-desktop", "sudo", "firmware-linux",
              "build-essential", "ssh", "vim", "git", "tree", "curl", "rsync",
              "p7zip-full", "htop", "docker", "docker-compose", "terminator",
              "mpv", "gthumb", "gimp", "arc-theme", "papirus-icon-theme"]
    with open(f"{workfolder}/config/package-lists/live.list.chroot", "w") as f:
        for clpkg in clpkgs:
            f.write(clpkg+"\n")

    with open(f"{workfolder}/config/build", "w") as f:
        f.write("[Image]\n")
        f.write("Architecture: amd64\n")
        f.write("Archive-Areas: main contrib non-free\n")
        f.write(f"Distribution-Chroot: {codename}"+"\n")
        f.write(f"Distribution-Binary: {codename}"+"\n")
        f.write("Mirror-Bootstrap: http://deb.debian.org/debian/\n\n")
        f.write("[FIXME]\n")
        f.write(f"Configuration-Version: 1:{build}"+"\n")
        f.write(f"Name: {codename}-custom"+"\n")

    buildbase = "/usr/share/doc/live-build/examples/auto"
    shutil.copytree(buildbase, f"{workfolder}/auto")
    with open(f"{workfolder}/auto/config", "w") as f:
        f.write('#!/bin/sh\n\n')
        f.write('set -e\n\n')
        f.write('lb config noauto \\\n')
        f.write('    --architectures "amd64" \\\n')
        f.write(f'    --distribution "{codename}" '+'\\\n')
        f.write('    --linux-flavours "amd64" \\\n')
        f.write('    --archive-areas "main contrib non-free" \\\n')
        f.write('    --linux-packages "linux-image" \\\n')
        f.write('    --firmware-binary "true" \\\n')
        f.write('    --firmware-chroot "true" \\\n')
        f.write('    --ignore-system-defaults \\\n')
        f.write('    --bootappend-live "boot=live persistence components ')
        f.write('autologin \\\n')
        f.write(f'        username={user} user-fullname={user} ')
        f.write(f'hostname={hostname} '+'\\\n')
        f.write('        keyboard-layouts=fr keyboard-model=pc105 ')
        f.write('timezone=Europe/Paris utc=yes" \\\n')
        f.write('    --debian-installer "live" \\\n')
        f.write('    --debian-installer-gui "true" \\\n')
        f.write('    "${@}"\n')

    print(f"{ci}Building ISO image...{c0}")
    os.chdir(workfolder)
    os.system("lb config")
    
    if os.system("lb build") == 0:
        customiso = ""

        for filename in os.listdir(workfolder):
            if filename.endswith(".iso"):
                customiso = os.path.join(workfolder, filename)
        
        if customiso == "":
            print(f"{error} Can not find ISO image in '{workfolder}'")
            exit(1)

        print(f"{done} ISO image built: '{customiso}")
    else:
        print(f"{error} Failed to build custom ISO image")
        exit(1)

    return customiso


def deploy_iso_on_usbkey(iso, device):
    print(f"{ci}Cleaning USB key...{c0}")
    if os.path.exists(f"/dev/{device}3"):
        for i in range(3, 0, -1):
            os.system(f"wipefs '/dev/{device}{i}'")
            fdiskanswers = "d+enter + enter + w+enter"
            if i == 1:
                fdiskanswers = "d+enter + w+enter"
            print(f'\n{ci}Removing partition "/dev/{device}{i}"...{c0}')
            print(f"{cw}Answers to give to 'fdisk'{c0}: {fdiskanswers}")
            os.system(f'fdisk "/dev/{device}"')
        os.system("partprobe")

    print(f"{ci}Putting iso image '{iso}' on '{device}'...{c0}")
    if os.system(f"dd if='{iso}' of='/dev/{device}'") == 0:
        print(f"{done} '{iso}' deployed on '{device}'")
    else:
        print(f"{error} Failed to deploy '{iso}' on '{device}'")
        exit(1)


def add_persistent_part(device):
    print(f'{ci}Adding persistent part "/dev/{device}3"...{c0}')
    os.system(f'wipefs "/dev/{device}"')
    fdiskanswers = "n+enter + enter*4 [+ y+enter if signature to remove] + "
    fdiskanswers += "w+enter"
    print(f"{cw}Answers to give to 'fdisk'{c0}: {fdiskanswers}")
    os.system(f'fdisk "/dev/{device}"')
    os.system("partprobe")
    os.system("sync")
    os.system(f'mkfs.ext4 -FL persistence "/dev/{device}3"')
    os.system(f'mount "/dev/{device}3" /mnt')
    with open("/mnt/persistence.conf", "w") as f:
        f.write("/ union")
    os.system("sync")
    os.system("umount /mnt")


def create_custom_live(device, persistence=False):
    clcodename, cluser, clhostname = configure_custom_live()

    cliso = build_iso(clcodename, cluser, clhostname)
    
    deploy_iso_on_usbkey(cliso, device)

    if persistence:
        add_persistent_part(device)

    print(f"{done} USB key is ready")


def choose_key_format():
    bkeys = ["Debian netinstall", "Xubuntu LTS live", "Clonezilla live",
             "Custom Debian live", "Custom Debian live with persistence"]
    print(f"{ci}Available bootable USB key format{c0}:")
    for i in range(len(bkeys)):
        print(f"  {i}) {ci}{bkeys[i]}{c0}")
    fchoicestr = input("Your choice ? ")

    try:
        fchoice = int(fchoicestr)
    except ValueError:
        print(f"{error} Invalid choice '{fchoicestr}'")
        fchoice = choose_key_format()
    
    if fchoice not in range(len(bkeys)):
        print(f"{error} Out of range choice '{fchoice}'")
        fchoice = choose_key_format()
    else:
        print(f"{cw}{bkeys[fchoice]}{c0}")

    return fchoice


c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"

if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif os.getuid() != 0:
        print(f"{error} Need higher privileges\n")
        exit(1)
    elif test_device(sys.argv[1]):
        mykey = choose_key_format()
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument\n")
        usage(1)

    mydistros = ["Debian", "Xubuntu LTS", "Clonezilla"]
    if mykey in [0..2]:
        create_usbkey(sys.argv[1], mydistros[mykey])
    elif mykey == 3:
        create_custom_live(sys.argv[1])
    elif mykey == 4:
        create_custom_live(sys.argv[1], persistence=True)
