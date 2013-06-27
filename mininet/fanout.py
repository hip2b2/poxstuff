#!/usr/bin/python
# Mininet Example Copyright 2012 William Yu
# wyu@ateneo.edu

from mininet.net import Mininet
from mininet.topolib import TreeTopo
Tree22 = TreeTopo(depth=2, fanout=2)
net = Mininet(topo=Tree22)
net.start()
net.pingAll()
net.stop()
