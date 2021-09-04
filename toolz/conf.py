#!/usr/bin/env python3

import os
import shutil
import urllib.request
from . import file

__description__ = "Configuration management module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def test_conf(conf_file, test_pattern):
    if os.path.isfile(conf_file):
        with open(conf_file, "r") as f:
            for line in f:
                if line.startswith(test_pattern):
                    return True

    return False


def swap():
    """Apply swap configuration"""

    swap_conf = "/etc/sysctl.d/99-swappiness.conf"

    for swapok_pattern in ["vm.swappiness=5\n", "vm.vfs_cache_pressure=50\n"]:
        if not test_conf(swap_conf, swapok_pattern):
            with open(swap_conf, "a") as f:
                f.write(f"{swapok_pattern}\n")

    for swap_cmd in [f"sysctl -p {swap_conf}", "swapoff -av", "swapon -av"]:
        os.system(swap_cmd)


def ssh():
    """Apply ssh configuration: allow root login"""

    sshconf_base = "/etc/ssh/sshd_config"
    sshconf_rootok = f"{sshconf_base}.d/allow_root.conf"

    rootok_pattern = "PermitRootLogin yes"
    if not test_conf(sshconf_base, rootok_pattern) and \
            not test_conf(sshconf_rootok, rootok_pattern):
        with open(sshconf_rootok, "a") as f:
            f.write("# Allow root user to connect on ssh\n")
            f.write(f"{rootok_pattern}\n")

        os.system("systemctl restart ssh")


toolz_folder = os.path.dirname(os.path.realpath(__file__)) 
conf_srcfolder = f"{toolz_folder}/_resources"


def bash(home):
    """Apply bash configuration"""

    bash_src = f"{conf_srcfolder}/bash"
    bash_cfg = f"{home}/.config/bash"

    file.overwrite(f"{bash_src}/profile", f"{home}/.profile")

    if not os.path.isdir(bash_cfg):
        os.makedirs(bash_cfg)

    if os.path.isfile(f"{home}/.bashrc"):
        os.remove(f"{home}/.bashrc")

    for bash_file in ["aliases", "history", "logout"]:
        bash_file_orig = f"{home}/.bash_{bash_file}"
        if os.path.isfile(bash_file_orig):
            shutil.move(bash_file_orig, f"{bash_cfg}/{bash_file}")

    if home == "/root":
        bashrc_src = f"{bash_src}/bashrc_root"
    else:
        bashrc_src = f"{bash_src}/bashrc_user"

    file.overwrite(bashrc_src, f"{bash_cfg}/bashrc")


def vim(home):
    """Apply vim configuration"""

    vim_src = f"{conf_srcfolder}/vim"
    vim_cfg = f"{home}/.vim"

    for vim_oldfile in [f"{home}/.vimrc", f"{home}/.viminfo"]:
        if os.path.isfile(vim_oldfile):
            os.remove(vim_oldfile)

    if not os.path.isdir(vim_cfg):
        os.makedirs(vim_cfg)

    file.overwrite(vim_src, vim_cfg)

    plug_folder = f"{vim_cfg}/autoload"
    if not os.path.isdir(plug_folder):
        os.makedirs(plug_folder)

    rawgit_url = "https://raw.githubusercontent.com/"
    plug_url = f"{rawgit_url}junegunn/vim-plug/master/plug.vim"
    urllib.request.urlretrieve(plugurl, f"{plug_folder}/plug.vim")

    if home == "/root":
        os.system("vim +PlugInstall +qall")


def root():
    """Apply 'root' configuration"""

    bash("/root")
    vim("/root")
    os.system("update-alternatives --set editor /usr/bin/vim.basic")
