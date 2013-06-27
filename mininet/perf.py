#!/usr/bin/python
# Mininet Example Copyright 2012 William Yu
# wyu@ateneo.edu

from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI

net = Mininet(host=CPULimitedHost, link=TCLink)

c0 = net.addController()
s0 = net.addSwitch('s0')
h0 = net.addHost('h0', cpu=0.5)
h1 = net.addHost('h1')
h2 = net.addHost('h2')

net.addLink(h0, s0, bw=10, delay='5ms', max_queue_size=1000, loss=10, use_htb=True)
net.addLink(h1, s0)
net.addLink(h2, s0)

net.start()
net.pingAll()
CLI(net)
net.stop()
