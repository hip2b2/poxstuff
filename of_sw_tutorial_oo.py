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

"""
This is a demonstration file that has various switch implementations.
The first example is a basic "all match" switch followed by a 
destination match, pair match then finally a more ideal pair match 
switch.

Mininet Command: sudo mn --topo single,3 --mac 
    --switch ovsk 
    --controller remote
Command Line: ./pox.py py --completion
    log.level --DEBUG 
    samples.of_sw_tutorial_oo

THIS VERSION SUPPORT resend() functionality in the betta branch POX.
Object-oriented version that allows user to switch switches via the 
command line interface.
"""

# These next two imports are common POX convention
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr

# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()

# Create the class to hold the switch tutorial implementations
class SwitchTutorial (object):

  # This table maps (switch,MAC-addr) pairs to the port on 'switch' at
  # which we last saw a packet *from* 'MAC-addr'.
  # (In this case, we use a Connection object for the switch.)
  table = {}

  # Holds the object with the default switch
  handlerName = 'SW_IDEALPAIRSWITCH'

  # Holds the current active PacketIn listener object
  listeners = None

  # Constructor and sets default handler to Ideal Pair Switch
  def __init__(self, handlerName = 'SW_IDEALPAIRSWITCH'):
    log.debug("Initializing switch %s." % handlerName)

  # Method for just sending a packet to any port (broadcast by default)
  def send_packet(self, event, dst_port = of.OFPP_ALL):
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
  def resend_packet(self, event, dst_port = of.OFPP_ALL):
    msg = of.ofp_packet_out(data = event.ofp)
    msg.actions.append(of.ofp_action_output(port = dst_port))
    event.connection.send(msg)

  # DUMB HUB Implementation
  # This is an implementation of a broadcast hub but all packets go 
  # to the controller since no flows are installed.
  def _handle_dumbhub_packetin(self, event):
    # Just send an instruction to the switch to send packet to all ports
    packet = event.parsed
    self.resend_packet(event, of.OFPP_ALL)

    log.debug("Broadcasting %s.%i -> %s.%i" %
      (packet.src, event.ofp.in_port, packet.dst, of.OFPP_ALL))

  # PAIR-WISE MATCHING HUB Implementation
  # This is an implementation of a broadcast hub with flows installed.
  def _handle_pairhub_packetin(self, event):
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
  def _handle_lazyhub_packetin(self, event):
    packet = event.parsed

    # Create flow that simply broadcasts any packet received
    msg = of.ofp_flow_mod()
    msg.data = event.ofp
    msg.idle_timeout = 10
    msg.hard_timeout = 30
    msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
    event.connection.send(msg)

    log.debug("Installing %s.%i -> %s.%i" %
      ("ff:ff:ff:ff:ff:ff", event.ofp.in_port, "ff:ff:ff:ff:ff:ff", 
      of.OFPP_ALL))

  # BAD SWITCH Implementation
  # This is an obvious but problematic implementation of switch that
  # routes based on destination MAC addresses. 
  def _handle_badswitch_packetin(self, event):
    packet = event.parsed

    # Learn the source and fill up routing table
    self.table[(event.connection,packet.src)] = event.port

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
    dst_port = self.table.get((event.connection,packet.dst))

    if dst_port is None:
      # We don't know where the destination is yet. So, we'll just
      # send the packet out all ports (except the one it came in on!)
      # and hope the destination is out there somewhere. :)
      # To send out all ports, we can use either of the special ports
      # OFPP_FLOOD or OFPP_ALL. We'd like to just use OFPP_FLOOD,
      # but it's not clear if all switches support this. :(
      self.resend_packet(event, of.OFPP_ALL)

      log.debug("Broadcasting %s.%i -> %s.%i" %
        (packet.src, event.ofp.in_port, packet.dst, of.OFPP_ALL))
    else:   
      # This is the packet that just came in -- we want send the packet
      # if we know the destination.
      self.resend_packet(event, dst_port)

      log.debug("Sending %s.%i -> %s.%i" %
        (packet.src, event.ofp.in_port, packet.dst, dst_port))

  # PAIR-WISE MATCH SWITCH Implementation
  # This is an implementation of an pair match switch. This only matches
  # source and destination MAC addresses. Whenever a new source 
  # destination MAC address is detected it then add a new flow 
  # identifying the source destination pair. The routing table is updated
  # using the detected destination MAC address to the destination port.
  def _handle_pairswitch_packetin (self, event):
    packet = event.parsed

    # Learn the source and fill up routing table
    self.table[(event.connection,packet.src)] = event.port
    dst_port = self.table.get((event.connection,packet.dst))

    if dst_port is None:
      # We don't know where the destination is yet. So, we'll just
      # send the packet out all ports (except the one it came in on!)
      # and hope the destination is out there somewhere. :)
      # To send out all ports, we can use either of the special ports
      # OFPP_FLOOD or OFPP_ALL. We'd like to just use OFPP_FLOOD,
      # but it's not clear if all switches support this. :(
      self.resend_packet(event, of.OFPP_ALL)

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
  def _handle_idealpairswitch_packetin(self, event):
    packet = event.parsed

    # Learn the source and fill up routing table
    self.table[(event.connection,packet.src)] = event.port
    dst_port = self.table.get((event.connection,packet.dst))

    if dst_port is None:
      # We don't know where the destination is yet. So, we'll just
      # send the packet out all ports (except the one it came in on!)
      # and hope the destination is out there somewhere. :)
      # To send out all ports, we can use either of the special ports
      # OFPP_FLOOD or OFPP_ALL. We'd like to just use OFPP_FLOOD,
      # but it's not clear if all switches support this. :(
      self.resend_packet(event, of.OFPP_ALL)

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

  # Define the proper handler
  def _set_handler_name (self, handlerName = 'SW_IDEALPAIRSWITCH'):
    self.handlerName = handlerName

  # Function to grab the appropriate handler
  def _get_handler (self, event):
    return self.swMap[self.handlerName](self, event)

  """ Here are functions that are meant to be called directly """
  # Here is a function to list all possible switches
  def list_available_listeners(self):
    for key in self.swMap.iterkeys():
      log.info("%s" % key)

  # Here is a function to displaying possible methods
  def help(self):
    log.info("Methods available: %s %s %s %s %s" % 
      ('list_available_listeners()', 
      'attach_packetin_listener(handlerName = \'SW_IDEALPAIRSWITCH\'',
      'detach_packetin_listener()',
      'clear_all_flows()',
      'clear_flows(connection)'))

  # Here is a function to attach the listener give the default handerName
  def attach_packetin_listener (self, handlerName = 'SW_IDEALPAIRSWITCH'):
    self._set_handler_name(handlerName)
    self.listeners = core.openflow.addListenerByName("PacketIn",
      self._get_handler)
    log.debug("Attach switch %s." % handlerName)

  # Here is a function to remove the listener
  def detach_packetin_listener (self):
    core.openflow.removeListener(self.listeners)
    log.debug("Detaching switch %s." % self.handlerName)

  # Function to clear all flows from a specified switch given 
  # a connection object
  def clear_flows (self, connection):
    msg = of.ofp_flow_mod(match=of.ofp_match(),command=of.OFPFC_DELETE)
    connection.send(msg)
    log.debug("Clearing all flows from %s." % 
      dpidToStr(connection.dpid))

  # Function to clear all flows from all switches
  def clear_all_flows (self):
    msg = of.ofp_flow_mod(match=of.ofp_match(),command=of.OFPFC_DELETE)
    for connection in core.openflow._connections.values():
      connection.send(msg)
      log.debug("Clearing all flows from %s." % 
        dpidToStr(connection.dpid))

  # Define various switch handlers
  swMap = {
    'SW_DUMBHUB' : _handle_dumbhub_packetin,
    'SW_PAIRHUB' : _handle_pairhub_packetin,
    'SW_LAZYHUB' : _handle_lazyhub_packetin,
    'SW_BADSWITCH' : _handle_badswitch_packetin,
    'SW_PAIRSWITCH' : _handle_pairswitch_packetin,
    'SW_IDEALPAIRSWITCH' : _handle_idealpairswitch_packetin,
  }


# function that is invoked upon load to ensure that listeners are
# registered appropriately. Uncomment the hub/switch you would like 
# to test. Only one at a time please.
def launch ():
  # create new tutorial class object using the IDEAL PAIR SWITCH as default
  MySwitch = SwitchTutorial('SW_IDEALPAIRSWITCH')

  # add this class into core.Interactive.variables to ensure we can access
  # it in the CLI.
  core.Interactive.variables['MySwitch'] = MySwitch

  # attach the corresponding default listener
  MySwitch.attach_packetin_listener()
