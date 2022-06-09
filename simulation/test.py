import sys
sys.path.append("/home/sdn/Downloads/int/")

from scapy.layers.l2 import Ether

from simulation.packet.probe import Probe, SrcRoute


from scapy.arch import get_if_hwaddr
from scapy.interfaces import get_if_list
from scapy.sendrecv import sendp

from simulation.packet import probe


def get_if():
    ifs = get_if_list()
    iface = None  # "h1-eth0"
    for i in ifs:
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

interface = get_if()
packet = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                Probe(hop_cnt=0) / SrcRoute(port=1)/SrcRoute(port=2)/SrcRoute(port=3)

# 内网网卡"h-eth0"
for _ in range(1):
    sendp(packet, iface="eth0")