#!/usr/bin/env python3

import os
import sys
import re
import shutil
import tempfile

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


def deploy_lib(lib_src):
    env_file = "/etc/environment"
    tmp_file = "/tmp/environment"

    overwrite(env_file, tmp_file)

    with open(tmp_file, "r") as f:
        my_env = f.read()
        if "PYTHONPATH" not in my_env:
            print(f"{done} PYTHONPATH set\n")

            with open(env_file, "a") as newf:
                newf.write(f"PYTHONPATH={lib_src}")
        elif lib_src not in my_env:
            print(f"{done} PYTHONPATH updated")

            with open(tmp_file, "r") as oldf, open(env_file, "w") as newf:
                for line in oldf:
                    if "PYTHONPATH" in line:
                        old_line = line.strip("\n")
                        newf.write(f"{old_line}:{lib_src}")
                    else:
                        newf.write(line)
        else:
            print(f"{done} PYTHONPATH already up to date")


def symlink_force(target, link_name):
    link_dir = os.path.dirname(link_name)

    while True:
        temp_link_name = tempfile.mktemp(dir=link_dir)
        try:
            os.symlink(target, temp_link_name)
            break
        except FileExistsError:
            pass
    try:
        os.replace(temp_link_name, link_name)
    except OSError:
        os.remove(temp_link_name)
        raise


def deploy_scripts(src, tgt):
    scripts = [f.replace(".py", "") for f in os.listdir(src) if f.endswith(".py")]

    not_to_deploy = ["xfce_init"]

    for script in not_to_deploy:
        scripts.remove(script)

    for script in scripts:
        script_tgt = f"{os.path.join(src, script)}.py"
        script_lnk = f"{os.path.join(tgt, script)}"

        symlink_force(script_tgt, script_lnk)

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

    deploy_lib(src)
    deploy_scripts(src, tgt)
