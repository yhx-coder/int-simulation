import sys

from scapy.layers.l2 import Ether

sys.path.append("/home/sdn/Downloads/int/")

from scapy.arch import get_if_hwaddr
from scapy.interfaces import get_if_list
from scapy.sendrecv import sendp

from simulation.packet.probe import *



portList = ["6","2","7"]
interface = "eth0"
packet = genProbe(portList, srcMac=get_if_hwaddr(interface))
# 内网网卡"h-eth0"
packet2 = Ether(dst="FF:FF:FF:FF:FF:FF",type=TYPE_PROBE_TRANSIT)/SrcRoute(port=6)/SrcRoute(port=2)/SrcRoute(port=7)/Probe(hop_cnt=0)
for _ in range(1):
    sendp(packet, iface=interface)