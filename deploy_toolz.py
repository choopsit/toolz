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


def usage(err_code=0):
    my_script = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  './{my_script} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(err_code)


def deploy_scripts(src, tgt):
    scripts = [f.replace(".py", "") for f in os.listdir(src) if f.endswith(".py")]

    not_to_deploy = ["xfce_init"]

    for script in not_to_deploy:
        scripts.remove(script)

    for script in scripts:
        script_tgt = f"{os.path.join(src, script)}.py"
        script_lnk = f"{os.path.join(tgt, script)}"

        toolz.file.symlink_force(script_tgt, script_lnk)

        print(f"{done} '{script}' deployed in '/usr/local/bin'")

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

    src = os.path.dirname(os.path.realpath(__file__))
    tgt = "/usr/local/bin"

    deploy_scripts(src, tgt)
