#!/usr/bin/env python3

import os
import re
import socket
import shutil
import subprocess
from . import file
from . import pkg
from . import sys
from . import user

__description__ = "Common functions module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def yesno(question, default="n"):
    """Ask a '"yes or no' question with a default choice defined as 'n'
       Return True/False for 'Yes'/'No'"""
    
    defindic = "[y/N]"
    answer = ""
    ret = False

    if default.lower() == "y":
        defindic = "[Y/n]"

    answer = input(f"{question} {defindic} ? ").lower()
    if answer == "":
        answer = default.lower()
    elif not re.match('^(y|yes|n|no)$', answer):
        print(f"{error} Invalid answer '{answer}'")
        ret = yesno(question, default)

    if answer.startswith("y"):
        ret = True

    return ret


def is_valid_hostname(hostname):
    """Check validity of a string to be used as hostname"""

    if len(hostname) > 255:
        return False

    if hostname[-1] == ".":
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)

    return all(allowed.match(x) for x in hostname.split("."))


def decompose_fqdn(fqdn):
    """Split FQDN in hostname and domain"""

    hostname = fqdn.split(".")[0]
    domain = ".".join(fqdn.split(".")[1:])

    return hostname, domain


def set_hostname():
    """Define a machine hostname"""

    fqdn = socket.getfqdn()
    if yesno(f"Keep current hostname: '{fqdn}'", "y"):
        hostname, domain = decompose_fqdn(fqdn)
    else:
        newhostname = input("New hostname (or FQDN) ? ")
        if newhostname == "":
            print(f"{error} No hostname given")
            hostname, domain = set_hostname()
        elif is_valid_hostname(newhostname):
            hostname, domain = decompose_fqdn(newhostname)
        else:
            print(f"{error} Invalid hostname '{newhostname}'")
            hostname, domain = set_hostname()

    return hostname, domain


def renew_hostname(fqdn):
    """Apply machine naming"""

    hostname, domain = decompose_fqdn(fqdn)

    with open("/etc/hostname", "w") as f:
        f.write(f"{hostname}\n")

    hostline = f"127.0.1.1\t{hostname}"
    if domain != "":
        hostline += f".{domain}\t{hostname}"

    file.overwrite("/etc/hosts", "/tmp/hosts")
    with open("/tmp/hosts", "r") as oldf, open("/etc/hosts", "w") as newf:
        for line in oldf:
            if line.startswith("127.0.1.1"):
                newf.write(hostline)
            else:
                newf.write(line)

    os.system(f"hostname {hostname}")


def git_update(url, folder):
    if os.path.isdir(folder):
        os.chdir(folder)
        pull_cmd = ["git", "pull", "-q", "--no-rebase"]
        subprocess.check_output(pull_cmd)
    else:
        clone_cmd = ["git", "clone", "-q", url, folder]
        subprocess.check_output(clone_cmd)


def prerequisites(reqpkgs):
    missingpkgs = []
    for rqpkg in reqpkgs:
        if not pkg.is_installed(rqpkg):
            missingpkgs.append(rqpkg) 

    if missingpkgs:
        print(f"{warning} Missing package(s): {', '.join(missingpkgs)}")
        pcount = "it"
        if len(missingpkgs) > 1:
            pcount = "them"
        if user.is_in_group(os.getlogin(), 'sudo'):
            if yesno(f"Install {pcount}"):
                install = "sudo apt-get install"
                inst_cmd = f"{install} -yy {' '.join(reqpkgs)}"
                os.system(inst_cmd)
            else:
                exit(1)
        elif os.getuid() == 0:
            if yesno(f"Install {pcount}"):
                pkg.install(missingpkgs)
            else:
                exit(1)
        else:
            exit(1)
