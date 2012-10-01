#!/usr/bin/python
# Copyright 2012 William Yu
# wyu@ateneo.edu
# 
# Sample network for creating an OpenFlow Static Router.
#
# This is a demonstration file aims to build a simple static router.
# Network A (192.168.1.0/26) 
# <--> Router A (192.168.1.1, 192.168.1.129)
# <--> Router B (192.168.1.65, 192.168.1.130)
# <--> Network B (192.168.1.64/26)
#

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.util import createLink

def createStaticRouterNetwork():
    info( '*** Creating network for Static Router Example\n' )

    # Create an empty network.
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)
    net.addController('c0')

    # Creating nodes in the network.
    h0 = net.addHost('h0')
    s0 = net.addSwitch('s0')
    h1 = net.addHost('h1')
    s1 = net.addSwitch('s1')

    # Creating links between nodes in network.
    h0int, s0int = createLink(h0, s0)
    h1int, s1int = createLink(h1, s1)
    s0pint, s1pint = createLink(s0, s1)

    # Configuration of IP addresses in interfaces
    s0.setIP(s0int, '192.168.1.1', 26)
    h0.setIP(h0int, '192.168.1.2', 26)
    s1.setIP(s1int, '192.168.1.65', 26)
    h1.setIP(h1int, '192.168.1.66', 26)
    s0.setIP(s0pint, '192.168.1.129', 26)
    s1.setIP(s1pint, '192.168.1.130', 26)

    info( '*** Network state:\n' )
    for node in s0, s1, h0, h1:
        info( str( node ) + '\n' )

    # Start command line 
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    createStaticRouterNetwork()
