#!/usr/bin/env python3

import sys
import re
import os
import subprocess
import pathlib
import getpass
import datetime
import time

import toolz

__description__ = "Make 'transmission-cli' manipulations simplified"
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
    print(f"  {my_script} [OPTION]")
    print(f"  {ci}if no option{c0}: Show queue evolution refreshing every 2s")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help:          Print this help")
    print(f"  -a,--add <TORRENT>: Add <TORRENT> to queue")
    print(f"  -A,--add-all:       Add all torrents from ~/Downloads to queue")
    print(f"  -d,--delete <ID>:   Remove torrent with queue-id <ID>", end=" ")
    print(f"and delete downloaded content")
    print(f"  -D,--delete-all:    Remove all torrents from queue and", end=" ")
    print(f"delete downloaded content")
    print(f"  -r,--restart:       Restart daemon")
    print(f"  -s,--status:        Daemon status")
    print(f"  -t,--test-port:     Test port\n")
    exit(err_code)


def show_queue():
    while True:
        try:
            os.system("clear")

            timenow = datetime.datetime.today().strftime("%a %b %d, %H:%M:%S")

            print(f"{ci}Transmission queue{c0} - {ci}{timenow}{c0}")

            torrent_queue = os.popen("transmission-remote -l").read()
            cl = "\33[36m"

            for line in torrent_queue.split("\n"):
                print(f"{cl}{line}{c0}")
                cl = "\33[0m"

            print(f"\n{cw}Press [Ctrl]+[C] to quit{c0}")
            time.sleep(2)
        except KeyboardInterrupt:
            print()
            exit(0)


def test_torrentfile(my_file):
    if os.path.isfile(my_file) and my_file.endswith(".torrent"):
        return True
    else:
        print(f'{error} "{my_file}" is not a valid torrent file\n')
        exit(1)


def add_one(torrent):
    tname = os.path.basename(torrent.rsplit('.', 1)[0])

    print(f"{ci}Adding '{tname}'...{c0}")

    os.system(f'transmission-remote -a "{torrent}"')

    print(f"{done} '{torrent}' added to queue")

    os.remove(torrent)


def add_all():
    tlist = []
    dlfolder = f"{home}/Downloads"

    for myfile in os.listdir(dlfolder):
        test_myfile = os.path.isfile(f"{dlfolder}/{myfile}")

        if test_myfile and myfile.endswith(".torrent"):
            tlist.append(f"{dlfolder}/{myfile}")

    if tlist != []:
        for new_torrent in tlist:
            add_one(new_torrent)
    else:
        print(f'{error} No torrent file in "~/Downloads"\n')
        exit(1)

    print()


def test_torrentid(my_id):
    ret = False
    tidcheck_cmd = f"transmission-remote -l"
    tidinfo = os.popen(tidcheck_cmd).read()

    for line in tidinfo.split("\n"):
        if re.match(f"\s+{my_id}\s.*", line):
            ret = True

    return ret


def remove_one(tid):
    tname = ""

    get_id_cmd = f'transmission-remote -t {tid} -i'
    tinfo = os.popen(get_id_cmd).read()

    for line in tinfo.split("\n"):
        if "Name:" in line:
            tname = " ".join(line.split()[1:])

    if tname != "":
        print(f'{ci}Removing "{tname}"...{c0}')

        if os.system(f"transmission-remote -t {tid} -rad") == 0:
            print(f'{done} "{tid}: {tname}" removed from queue')

            if toolz.yesno("Restart daemon to reorder IDs"):
                restart_daemon()
        else:
            print(f'{error} Failed to remove "{tid}: {tname}"\n')
    else:
        print(f"{error} No torrent with ID {tid}\n")


def remove_all():
    for tid in os.popen("transmission-remote -l").read():
        if type(tid) == int:
            remove_one(tid)

    print()


def restart_daemon():
    high = ""
    if toolz.user.is_in_group(os.getlogin(), "sudo"):
        high = "sudo "
    elif os.getuid() != 0:
        pass
    else:
        print(f"{error} '{my_user}' can not restart transmission-daemon\n")

    print(f"{ci}Restarting daemon...{c0}")

    if os.system(f"{high}systemctl restart transmission-daemon") == 0:
        print(f"{done} transmission-daemon restarted\n")
    else:
        print(f"{error} Failed to restart transmission-daemon")


def daemon_status():
    print(f"{ci}Daemon status{c0}:")
    os.system("systemctl status transmission-daemon")


def test_port():
    tsm_conf = f"{home}/.config/transmission-daemon/settings.json"

    if not os.path.isfile(tsm_conf):
        print(f"{error} Can not find transmission-daemon configuration file\n")
        exit(1)

    port = ""

    with open(tsm_conf, "r") as f:
        for line in f:
            if '"peer-port":' in line:
                port = line.split()[1].strip(',')

    if port != "":
        print(f"{ci}Transmission-daemon status{c0}:")
        print(f"{ci}Testing port '{cw}{port}{ci}'...{c0}")
        os.system("transmission-remote -pt")
        print()
    else:
        print(f"{error} Can not find port in transmission-daemon config\n")
        exit(1)


my_user = getpass.getuser()
home = pathlib.Path.home()

if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    else:
        req_pkgs = ["transmission-daemon"]
        toolz.pkg.prerequisites(req_pkgs)

        if len(sys.argv) == 1:
            show_queue()
        elif len(sys.argv) == 2:
            if sys.argv[1] in ["-A", "--add-all"]:
                add_all()
            elif sys.argv[1] in ["-D", "--delete-all"]:
                remove_all()
            elif sys.argv[1] in ["-r", "--restart"]:
                restart_daemon()
            elif sys.argv[1] in ["-s", "--status"]:
                daemon_status()
            elif sys.argv[1] in ["-t", "--test-port"]:
                test_port()
        elif len(sys.argv) == 3:
            if sys.argv[1] in ["-a", "--add"] and test_torrentfile(sys.argv[2]):
                add_one(sys.argv[2])
                print()
            elif sys.argv[1] in ["-d", "--delete"] and \
                    test_torrentid(sys.argv[2]):
                remove_one(sys.argv[2])
                print()
        else:
            print(f"{error} Bad argument\n")
            usage(1)
