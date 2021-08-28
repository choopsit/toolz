#!/usr/bin/env python3

import sys
import os

__description__ = "Show help for scripts deployed from 'choopsit/playground'"
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
    print(f"  -h,--help: Print this help\n")
    exit(errcode)


def print_help():
    cs = "\33[33m"
    for script in sorted(os.listdir("/usr/local/bin")):
        okscript = False
        okhelp = False
        if os.path.isdir(script):
            continue
        with open(f"/usr/local/bin/{script}", "r") as f:
            for line in f:
                if line.startswith("#!/"):
                    language = line.split()[1]
                    if language.endswith("sh"):
                        cl = "\33[37m"
                    elif language.startswith("python"):
                        cl = "\33[94m"
                    else:
                        cl = "\33[35m"
                if line.startswith("__author__") and "Choops" in line:
                    okscript = True
                if "-h,--help:" in line:
                    okhelp = True
        if okscript and okhelp:
            print(f"{cs}{script}{c0} [{cl}{language}{c0}]:")
            os.system(f"{script} -h")


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument\n")
        usage(1)


    print_help()
