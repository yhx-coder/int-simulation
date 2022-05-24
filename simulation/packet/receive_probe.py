# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/20 16:24
import time

import pymysql
from scapy.sendrecv import sniff

import probe

conn = pymysql.connect(user="root", password="root", host="localhost", database="cfint")
cursor = conn.cursor()


def pktHandler(pkt):
    """
    和时间有关的都用微秒
    :param pkt:
    """
    if probe.IntData in pkt:
        packetMeta = bytes(pkt.getlayer("Raw"))
        packetMeta = str(packetMeta, "utf-8")
        packetId, deliveryTime = packetMeta.split("_")
        now = time.time()
        pkt = pkt.payload
        while pkt:
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

                sql = "insert into int_data(switchId,ingressPort,egressPort," \
                      "hopLatency,deqQdepth,deqTimedelta,interval,utilization,curTime,packetId) " \
                      "values(%(switch_id),%(ingress_port),%(egress_port)," \
                      "%(hop_latency),%(deq_qdepth),%(deq_timedelta),%(interval),%(utilization)," \
                      "%(totalTime),%(curTime),%(packetId))"

                values = {"switch_id": switch_id, "ingress_port": ingress_port, "egress_port": egress_port,
                          "hop_latency": hop_latency, "deq_qdepth": deq_qdepth, "deq_timedelta": deq_timedelta,
                          "interval": interval, "utilization": utilization, "totalTime": totalTime,
                          "curTime": pkt.cur_time,
                          "packetId": packetId}
                cursor.execute(sql, values)
                cursor.commit()
            pkt = pkt.payload


iface = "eth0"
sniff(iface=iface, prn=lambda x: pktHandler(x))
