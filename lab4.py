#!/usr/bin/python
# Script setup lab 4 exercise
# wyu@ateneo.edu

# import libraries
from mininet.net import Mininet
from mininet.cli import CLI

# setup mininet network
net = Mininet()
c0 = net.addController('c0')
s0 = net.addSwitch('s0')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')
h0 = net.addHost('h0')
h1 = net.addHost('h1')
h2 = net.addHost('h2')
h3 = net.addHost('h3')
h4 = net.addHost('h4')
h5 = net.addHost('h5')
net.addLink(s0, h0)
net.addLink(s0, h1)
net.addLink(s1, h2)
net.addLink(s1, h3)
net.addLink(s2, h4)
net.addLink(s2, h5)

# start network and test
net.start()
CLI(net)
net.stop()
