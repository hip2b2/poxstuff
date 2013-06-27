#!/usr/bin/python
# Mininet Example Copyright 2012 William Yu
# wyu@ateneo.edu

from mininet.net import Mininet
from mininet.topo import LinearTopo
Linear4 = LinearTopo(k=4)
net = Mininet(topo=Linear4)
net.start()
net.pingAll()
net.stop()
