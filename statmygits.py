#!/usr/bin/env python3

import pathlib
import socket
import sys
import re
import os

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


def usage():
    myscript = f"{os.path.basename(__file__)}"
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {myscript} [OPTION] [GIT_STOCK_FOLDER (default: current path)]")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help")
    print()


def stat_repo(path):
    os.chdir(path)
    lc_cmd = "git show | "
    lc_cmd += "awk '/^Date:/ {print $2 \" \" $3 \" \" $4 \" \" $6 \" \" $5}'"
    lastcommit = os.popen(lc_cmd).read().strip("\n")
    commitcount = os.popen("git rev-list --all --count").read().strip("\n")
    print(f"{ci}Last commit{c0}: {lastcommit} ({commitcount})")

    chk = os.popen("git status -s").read()
    if chk == "":
        print(f"{cok}Up to date{c0}")
    else:
        print(f"{cw}Uncommited changes{c0}:")
        os.system("git status -s")
    print()


def test_repo(path):
    with open(f"{path}/.git/config", "r") as f:
        stat_repo(path)


if __name__ == "__main__":
    gitstock = pathlib.Path().absolute()

    if socket.gethostname() == "mrchat":
        home = pathlib.Path.home()
        gitstock = f"{home}/Work/git"

    if len(sys.argv) > 1:
        if re.match('^-(h|-help)$', sys.argv[1]):
            usage()
            exit(0)
        gitstock = sys.argv[1]

    if len(sys.argv) > 2:
        print(f"{error} Too many arguments")
        exit(1)

    if not os.path.isdir(gitstock):
        print(f"{error} '{gitstock}' is not a folder")
        exit(1)

    cpt = 0
    for repo in os.listdir(gitstock):
        path = f"{gitstock}/{repo}"
        if os.path.isdir(f"{path}/.git"):
            cpt += 1
            print(f"{ci}Repo{c0}: {repo}")
            test_repo(path)

    if cpt == 0:
        print(f"{error} No git repo found in '{gitstock}'")
