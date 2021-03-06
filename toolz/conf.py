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

lib_folder = os.path.dirname(os.path.realpath(__file__))
conf_srcfolder = f"{lib_folder}/_resources"


def test_conf(conf_file, test_pattern):
    """
    Test if a line starts with a pattern in a configuration file
    """

    if os.path.isfile(conf_file):
        with open(conf_file, "r") as f:
            for line in f:
                if line.startswith(test_pattern):
                    return True

    return False


def swap():
    """
    Apply swap configuration
    """

    swap_conf = "/etc/sysctl.d/99-swappiness.conf"

    for swapok_pattern in ["vm.swappiness=5\n", "vm.vfs_cache_pressure=50\n"]:
        if not test_conf(swap_conf, swapok_pattern):
            with open(swap_conf, "a") as f:
                f.write(f"{swapok_pattern}\n")

    for swap_cmd in [f"sysctl -p {swap_conf}", "swapoff -av", "swapon -av"]:
        os.system(swap_cmd)


def ssh():
    """
    Apply ssh configuration: allow root login
    """

    ssh_conf_base = "/etc/ssh/sshd_config"
    ssh_conf_rootok = f"{sshconf_base}.d/allow_root.conf"

    rootok_pattern = "PermitRootLogin yes"

    if not test_conf(ssh_conf_base, rootok_pattern) and \
            not test_conf(ssh_conf_rootok, rootok_pattern):
        with open(ssh_conf_rootok, "a") as f:
            f.write("# Allow root user to connect on ssh\n")
            f.write(f"{rootok_pattern}\n")

        os.system("systemctl restart ssh")


def bash(home):
    """
    Apply bash configuration
    """

    bash_src = f"{conf_srcfolder}/bash"
    bash_cfg = f"{home}/.config/bash"

    file.overwrite(f"{bash_src}/profile", f"{home}/.profile")

    if not os.path.isdir(bash_cfg):
        os.makedirs(bash_cfg)

    old_bashrc = f"{home}/.bashrc"

    if os.path.isfile(old_bashrc):
        os.remove(old_bashrc)

    for bash_file in ["aliases", "history", "logout"]:
        bash_file_orig = f"{home}/.bash_{bash_file}"
        bash_file_tgt = f"{bash_cfg}/{bash_file}"

        if os.path.isfile(bash_file_orig):
            shutil.move(bash_file_orig, bash_file_tgt)

    if home == "/root":
        bashrc_src = f"{bash_src}/bashrc_root"
    else:
        bashrc_src = f"{bash_src}/bashrc_user"

    bashrc_tgt = f"{bash_cfg}/bashrc"

    file.overwrite(bashrc_src, bashrc_tgt)


def vim(home):
    """
    Apply vim configuration
    """

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
    plug_tgt = f"{plug_folder}/plug.vim"

    urllib.request.urlretrieve(plug_url, plug_tgt)

    if home == "/root":
        vimrc = f"{vim_cfg}/vimrc"
        tmp_file = "/tmp/vimrc"

        file.overwrite(vimrc, tmp_file)

        with open(tmp_file, "r") as oldf, open(vimrc, "w") as newf:
            for line in oldf:
                if not "gruvbox" in line:
                    newf.write(line)

        os.system("vim +PlugInstall +qall")


def root():
    """
    Apply 'root' configuration
    """

    bash("/root")
    vim("/root")
    os.system("update-alternatives --set editor /usr/bin/vim.basic")


def lightdm():
    """
    Make username choosable in a list in Display Manager
    """

    lightdm_conf = "/usr/share/lightdm/lightdm.conf.d/10_my.conf"
    tmp_file = "/tmp/lightdm_perso.conf"
    new_lines = ["[Seat:*]\n", "greeter-hide-users=false\n", "[Greeter]\n",
            "draw-user-backgrounds=true\n"]

    if os.path.isfile(lightdm_conf):
        file.overwrite(lightdm_conf, tmp_file)

        with open(tmp_file, "r") as oldf, open(lightdm_conf, "a") as newf:
            for line in new_lines:
                if line not in oldf:
                    newf.write(line)
    else:
        with open(lightdm_conf, "w") as f:
            for line in new_lines:
                f.write(line)


def networkmanager():
    """
    Make network-manager manage already configured interfaces without it
    """

    nw_conf = "/etc/network/interfaces"
    iface = os.popen("ip r | grep default").read().split()[4]
    tmp_file = "/tmp/interfaces"

    file.overwrite(nw_conf, tmp_file)

    with open(tmp_file, "r") as oldf, open(nw_conf, "w") as newf:
        for line in oldf:
            if iface in line:
                newf.write(f"#{line}")
            else:
                newf.write(line)


def pulseaudio():
    """
    Fix stupid default pulseaudio max volume on new application launch
    """

    pulse_conf = "/etc/pulse/daemon.conf"

    if not test_conf(pulse_conf, "flat-volumes = no"):
        tmp_file = "/tmp/pulse_daemon.conf"

        file.overwrite(pulse_conf, tmp_file)

        with open(tmp_file, "r") as oldf, open(pulse_conf, "w") as newf:
            for line in oldf:
                if "flat-volumes" in line:
                    newf.write("flat-volumes = no\n")
                else:
                    newf.write(line)


def redshift():
    """
    Link redshift to geoclue to follow local time
    """

    geoclue_conf = "/etc/geoclue/geoclue.conf"

    if not test_conf(geoclue_conf, "[redshift]"):
        with open(geoclue_conf, "a") as f:
            f.write("\n[redshift]\nallowed=true\nsystem=false\nusers=\n")


def transmissiond(user, home):
    """
    Deploy transmission-deamon configuration with {user} as daemon user
    """

    os.system("systemctl stop transmission-daemon")

    tsmd_service_dir = "/etc/systemd/system/transmission-daemon.service.d/"
    tsmd_service_conf = f"{tsmd_confdir}/override.conf"

    tsmd_conf_dir = f"{home}/.config/transmission-daemon"
    tsmd_conf_orig = "/var/lib/transmission-daemon/info/settings.json"
    tsmd_user_conf = f"{tsmd_conf_dir}/settings.json"
    tmp_file = "/tmp/tsmdsettings.json"

    sysctl_cmds = ["daemon-reload", "start transmission-daemon",
            "stop transmission-daemon"]

    if not os.path.isdir(tsmd_service_dir):
        os.makedirs(tsmd_service_dir)

    os.system(f"systemctl {sysctl_cmds[-1]}")

    with open(tsmd_service_conf, "w") as f:
        f.write(f"[Service]\nUser={user}\n")

    for sysctl_cmd in sysctl_cmds:
        os.system(f"systemctl {sysctl_cmd}")

    if not os.path.isdir(tsmd_conf_dir):
        os.makedirs(tsmd_conf_dir)

    if not os.path.isfile(tsmd_user_conf):
        shutil.copy(tsmd_conf_orig, tsmd_user_conf)

    file.overwrite(tsmd_user_conf, tmp_file)

    with open(tmp_file, "r") as oldf, open(tsmd_user_conf, "w") as newf:
        for line in oldf:
            if '"peer-port"' in line:
                newf.write('    "peer-port": 57413,\n')
            else:
                newf.write(line)

    for sysctl_cmd[:-1] in sysctl_cmds:
        os.system(f"systemctl {sysctl_cmd}")


def gruvbox_gtk():
    """
    Add gruvbox color scheme for gtk applications
    """

    gruvbox_styles = ["gruvbox-dark.xml", "gruvbox-light.xml"]

    for style in gruvbox_styles:
        style_url = "https://raw.githubusercontent.com/morhetz/"
        style_url += f"gruvbox-contrib/master/gedit/{style}"

        style_tgts = [f"/usr/share/gtksourceview-/styles/{style}"]
        style_tgts.append(style_tgts[0].replace("4", "5"))

        for style_tgt in style_tgts:
            if not os.path.exists(style_tgt):
                urllib.request.urlretrieve(style_url, style_tgt)
                print(f"{done} '{style}' deployed")


def xfce(home):
    """
    Apply default 'xfce' configuration for user
    """

    git_dir = f"{home}/Work/git"

    if not os.path.isdir(git_dir):
        os.makedirs(git_dir)

    conf_dict = {
            "Xfce": "xfce4",
            "Thunar": "Thunar",
            "Mousepad": "Mousepad",
            "Plank": "plank",
            "Autostarts": "autostart"
            }

    for soft, soft_conf in conf_dict.items():
        conf_src = f"{conf_srcfolder}/config/{soft_conf}"
        conf_tgt = f"{home}/.config/{soft_conf}"

        if not os.path.exists(conf_tgt):
            os.makedirs(conf_tgt)

        file.overwrite(conf_src, conf_tgt)

        print(f"{done} {soft} configuration deployed in '{home}/.config'")
