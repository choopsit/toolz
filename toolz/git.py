#!/usr/bin/env python3

import os
import subprocess

__description__ = "Git functions module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def update(url, folder):
    """Pull a git repo if avaliable, else clone it"""

    if os.path.isdir(folder):
        os.chdir(folder)
        pull_cmd = ["git", "pull", "-q", "--no-rebase"]
        subprocess.check_output(pull_cmd)
    else:
        clone_cmd = ["git", "clone", "-q", url, folder]
        subprocess.check_output(clone_cmd)


def stat_repo(path):
    """Return git repo status"""

    os.chdir(path)
    awk_cmd = "'/^Date:/ {print $2 \" \" $3 \" \" $4 \" \" $6 \" \" $5}'"
    lc_cmd = f"git show | awk {awk_cmd}"
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
    """Test if a folder is a git repo, then get its status"""

    with open(f"{path}/.git/config", "r") as f:
        stat_repo(path)
