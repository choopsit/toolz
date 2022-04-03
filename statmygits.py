#!/usr/bin/env python3

import pathlib
import socket
import sys
import os
import getpass
import toolz

__description__ = "Return status of all git repositories stocked in a targetted folder"
__author__ = "Choops <choopsbd@gmail.com>"

DEF = "\33[0m"
RED = "\33[31m"
GRN = "\33[32m"
YLO = "\33[33m"
CYN = "\33[36m"

ERR = f"{RED}ERR{DEF}:"
OK = f"{GRN}OK{DEF}:"
WRN = f"{YLO}WRN{DEF}:"
NFO = f"{CYN}NFO{DEF}:"


def usage(err_code=0):
    my_script = os.path.basename(__file__)
    print(f"{CYN}{__description__}\nUsage{DEF}:")
    print(f"  {my_script} [OPTION] [GIT_STOCK_FOLDER (default: current path)]")
    print(f"{CYN}Options{DEF}:")
    print(f"  -h,--help: Print this help\n")
    exit(err_code)


def get_repos_status(git_stock):
    cpt = 0
    for repo in os.listdir(git_stock):
        path = f"{git_stock}/{repo}"

        if os.path.isdir(f"{path}/.git"):
            cpt += 1
            if cpt == 1:
                print(f"{CYN}Git repos status{DEF}:")
            print(f"{CYN}Repo{DEF}: {YLO}{repo}{DEF}")
            toolz.git.stat_repo(path)

    if cpt == 0:
        print(f"{ERR} No git repo found in '{gitstock}'\n")
        exit(1)


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
        git_stock = sys.argv[1]
    elif len(sys.argv) == 1:
        git_stock = pathlib.Path().absolute()
        if getpass.getuser() == "choops":
            home = pathlib.Path.home()
            git_stock = f"{home}/Work/git"
    elif len(sys.argv) > 1:
        print(f"{ERR} Bad argument\n")
        usage(1)

    get_repos_status(git_stock)
