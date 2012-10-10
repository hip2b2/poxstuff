#!/usr/bin/python
# Copyright 2012 James McCauley, William Yu
# wyu@ateneo.edu
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX. If not, see <http://www.gnu.org/licenses/>.
#

"""
This is a demonstration file that has various switch implementations.
The first example is a basic "all match" switch followed by a 
destination match, pair match then finally a more ideal pair match 
switch.

Mininet: sudo mn --topo single,3 --mac --switch ovsk --controller remote
Command Line: ./pox.py log.level --DEBUG samples.of_sw_tutorial

THIS VERSION SUPPORT resend() functionality in the betta branch POX.
"""

# These next two imports are common POX convention
from pox.core import core
import pox.openflow.libopenflow_01 as of

# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()

# This table maps (switch,MAC-addr) pairs to the port on 'switch' at
# which we last saw a packet *from* 'MAC-addr'.
# (In this case, we use a Connection object for the switch.)
table = {}

# Method for just sending a packet to any port (broadcast by default)
def send_packet (event, dst_port = of.OFPP_ALL):
  msg = of.ofp_packet_out(in_port=event.ofp.in_port)
  if event.ofp.buffer_id != -1 and event.ofp.buffer_id is not None:
    msg.buffer_id = event.ofp.buffer_id
  else:
    if event.ofp.data:
      return
    msg.data = event.ofp.data
  msg.actions.append(of.ofp_action_output(port = dst_port))
  event.connection.send(msg)

# Optimal method for resending a packet
def resend_packet (event, dst_port = of.OFPP_ALL):
  msg = of.ofp_packet_out(data = event.ofp)
  msg.actions.append(of.ofp_action_output(port = dst_port))
  event.connection.send(msg)

# DUMB HUB Implementation
# This is an implementation of a broadcast hub but all packets go 
# to the controller since no flows are installed.
def _handle_dumbhub_packetin (event):
  # Just send an instruction to the switch to send packet to all ports
  packet = event.parsed
  resend_packet(event, of.OFPP_ALL)

  log.debug("Broadcasting %s.%i -> %s.%i" %
    (packet.src, event.ofp.in_port, packet.dst, of.OFPP_ALL))

# PAIR-WISE MATCHING HUB Implementation
# This is an implementation of a broadcast hub with flows installed.
def _handle_pairhub_packetin (event):
  packet = event.parsed

  # Create flow that simply broadcasts any packet received
  msg = of.ofp_flow_mod()
  msg.data = event.ofp
  msg.idle_timeout = 10
  msg.hard_timeout = 30
  msg.match.dl_src = packet.src
  msg.match.dl_dst = packet.dst
  msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
  event.connection.send(msg)

  log.debug("Installing %s.%i -> %s.%i" %
    (packet.src, event.ofp.in_port, packet.dst, of.OFPP_ALL))

# LAZY HUB Implementation (How hubs typically are)
# This is an implementation of a broadcast hub with flows installed.
def _handle_lazyhub_packetin (event):
  packet = event.parsed

  # Create flow that simply broadcasts any packet received
  msg = of.ofp_flow_mod()
  msg.data = event.ofp
  msg.idle_timeout = 10
  msg.hard_timeout = 30
  msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
  event.connection.send(msg)

  log.debug("Installing %s.%i -> %s.%i" %
    ("ff:ff:ff:ff:ff:ff", event.ofp.in_port, "ff:ff:ff:ff:ff:ff", of.OFPP_ALL))

# BAD SWITCH Implementation
# This is an obvious but problematic implementation of switch that
# routes based on destination MAC addresses. 
def _handle_badswitch_packetin (event):
  packet = event.parsed

  # Learn the source and fill up routing table
  table[(event.connection,packet.src)] = event.port

  # install appropriate flow rule when learned
  msg = of.ofp_flow_mod()
  msg.idle_timeout = 10
  msg.hard_timeout = 30
  msg.match.dl_dst = packet.src
  msg.actions.append(of.ofp_action_output(port = event.port))
  event.connection.send(msg)

  log.debug("Installing %s.%i -> %s.%i" %
    ("ff:ff:ff:ff:ff:ff", event.ofp.in_port, packet.src, event.port))

  # determine if appropriate destination route is available
  dst_port = table.get((event.connection,packet.dst))

  if dst_port is None:
    # We don't know where the destination is yet. So, we'll just
    # send the packet out all ports (except the one it came in on!)
    # and hope the destination is out there somewhere. :)
    # To send out all ports, we can use either of the special ports
    # OFPP_FLOOD or OFPP_ALL. We'd like to just use OFPP_FLOOD,
    # but it's not clear if all switches support this. :(
    resend_packet(event, of.OFPP_ALL)

    log.debug("Broadcasting %s.%i -> %s.%i" %
      (packet.src, event.ofp.in_port, packet.dst, of.OFPP_ALL))
  else:   
    # This is the packet that just came in -- we want send the packet
    # if we know the destination.
    resend_packet(event, dst_port)

    log.debug("Sending %s.%i -> %s.%i" %
      (packet.src, event.ofp.in_port, packet.dst, dst_port))

# PAIR-WISE MATCH SWITCH Implementation
# This is an implementation of an pair match switch. This only matches
# source and destination MAC addresses. Whenever a new source 
# destination MAC address is detected it then add a new flow 
# identifying the source destination pair. The routing table is updated
# using the detected destination MAC address to the destination port.
def _handle_pairswitch_packetin (event):
  packet = event.parsed

  # Learn the source and fill up routing table
  table[(event.connection,packet.src)] = event.port
  dst_port = table.get((event.connection,packet.dst))

  if dst_port is None:
    # We don't know where the destination is yet. So, we'll just
    # send the packet out all ports (except the one it came in on!)
    # and hope the destination is out there somewhere. :)
    # To send out all ports, we can use either of the special ports
    # OFPP_FLOOD or OFPP_ALL. We'd like to just use OFPP_FLOOD,
    # but it's not clear if all switches support this. :(
    resend_packet(event, of.OFPP_ALL)

    log.debug("Broadcasting %s.%i -> %s.%i" %
      (packet.src, event.ofp.in_port, packet.dst, of.OFPP_ALL))
  else:   
    # This is the packet that just came in -- we want to
    # install the rule and also resend the packet.
    msg = of.ofp_flow_mod()
    msg.data = event.ofp
    msg.idle_timeout = 10
    msg.hard_timeout = 30
    msg.match.dl_src = packet.src
    msg.match.dl_dst = packet.dst
    msg.actions.append(of.ofp_action_output(port = dst_port))
    event.connection.send(msg)

    log.debug("Installing %s.%i -> %s.%i" %
      (packet.src, event.ofp.in_port, packet.dst, dst_port))

# SMARTER PAIR-WISE MATCH SWITCH Implementation
# This is an implementation of an ideal pair switch. This optimizes the
# previous example by adding both direction in one entry.
def _handle_idealpairswitch_packetin (event):
  packet = event.parsed

  # Learn the source and fill up routing table
  table[(event.connection,packet.src)] = event.port
  dst_port = table.get((event.connection,packet.dst))

  if dst_port is None:
    # We don't know where the destination is yet. So, we'll just
    # send the packet out all ports (except the one it came in on!)
    # and hope the destination is out there somewhere. :)
    # To send out all ports, we can use either of the special ports
    # OFPP_FLOOD or OFPP_ALL. We'd like to just use OFPP_FLOOD,
    # but it's not clear if all switches support this. :(
    resend_packet(event, of.OFPP_ALL)

    log.debug("Broadcasting %s.%i -> %s.%i" %
      (packet.src, event.ofp.in_port, packet.dst, of.OFPP_ALL))
  else:
    # Since we know the switch ports for both the source and dest
    # MACs, we can install rules for both directions.
    msg = of.ofp_flow_mod()
    msg.idle_timeout = 10
    msg.hard_timeout = 30
    msg.match.dl_dst = packet.src
    msg.match.dl_src = packet.dst
    msg.actions.append(of.ofp_action_output(port = event.port))
    event.connection.send(msg)
    
    # This is the packet that just came in -- we want to
    # install the rule and also resend the packet.
    msg = of.ofp_flow_mod()
    msg.data = event.ofp
    msg.idle_timeout = 10
    msg.hard_timeout = 30
    msg.match.dl_src = packet.src
    msg.match.dl_dst = packet.dst
    msg.actions.append(of.ofp_action_output(port = dst_port))
    event.connection.send(msg)

    log.debug("Installing %s.%i -> %s.%i AND %s.%i -> %s.%i" %
      (packet.dst, dst_port, packet.src, event.ofp.in_port,
      packet.src, event.ofp.in_port, packet.dst, dst_port))


# function that is invoked upon load to ensure that listeners are
# registered appropriately. Uncomment the hub/switch you would like 
# to test. Only one at a time please.
def launch ():
  #core.openflow.addListenerByName("PacketIn", _handle_dumbhub_packetin)
  #core.openflow.addListenerByName("PacketIn", _handle_pairhub_packetin)
  #core.openflow.addListenerByName("PacketIn", _handle_lazyhub_packetin)
  #core.openflow.addListenerByName("PacketIn", _handle_badswitch_packetin)
  #core.openflow.addListenerByName("PacketIn", _handle_pairswitch_packetin)
  core.openflow.addListenerByName("PacketIn", 
    _handle_idealpairswitch_packetin)

  log.info("Switch Tutorial is running.")
