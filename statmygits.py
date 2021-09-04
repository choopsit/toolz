#!/usr/bin/env python3

import pathlib
import socket
import sys
import os
import getpass
import toolz

__description__ = "Return status of all git repositories stocked in a targetted folder"
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
    myscript = os.path.ame(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {myscript} [OPTION] [GIT_STOCK_FOLDER (default: current path)]")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help")
    print()
    exit(errcode)


def get_repos_status(gitstock):
    cpt = 0
    for repo in os.listdir(gitstock):
        path = f"{gitstock}/{repo}"
        if os.path.isdir(f"{path}/.git"):
            cpt += 1
            print(f"{ci}Repo{c0}: {repo}")
            toolz.git.stat_repo(path)

    if cpt == 0:
        print(f"{error} No git repo found in '{gitstock}'\n")
        exit(1)


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
        gitstock = sys.argv[1]
    elif len(sys.argv) == 1:
        gitstock = pathlib.Path().absolute()
        if getpass.getuser() == "choops":
            home = pathlib.Path.home()
            gitstock = f"{home}/Work/git"
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument\n")
        usage(1)

    get_repos_status(gitstock)
