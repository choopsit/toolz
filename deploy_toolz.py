#!/usr/bin/env python3

import os
import sys
import re
import toolz

__description__ = "Deploy scripts to '/usr/local/bin'"
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
    print(f"  './{myscript} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(errcode)


def deploy_lib(src, tgt):
    mylib = "toolz"
    libsrc = os.path.join(src, mylib)
    libtgt = os.path.join(tgt, mylib)

    if not os.path.isdir(libtgt):
        os.makedirs(libtgt)

    if toolz.file.overwrite(libsrc, libtgt):
        print(f"{done} '{mylib}' deployed in '/usr/local/bin'")


def deploy_scripts(src, tgt):
    scripts = [f.replace(".py", "") for f in os.listdir(src) if f.endswith(".py")]

    for not_to_deploy in ["deploy_toolz", "xfce_init"]:
        scripts.remove(not_to_deploy)
        print(f"{warning} '{not_to_deploy}.py' not deployed")

    for script in scripts:
        if toolz.file.overwrite(f"{src}/{script}.py", f"{tgt}/{script}"):
            print(f"{done} '{script}' deployed in '/usr/local/bin'")
        else:
            print(f"{error} '{script}' failed to be deployed")
    print()


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif os.getuid() != 0:
        print(f"{error} Need higher privileges\n")
        exit(1)
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument\n")
        usage(1)

    toolz.syst.prereq()

    src = os.path.dirname(os.path.realpath(__file__))
    tgt = "/usr/local/bin"

    deploy_lib(src, tgt)
    deploy_scripts(src, tgt)
