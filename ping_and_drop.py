#!/usr/bin/python
# wyu@ateneo.edu

# import libraries
from mininet.net import Mininet
from mininet.node import RemoteController
import thread
import time

# ping forever function
def ping_thread (threadName, src, dst):
  while (1):
    time.sleep(1)
    print src.cmd('ping -c1 %s' % dst.IP())

# setup mininet network
net = Mininet()
c0 = net.addController('c0')
s0 = net.addSwitch('s0')
h0 = net.addHost('h0')
h1 = net.addHost('h1')
net.addLink(s0, h0) 
net.addLink(s0, h1)

# start network and test
net.start()

# do the actual test and run forever
thread.start_new_thread(ping_thread, ("pinging thread", h0, h1))

# wait 10 seconds before killing the network
time.sleep(10)
net.configLinkStatus("s0", "h1", "down")

# stop network
net.stop()
