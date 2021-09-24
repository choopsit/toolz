#!/usr/bin/env python3

import os
import sys
import re
import shutil
import pathlib

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
    myscript = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  './{myscript} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(errcode)


def overwrite(src, tgt):
    """Overwrite file or folder"""

    if os.path.isdir(src):
        if os.path.isdir(tgt):
            shutil.rmtree(tgt)

        try:
            shutil.copytree(src, tgt, symlinks=True)
        except EnvironmentError:
            return False
    else:
        if os.path.exists(tgt):
            os.remove(tgt)

        try:
            shutil.copy(src, tgt, follow_symlinks=False)
        except EnvironmentError:
            return False

    return True


def deploy_lib(src, mylib):
    lib_src = os.path.join(src, mylib)

    _USERNAME = os.getenv("SUDO_USER") or os.getenv("USER")
    _HOME = os.path.expanduser(f"~{_USERNAME}")

    bashrc = f"{_HOME}/.config/bash/bashrc"
    tmp_file = "/tmp/bashrc"

    overwrite(bashrc, tmp_file)

    _GROUP = pathlib.Path(bashrc).group()

    if not os.path.isfile(bashrc):
        bashrc =f"{_HOME}/.bashrc"

    with open(tmp_file, "r") as f:
        bashrc_content = f.read()
        if "PYTHONPATH" in bashrc_content and src not in bashrc_content:
            with open (tmp_file, "r") as oldf, open(bashrc, "w") as newf:
                print("Editing bashrc")
                for line in oldf:
                    if line.startswith("export PYTHONPATH"):
                        oldline = line.strip('\n')
                        newline = f"{oldline}:{src}\n"
                        newf.write(newline)
                    else:
                        newf.write(line)
        elif "PYTHONPATH" not in bashrc_content:
            with open(bashrc, "a") as newf:
                print("Expanding bashrc")
                newline = f"\nexport PYTHONPATH={src}\n"
                newf.write(newline)

        shutil.chown(bashrc, _USERNAME, _GROUP)


def deploy_scripts(src, tgt):
    scripts = [f.replace(".py", "") for f in os.listdir(src) if f.endswith(".py")]

    for not_to_deploy in ["deploy_toolz", "xfce_init"]:
        scripts.remove(not_to_deploy)
        print(f"{warning} '{not_to_deploy}.py' not deployed")

    for script in scripts:
        if overwrite(f"{src}/{script}.py", f"{tgt}/{script}"):
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

    src = os.path.dirname(os.path.realpath(__file__))
    tgt = "/usr/local/bin"

    mylib = "toolz"

    deploy_lib(src, mylib)
    deploy_scripts(src, tgt)
