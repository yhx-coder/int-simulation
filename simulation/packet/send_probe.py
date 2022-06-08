# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/20 14:36
import sys


sys.path.append("/home/sdn/Downloads/int/")
import struct

from concurrent.futures import ThreadPoolExecutor

from scapy.arch import get_if_hwaddr
from scapy.interfaces import get_if_list
from scapy.sendrecv import sendp

import probe
import socket

from simulation.config.constants import Constants


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


def rcvControlMessage(controlPort):
    """
    控制端与 controlPort 端口建立 tcp。发送的控制消息格式为： 负载长度[[],[],[],...]
    """

    # 控制包的包头长度
    headSize = 4
    # 数据缓存
    dataBuffer = bytes()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    tcp_socket.bind(("", controlPort))
    tcp_socket.listen(1)
    conn, addr = tcp_socket.accept()
    while True:
        # 之前写的自定义结束符，性能不高，收到一个字符就得判断一下。
        # 粘包处理
        data = conn.recv(1024)
        if data:
            dataBuffer += data
            # 处理缓存中的内容
            while True:
                if len(dataBuffer) < headSize:
                    break
                # 读包头得到 payload 大小
                payloadSize = struct.unpack("I", dataBuffer[:headSize])[0]
                # 若缓存中的数据不到一个包
                if len(dataBuffer) < headSize + payloadSize:
                    break
                payload = dataBuffer[headSize:headSize + payloadSize]
                portLists = eval(payload)
                pool.submit(sendProbe, portLists)

                # 处理一个包后，清理缓冲区
                dataBuffer = dataBuffer[headSize + payloadSize:]


def sendProbe(portLists):
    for portList in portLists:
        packet = probe.genProbe(portList, srcMac=get_if_hwaddr(interface))
        # 内网网卡"h-eth0"
        sendp(packet, iface=interface)


if __name__ == "__main__":
    interface = get_if()
    pool = ThreadPoolExecutor(max_workers=2)
    rcvControlMessage(Constants.CONTROL_PORT)
