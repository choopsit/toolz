#!/usr/bin/env python3

import sys
import re
import os
import subprocess
import socket
import fcntl
import struct

__description__ = "Show network informations"
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
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help\n")
    exit(err_code)


def get_host_info():
    my_hostname = socket.gethostname()
    print(f"{ci}Hostname{c0}: {my_hostname}")

    my_fqdn = socket.getfqdn()

    if my_fqdn != my_hostname:
        print(f"{ci}FQDN{c0}: {my_fqdn}")


def get_mtu(ifname):
    return open(f"/sys/class/net/{ifname}/mtu").readline().rstrip("\n")


def get_mac(ifname):
    return open(f"/sys/class/net/{ifname}/address").readline().rstrip("\n")


def get_ip(ifname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd = sock.fileno()
    SIOCGIFADDR = 0x8915

    ifreq = struct.pack('16sH14s', ifname.encode('utf-8'), socket.AF_INET,
                        b'\x00'*14)

    try:
        res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
    except:
        return None

    ip = struct.unpack('16sH2x4s8x', res)[2]

    return socket.inet_ntoa(ip)


def get_gw():
    get_gw_cmd = "ip r | grep default | awk '{print $3}'"

    return os.popen(get_gw_cmd).read().rstrip("\n")


def get_dns():
    get_dns_cmd = "dig | awk -F'(' '/SERVER:/{print $2}' | sed 's/.$//'"

    return os.popen(get_dns_cmd).read().rstrip(")\n")


def list_ifaces():
    if_list = os.listdir('/sys/class/net/')

    for iface in if_list:
        if not re.match('^(lo|vif.*|virbr.*-.*|vnet.*)$', iface):
            print(f"{ci}Interface{c0}: {iface}")
            mtu = get_mtu(iface)
            print(f"  - {ci}MTU{c0}:         {mtu}")
            macaddr = get_mac(iface)
            print(f"  - {ci}MAC address{c0}: {macaddr}")
            ipaddr = get_ip(iface)
            print(f"  - {ci}IP address{c0}:  {ipaddr}")

    gw = get_gw()
    print(f"{ci}Gateway{c0}:         {gw}")

    nameserver = get_dns()
    print(f"{ci}DNS nameserver{c0}:  {nameserver}")
    print()


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["-h","--help"]):
        usage()
    elif len(sys.argv) > 1:
        print(f"{error} Bad argument")
        usage(1)

    get_host_info()
    list_ifaces()
