#!/usr/bin/env python3

from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# Network general options
net.setLogLevel('info')
net.enableCli()

switch_count = 10

for i in range(switch_count):
    sw = 's' + str(i + 1)
    h = 'h' + str(i + 1)
    net.addP4Switch(sw)
    net.setP4Source(sw,'data/stp.p4')
    net.addHost(h)
    net.addLink(sw, h)

for i in range(switch_count):
    net.addLink("s" + str(i + 1), "s" + str((i + 1) % switch_count + 1))

for i in range(2, switch_count // 2):
    net.addLink("s" + str(i), "s" + str(switch_count - i + 1))

# Assignment strategy
net.l2()

# Nodes general options
net.enableCpuPortAll()
net.enablePcapDumpAll()
net.disableArpTables()
net.enableLogAll()

# Start network
net.startNetwork()
