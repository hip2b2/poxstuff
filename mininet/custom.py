#!/usr/bin/python
# Mininet Example Copyright 2012 William Yu
# wyu@ateneo.edu

from mininet.net import Mininet
from mininet.cli import CLI
net = Mininet()

# Creating nodes in the network.
c0 = net.addController()
h0 = net.addHost('h0')
s0 = net.addSwitch('s0')
h1 = net.addHost('h1')

# Creating links between nodes in network
net.addLink(h0, s0)
net.addLink(h1, s0)

# Configuration of IP addresses in interfaces
h0.setIP('192.168.1.1', 24)
h1.setIP('192.168.1.2', 24)

net.start()
net.pingAll()
CLI(net)
net.stop()

