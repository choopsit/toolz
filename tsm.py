#!/usr/bin/env python3

import sys
import re
import os
import subprocess
import pathlib
import getpass
import datetime
import time
import toolzlib

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


def usage(errcode=0):
    myscript = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  {myscript} [OPTION]")
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
    exit(errcode)


def show_queue():
    while True:
        try:
            os.system("clear")
            timenow = datetime.datetime.today().strftime("%a %b %d, %H:%M:%S")
            print(f"{ci}Transmission queue{c0} - {ci}{timenow}{c0}")
            torrentqueue = os.popen("transmission-remote -l").read()
            cl = "\33[36m"
            for line in torrentqueue.split("\n"):
                print(f"{cl}{line}{c0}")
                cl = "\33[0m"
            print(f"\n{cw}Press [Ctrl]+[C] to quit{c0}")
            time.sleep(2)
        except KeyboardInterrupt:
            print()
            exit(0)


def test_torrentfile(myfile):
    if os.path.isfile(myfile) and myfile.endswith(".torrent"):
        return True
    else:
        print(f'{error} "{myfile}" is not a valid torrent file')
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
        testmyfile = os.path.isfile(f"{dlfolder}/{myfile}")
        if testmyfile and myfile.endswith(".torrent"):
            tlist.append(f"{dlfolder}/{myfile}")

    if tlist != []:
        for newtorrent in tlist:
            add_one(newtorrent)
    else:
        print(f'{error} No torrent file in "~/Downloads"')
        exit(1)


def test_torrentid(myid):
    ret = False
    tidcheck_cmd = f"transmission-remote -l"
    tidinfo = os.popen(tidcheck_cmd).read()
    for line in tidinfo.split("\n"):
        if re.match(f"\s+{myid}\s.*", line):
            ret = True

    return ret


def remove_one(tid):
    tname = ""

    getid_cmd = f'transmission-remote -t {tid} -i'
    tinfo = os.popen(getid_cmd).read()
    for line in tinfo.split("\n"):
        if "Name:" in line:
            tname = " ".join(line.split()[1:])

    if tname != "":
        print(f'{ci}Removing "{tname}"...{c0}')
        if os.system(f"transmission-remote -t {tid} -rad") == 0:
            print(f'{done} "{tid}: {tname}" removed from queue')
            if toolzlib.yesno("Restart daemon to reorder IDs"):
                restart_daemon()
        else:
            print(f'{error} Failed to remove "{tid}: {tname}"')
    else:
        print(f"{error} No torrent with ID {tid}")


def remove_all():
    for tid in os.popen("transmission-remote -l").read():
        if type(tid) == int:
            remove_one(tid)


def restart_daemon():
    if toolzlib.user.is_in_group(os.getlogin(), "sudo"):
        print(f"{ci}Restarting daemon...{c0}")
        if os.system("sudo systemctl restart transmission-daemon") == 0:
            print(f"{done} transmission-daemon restarted")
    else:
        print(f"{error} '{myuser}' can not restart transmission-daemon")


def daemon_status():
    print(f"{ci}Daemon status{c0}:")
    os.system("systemctl status transmission-daemon")


def test_port():
    tsmconf = f"{home}/.config/transmission-daemon/settings.json"

    if not os.path.isfile(tsmconf):
        print(f"{error} Can not find transmission-daemon configuration file")
        exit(1)

    port = ""
    with open(tsmconf, "r") as f:
        for line in f:
            if '"peer-port":' in line:
                port = line.split()[1].strip(',')

    if port != "":
        print(f"{ci}Transmission-daemon status{c0}:")
        print(f"{ci}Testing port '{port}'...{c0}")
        os.system("transmission-remote -pt")
        print()
    else:
        print(f"{error} Can not find port in transmission-daemon config\n")
        exit(1)


def do_action(myid, myargid):
    if myid == 0:
        show_queue()
    elif myid == 1:
        if test_torrentfile(sys.argv[myargid]):
            add_one(sys.argv[myargid])
    elif myid == 2:
        add_all()
    elif myid == 3:
        if test_torrentid(myargid):
            remove_one(sys.argv[myargid])
    elif myid == 4:
        remove_all()
    elif myid == 5:
        restart_daemon()
    elif myid == 6:
        daemon_status()
    elif myid == 7:
        test_port()


myuser = getpass.getuser()
home = pathlib.Path.home()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        actionid = 0
        argid = 0

    i = 1
    positionals = []
    delay = 10
    while i < len(sys.argv):
        argid = 0
        if re.match('^-(h|-help)', sys.argv[i]):
            usage()
        elif re.match('^-(a|-add)', sys.argv[i]):
            actionid = 1
            argid = i + 1
            i += 1
        elif re.match('^-(A|-add-all)', sys.argv[i]):
            actionid = 2
        elif re.match('^-(d|-delete)', sys.argv[i]):
            actionid = 3
            argid = i + 1
            i += 1
        elif re.match('^-(D|-delete-all)', sys.argv[i]):
            actionid = 4
        elif re.match('^-(r|-restart)', sys.argv[i]):
            actionid = 5
        elif re.match('^-(s|-status)', sys.argv[i]):
            actionid = 6
        elif re.match('^-(t|-test-port)', sys.argv[i]):
            actionid = 7
        elif re.match('^-', sys.argv[i]):
            print(f"{error} Unknow option '{sys.argv[i]}'\n")
            usage(1)
        else:
            positionals.append(sys.argv[i])
        i += 1

    if len(positionals) > 0:
        badargs = ", ".join(positionals)
        print(f"{error} Unhandled arguments '{badargs}'")
        usage(1)

    if len(sys.argv) > 3:
        print(f"{error} Too many arguments")
        usage(1)

    reqpkgs = ["transmission-daemon"]
    toolzlib.pkg.prerequisites(reqpkgs)

    do_action(actionid, argid)
