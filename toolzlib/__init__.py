#!/usr/bin/env python3

import os
import re
import socket
import shutil
import subprocess
from . import file
from . import git
from . import pkg
from . import syst
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
        if user.is_sudo():
            if yesno(f"Install {pcount}"):
                pkg.install(reqpkgs, True)
            else:
                exit(1)
        else:
            exit(1)
        for rqpkg in missingpkgs:
            if not pkg.is_installed(rqpkg):
                print(f"{error} Needed package not installed\n")
                exit(1)
