# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/19 20:38
import time
import uuid

from scapy.fields import BitField, IntField, ByteField
from scapy.layers.l2 import Ether
from scapy.packet import Packet, bind_layers

TYPE_PROBE = 0x812


class Probe(Packet):
    fields_desc = [ByteField("hop_cnt", 0)]


class SrcRoute(Packet):
    fields_desc = [ByteField(name="port", default=0)]


class IntData(Packet):
    fields_desc = [BitField(name="bos", default=0, size=1),
                   BitField(name="switch_id", default=0, size=10),
                   BitField(name="ingress_port", default=0, size=9),
                   BitField(name="egress_port", default=0, size=9),
                   BitField(name="hop_latency", default=0, size=48),
                   BitField(name="deq_qdepth", default=0, size=19),
                   IntField(name="deq_timedelta", default=0),
                   IntField(name="byte_cnt", default=0),
                   BitField(name="last_time", default=0, size=48),
                   BitField(name="cur_time", default=0, size=48)]


bind_layers(Ether, Probe, type=TYPE_PROBE)
bind_layers(Probe, SrcRoute, hop_cnt=0)
bind_layers(Probe, IntData)
bind_layers(IntData, SrcRoute, bos=1)
bind_layers(IntData, IntData, bos=0)
bind_layers(SrcRoute, SrcRoute)


def genProbe(portList, srcMac, dstMac="FF:FF:FF:FF:FF:FF"):
    """
    生成探针包
    :param srcMac: 源 mac
    :param dstMac: 目的 mac
    :param portList: 源路由的端口号列表。每一项是字符串类型
    :return:
    """
    probe = Ether(dst=dstMac, src=srcMac, type=TYPE_PROBE)
    probe = probe / Probe(hop_cnt=0)
    for port in portList:
        port = int(port)
        probe = probe / SrcRoute(port=port)
    packetId = str(uuid.uuid4())
    deliveryTime = str(time.time())
    payload = "_".join((packetId, deliveryTime))
    probe = probe / payload
    return probe
