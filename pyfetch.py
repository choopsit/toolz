#!/usr/bin/env python3

import sys
import apt
import os
import shutil
import re
import getpass
import socket
import platform
import subprocess
import datetime
import pathlib

__description__ = "Fetch system informations"
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
    print(f"  -h,--help:         Print this help")
    print(f"  -d,--default-logo: Use default logo")
    print()
    exit(errcode)


def default_logo():
    dlogo = []
    cl = ["\33[34m", "\33[33m"]
    dlogo.append(f"{cl[0]}      .####.      ")
    dlogo.append(f"{cl[0]}      #.####      ")
    dlogo.append(f"{cl[0]}  .######### {cl[1]}###. ")
    dlogo.append(f"{cl[0]}  ########## {cl[1]}#### ")
    dlogo.append(f"{cl[0]}  #### {cl[1]}########## ")
    dlogo.append(f"{cl[0]}  `### {cl[1]}#########` ")
    dlogo.append(f"{cl[1]}       ####`#     ")
    dlogo.append(f"{cl[1]}       `####`     ")
    dlogo.append("                  ")

    return dlogo


def distro_logo(dist):
    dlogo = []
    if dist == "debian":
        cl = ["\33[31m"]
        dlogo.append(f"{cl[0]}     ,get$$gg.    ")
        dlogo.append(f"{cl[0]}   ,g$\"     \"$P.  ")
        dlogo.append(f"{cl[0]}  ,$$\" ,o$g. \"$$: ")
        dlogo.append(f"{cl[0]}  :$$ ,$\"  \"  $$  ")
        dlogo.append(f"{cl[0]}   $$ \"$,   .$$\"  ")
        dlogo.append(f"{cl[0]}   \"$$ \"9$$$P\"    ")
        dlogo.append(f"{cl[0]}    \"$b.          ")
        dlogo.append(f"{cl[0]}      \"$b.        ")
        dlogo.append(f"{cl[0]}         \"\"\"      ")
    elif dist == "raspbian":
        cl = ["\33[32m", "\33[31m"]
        dlogo.append(f"{cl[0]} o.     .oo@$$$$$°")
        dlogo.append(f"{cl[0]} $$$o..o$$$$$$$*' ")
        dlogo.append(f"{cl[0]} $${cl[1]}.o@@o.{cl[0]}$$$*'    ")
        dlogo.append(f"{cl[1]} . $$$$$$ .o@o.   ")
        dlogo.append(f"{cl[1]} $ '*$$*' $$$$$   ")
        dlogo.append(f"{cl[1]} ' .o@@o. '*$*'.$ ")
        dlogo.append(f"{cl[1]} . $$$$$$ .o@o.'$ ")
        dlogo.append(f"{cl[1]} $ '*$$*' $$$$$   ")
        dlogo.append(f"{cl[1]} ' .o@@o. '*$*'   ")
    else:
        dlogo = default_logo()

    return dlogo


def draw_logo(default):
    cpalette = ["\33[30m", "\33[31m", "\33[32m", "\33[33m", "\33[34m",
                "\33[35m", "\33[36m", "\33[37m"]

    palette = ""
    for cpal in cpalette:
        palette += f"{cpal}#{c0}"

    logo = []

    dist = ""
    with open("/etc/os-release", "r") as osfile:
        for line in osfile:
            if line.startswith("ID="):
                dist = line.split("=")[1].rstrip("\n").lower()

    if dist and default is False:
        logo = distro_logo(dist)
    else:
        logo = default_logo()

    logo.append(f"     {palette}     ")

    return logo, dist


def get_host():
    ch = "\33[33m"
    myuser = getpass.getuser()
    myhostname = socket.gethostname()

    return f"{ch}{myuser}{c0}@{ch}{myhostname}{c0}"


def get_os():
    with open("/etc/os-release", "r") as osfile:
        for line in osfile:
            if line.startswith("PRETTY"):
                osname = line.split("=")[1].rstrip("\n").replace("\"", "")
    osname += " "+platform.machine()

    return f"{ci}OS{c0}:     {osname}"


def get_kernel():
    kernel = platform.release()

    sep = ""
    if len(kernel) < 12:
        sep = "\t"

    return f"{ci}Kernel{c0}: {kernel}{sep}"


def get_packages(dist):
    pkgcount = "N/A"

    distok = ["debian", "raspbian", "ubuntu"]
    if dist in distok:
        list_cmd = ['dpkg', '-l']
        count_cmd = ['grep', '-c', '^i']
        pkglist = subprocess.Popen(list_cmd, stdout=subprocess.PIPE)
        pkgcount = subprocess.check_output(count_cmd, stdin=pkglist.stdout,
                                           universal_newlines=True).rstrip("\n")

    return f"{ci}Packages{c0}:  {pkgcount}"


def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = int(float(f.readline().split()[0]))
        uptime_string = datetime.timedelta(seconds=uptime_seconds)

    return f"{ci}Uptime{c0}: {uptime_string}"


def get_shell():
    shell = os.path.basename(os.environ['SHELL'])
    shellvf = str(subprocess.check_output(['bash', '--version'])).split()[3]
    shellv = shellvf.split("(")[0]

    return f"{ci}Shell{c0}:  {shell} {shellv}"


def get_term():
    term = "N/A"

    getterm = "x-terminal-emulator --version 2>/dev/null"
    try:
        os.environ['DISPLAY']
    except KeyError:
        for line in os.popen(getterm):
            if "terminator" in line:
                term = "terminator"
    else:
        term = os.popen(getterm).read().rstrip()

    return f"{ci}Terminal{c0}:  {term}"


def get_de():
    try:
        de = os.environ['XDG_CURRENT_DESKTOP']
    except KeyError:
        try:
            de = os.environ['DESKTOP_SESSION']
        except KeyError:
            de = "N/A"

    wmchk_cmd = ['update-alternatives', '--list', 'x-window-manager']
    try:
        wm = subprocess.check_output(wmchk_cmd,
                                     universal_newlines=True).split("/")[-1].rstrip("\n")
    except subprocess.CalledProcessError:
        wm = "N/A"

    sep = "\t\t"
    if len(de) < 5:
        sep += "\t"
    elif len(de) > 12:
        sep = "\t"

    return f"{ci}DE{c0}:     {de}{sep}{ci}WM{c0}:\t   {wm}", de, wm


def get_perso(de, wm):
    gtkth = ""
    iconth = ""
    home = str(pathlib.Path.home())
    if de == "XFCE" or wm == "xfwm4":
        conf = f"{home}/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml"
        with open(conf, "r") as f:
            for line in f:
                if "\"ThemeName" in line:
                    gtkth = line.split('="')[-1].split('"')[0]
                if "IconThemeName" in line:
                    iconth = line.split('="')[-1].split('"')[0]
    elif wm == "awesome":
        conf = f"{home}/.gtkrc-2.0"
        if os.path.isfile(conf):
            with open(conf, "r") as f:
                for line in f:
                    if line.startswith("gtk-theme-name"):
                        gtkth = line.split('="')[-1].split('"')[0]
                    if line.startswith("gtk-icon-theme-name"):
                        iconth = line.split('="')[-1].split('"')[0]

    sep = "\t\t"
    if len(iconth) < 5:
        sep += "\t"
    elif len(iconth) > 12:
        sep = "\t"

    return f"{ci}Icons{c0}:  {iconth}{sep}{ci}GTK-theme{c0}: {gtkth}"


def get_cpu():
    threadcount = 0
    with open("/proc/cpuinfo", "r") as f:
        for line in f:
            if line.startswith("model name"):
                threadcount += 1
                cpu = line.split(': ')[1].rstrip("\n")

    return f"{ci}CPU{c0}:    {cpu} ({threadcount} threads)"


def get_gpu():
    pcilist_cmd = ['lspci']
    filter_cmd = ['grep', 'VGA']
    pciinfo = subprocess.Popen(pcilist_cmd, stdout=subprocess.PIPE)
    gpuinfo = subprocess.check_output(filter_cmd, stdin=pciinfo.stdout,
                                      universal_newlines=True).rstrip("\n")
    gpu = gpuinfo.split(": ")[1]

    return f"{ci}GPU{c0}:    {gpu}"


def get_mem():
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                memtotal = int(line.split(None, 2)[1]) // 1024
            if line.startswith("MemAvailable:"):
                memused = memtotal - int(line.split(None, 2)[1]) // 1024
            if line.startswith("SwapTotal:"):
                swaptotal = int(line.split(None, 2)[1]) // 1024
            if line.startswith("SwapFree:"):
                swapused = swaptotal - int(line.split(None, 2)[1]) // 1024

    mrepart = f"{memused}/{memtotal}"
    msep = "\t"
    if len(mrepart) < 10:
        msep += "\t"
    ret = f"{ci}RAM{c0}:    {memused}/{memtotal}MB {msep}"
    ret += f"{ci}Swap{c0}:      {swapused}/{swaptotal}MB"
    return ret


def pick_infos(logo, dist):
    infolist = []
    infolist.append(get_host())
    infolist.append(get_os())
    infolist.append(f"{get_kernel()}\t{get_packages(dist)}")
    infolist.append(get_uptime())
    infolist.append(f"{get_shell()}\t\t{get_term()}")
    deinfo, de, wm = get_de()
    infolist.append(deinfo)
    infolist.append(get_perso(de, wm))
    infolist.append(get_cpu())
    if dist != 'raspbian':
        infolist.append(get_gpu())
    infolist.append(get_mem())

    while len(infolist) < len(logo):
        infolist.append("")

    return infolist


def show_infos(logo, info):
    for i in range(len(logo)):
        print(logo[i], info[i])

    print()


if __name__ == "__main__":
    defaultlogo = False

    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) == 2 and re.match('^-(d|-default-logo)$', sys.argv[1]):
        defaultlogo = True
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument")
        usage(1)

    mylogo, mydist = draw_logo(defaultlogo)
    myinfo = pick_infos(mylogo, mydist)

    show_infos(mylogo, myinfo)
