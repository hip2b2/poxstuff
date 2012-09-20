#!/usr/bin/python
# wyu@ateneo.edu
#
# This is a demonstration file created to show how to obtain flow 
# and port statistics from OpenFlow 1.0-enabled switches.
#

# standard includes
from pox.core import core
import pox.openflow.libopenflow_01 as of

# include as part of the betta branch
from pox.openflow.of_json import *

log = core.getLogger()

# handler for timer function that sends the requests to all the
# switches connected to the controller.
def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
    connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
  log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

# handler to display flow statistics received in JSON format
def handle_FlowStatsReceived(event):
  stats = flow_stats_to_list(event.stats)
  log.debug("FlowStatsReceived %s", stats)

# handler to display port statistics received in JSON format
def handle_PortStatsReceived(event):
  stats = flow_stats_to_list(event.stats)
  log.debug("PortStatsReceived %s", stats)
    
def launch ():
  from pox.lib.recoco import Timer

  # attach handsers to listners
  core.openflow.addListenerByName("FlowStatsReceived", handle_FlowStatsReceived) 
  core.openflow.addListenerByName("PortStatsReceived", handle_PortStatsReceived) 

  # timer set to execute every five seconds
  Timer(5, _timer_func, recurring=True)
