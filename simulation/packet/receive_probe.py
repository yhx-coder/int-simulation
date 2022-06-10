# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/20 16:24
import sys

sys.path.append("/home/sdn/Downloads/int/")

import pymysql

from probe import *

conn = pymysql.connect(user="root", password="root", database="cfint", unix_socket="/var/run/mysqld/mysqld.sock")
cursor = conn.cursor()


def pktHandler(pkt):
    """
    和时间有关的都用微秒
    :param pkt:
    """
    if pkt.type == TYPE_PROBE_SINK:
        packetMeta = bytes(pkt.getlayer("Raw"))
        packetMeta = str(packetMeta, "utf-8")
        packetId, deliveryTime = packetMeta.split("_")
        now = time.time()
        pkt = pkt.payload
        hop_cnt = int(pkt.hop_cnt)
        pkt = pkt.payload
        for _ in range(hop_cnt):
            if pkt.name == "IntData":
                switch_id = pkt.switch_id
                ingress_port = pkt.ingress_port
                egress_port = pkt.egress_port
                hop_latency = pkt.hop_latency
                deq_qdepth = pkt.deq_qdepth
                deq_timedelta = pkt.deq_timedelta
                interval = pkt.cur_time - pkt.last_time
                # 出端口的链路利用率。bytes/microsecond
                utilization = 0 if interval == 0 else pkt.byte_cnt / interval

                totalTime = now - float(deliveryTime)
                totalTime = int(round(totalTime * 1000000))

                cur_time = pkt.cur_time

                sql = "insert into int_data(`switchId`,`ingressPort`,`egressPort`," \
                      "`hopLatency`,`deqQdepth`,`deqTimedelta`,`interval`,`utilization`,`totalTime`,`curTime`,`packetId`) " \
                      "values(%(switch_id)s,%(ingress_port)s,%(egress_port)s,%(hop_latency)s," \
                      "%(deq_qdepth)s,%(deq_timedelta)s,%(interval)s,%(utilization)s,%(totalTime)s,%(curTime)s,%(packetId)s)"

                values = {"switch_id": switch_id, "ingress_port": ingress_port, "egress_port": egress_port,
                          "hop_latency": hop_latency, "deq_qdepth": deq_qdepth, "deq_timedelta": deq_timedelta,
                          "interval": interval, "utilization": utilization, "totalTime": totalTime,
                          "curTime": cur_time,
                          "packetId": packetId}
                cursor.execute(sql, values)
                conn.commit()
            pkt = pkt.payload


def handle(pkt):
    if pkt.type == TYPE_PROBE_TRANSIT or pkt.type == TYPE_PROBE_SINK:
        pkt.show()


iface = "eth0"
sniff(iface=iface, prn=lambda x: pktHandler(x))
