#!/usr/bin/python
# Copyright 2012 William Yu
# wyu@ateneo.edu
# 
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.util import createLink

def createDoubleControllerNetwork():
    info( '*** Creating network for Double Controller Example\n' )

    # Create an empty network.
    net = Mininet(switch=OVSKernelSwitch)
    c0 = net.addController('c0', controller=RemoteController, 
      defaultIP="127.0.0.1", port=6633)
    c1 = net.addController('c1', controller=RemoteController, 
      defaultIP="127.0.0.1", port=6644)

    # Creating nodes in the network.
    h0 = net.addHost('h0')
    h1 = net.addHost('h1')
    s0 = net.addSwitch('s0')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    s1 = net.addSwitch('s1')

    # Creating links between nodes in network.
    h0int, s0int = createLink(h0, s0)
    h1int, s0int = createLink(h1, s0)
    h2int, s1int = createLink(h2, s1)
    h3int, s1int = createLink(h3, s1)
    s0int, s1int = createLink(s0, s1)

    # Configuration of IP addresses in interfaces
    h0.setIP(h0int, '192.168.1.2', 26)
    h1.setIP(h1int, '192.168.1.3', 26)
    h2.setIP(h2int, '192.168.1.66', 26)
    h3.setIP(h3int, '192.168.1.67', 26)

    # Start network
    net.build()

    # Attaching Controllers to Switches
    s0.start([c0])
    s1.start([c1])

    # Setting interface only routes and not default routes
    h0.cmd("route del -net 0.0.0.0")
    h1.cmd("route del -net 0.0.0.0")
    h2.cmd("route del -net 0.0.0.0")
    h3.cmd("route del -net 0.0.0.0")
    h0.cmd("route add -net 192.168.1.0 netmask 255.255.255.192 " + h0int)
    h1.cmd("route add -net 192.168.1.0 netmask 255.255.255.192 " + h1int)
    h2.cmd("route add -net 192.168.1.64 netmask 255.255.255.192 " + h2int)
    h3.cmd("route add -net 192.168.1.64 netmask 255.255.255.192 " + h3int)

    # dump stuff on the screen
    info( '*** Network state:\n' )
    for node in c0, c1, s0, s1, h0, h1, h2, h3:
        info( str( node ) + '\n' )

    # Start command line 
    CLI(net)

    # Stop network
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    createDoubleControllerNetwork()
