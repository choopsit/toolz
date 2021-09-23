#!/usr/bin/env python3

import sys
import os
import shutil
import re

__description__ = "Graphical filesystems usage"
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
    print(f"  -a,--all:  Show all filesystems including tmpfs\n")
    exit(errcode)


def dim_separator(prop):
    sep = " "

    if prop == 100:
        sep = ""
    elif prop < 10:
        sep = "  "

    return sep


def color_fs(prop):
    color = "\33[32m"

    if prop >= 90:
        color = "\33[33m"
    elif prop >= 95:
        color = "\33[31m"

    return color


def dim_fsunit(voltotal):
    fsunit = "GB"
    ufactor = (1024**3)

    if voltotal / ufactor > 1024:
        fsunit = "TB"
        ufactor *= 1024

    return fsunit, ufactor


def color_line(mountpoint):
    fs_color = "\33[0m"

    if mountpoint[1] in ["nfs", "cifs"]:
        fs_color = "\33[34m"
    elif mountpoint[1].startswith("fuse"):
        fs_color = "\33[35m"
    elif mountpoint[1].endswith("tmpfs"):
        fs_color = "\33[37m"

    return fs_color


def draw_fs(mountpoint):
    ctxt = color_line(mountpoint)

    total = shutil.disk_usage(str(mountpoint[0]))[0]
    used = shutil.disk_usage(str(mountpoint[0]))[1]

    usedprop = 100 * used // total

    sepg = dim_separator(usedprop)

    cfs = color_fs(usedprop)
    cn = "\33[37m"

    totallg = 40
    usedlg = usedprop * totallg // 100
    usedgr = usedlg * f"#"
    freegr = (totallg - usedlg) * "-"

    unit, factor = dim_fsunit(total)

    totalu = total / factor
    usedu = used / factor
    freeu = totalu - usedu

    tline = f"-{ci}{mountpoint[2]}{c0}:\n"
    tline += f"  {ci}type{c0}: {ctxt}{mountpoint[1]}\t"
    tline += f"{ci}mounted on{c0}: {ctxt}{mountpoint[0]}{c0}"

    repart = f"{usedu:.1f}/{totalu:.1f}{unit}"
    lensep = 13 - len(repart)
    sep = " " * lensep

    gline = f"  [{cfs}{usedgr}{cn}{freegr}{c0}]{sepg}{cfs}{usedprop}{c0}%"
    gline += f" {sep}{ctxt}{repart}{c0}"

    freesp= f"{freeu:.1f}{unit}"
    lenfsep = 8 - len(freesp)
    fsep = " " * lenfsep

    gline += f" -{fsep}{ctxt}{freesp} free{c0}"

    print(f"{tline}\n{gline}")


def fs_info(fsregex):
    print(f"{ci}Filesystems{c0}:")

    with open("/proc/mounts", "r") as f:
        mounts = [(line.split()[1].replace('\\040', ' '), line.split()[2], line.split()[0])
                  for line in f.readlines()]

        for mntpoint in mounts:
            if re.match(fsregex, mntpoint[1]):
                draw_fs(mntpoint)

    print()


if __name__ == "__main__":
    myfsregex = 'ext|btrfs|lvm|xfs|zfs|ntfs|vfat|fuseblk|nfs$|nfs4|cifs'

    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) == 2 and sys.argv[1] in ["-a","--all"]:
        myfsregex += '|.*tmpfs'
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument\n")
        usage(1)

    fs_info(myfsregex)
