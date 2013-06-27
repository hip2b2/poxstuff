#!/usr/bin/python
# Mininet Example Copyright 2012 William Yu
# wyu@ateneo.edu

from mininet.net import Mininet
from mininet.util import createLink

net = Mininet(host=CPULimitedHost, link=TCLink)

s0 = net.addSwitch('s0')
h0 = net.addHost('h0')
h1 = net.addHost('h1', cpu=0.5)

net.addLink(s0, h0, bw=10, delay='5ms', max_queue_size=1000, loss=10, use_htb=True)

net.start()
net.pingAll()
net.stop()
