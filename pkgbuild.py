#!/usr/bin/env python3
import sys
import re
import os
import pathlib
import shutil
import toolz

__description__ = "Build a debian package"
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
    print(f"  '{myscript} [OPTION] <BUILDFOLDER>' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(errcode)


def build_deb_package(folder):
    myuser = pathlib.Path(folder).owner()
    mygroup = pathlib.Path(folder).group()

    toolz.file.rchown(folder, "root", "root")

    os.system(f"dpkg-deb --build {folder}")

    for target in [folder, f"{folder}.deb"]:
        toolz.file.rchown(target, myuser, mygroup)

    destfolder = os.path.abspath(pathlib.Path(folder).parent)
    pkgname = os.path.basename(folder)
    print(f"{done} '{pkgname}.deb' generated in '{destfolder}'")


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif os.getuid() != 0:
        print(f"{error} Need higher privileges")
        exit(1)
    elif len(sys.argv) == 2:
        if sys.argv[1].endswith("/"):
            folder = sys.argv[1][:-1]
        else:
            folder = sys.argv[1]

        if os.path.isfile(f"{folder}/DEBIAN/control"):
            build_deb_package(folder)
        else:
            print(f"{error} Invalid debian package source folder '{folder}'")
            exit(1)
    else:
        print(f"{error} Bad argument")
        usage(1)
