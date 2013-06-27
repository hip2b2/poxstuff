#!/usr/bin/python
# Copyright 2012 William Yu
# wyu@ateneo.edu
# 
# Sample network for creating an OpenFlow Static Router.
#
# This is a demonstration file aims to build a simple static router.
# Network A (192.168.1.0/26) 
# <--> Switch
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

    # Creating links between nodes in network.
    h0int, s0int = createLink(h0, s0)
    h1int, s0int = createLink(h1, s0)

    # Configuration of IP addresses in interfaces
    h0.setIP(h0int, '192.168.1.2', 26)
    h1.setIP(h1int, '192.168.1.66', 26)

    info( '*** Network state:\n' )
    for node in s0, h0, h1:
        info( str( node ) + '\n' )

    # Start command line 
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    createStaticRouterNetwork()
