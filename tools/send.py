#!/usr/bin/env python
import sys
import socket
import random
from subprocess import Popen, PIPE
import re

from scapy.all import sendp, get_if_list, get_if_hwaddr, raw, Ether
from packets import BPDU

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():
    iface = get_if()
    print("Sending on interface %s to %s" % (iface, str()))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='01:81:c2:00:00:00') / BPDU(type=0, root_priority=0, root_mac='00:00:00:00:00:00', root_cost=0, bridge_priority=0, bridge_mac='00:00:00:00:00:00', flags=0)
    pkt.show()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
