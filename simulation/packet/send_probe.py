# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/20 14:36
import threading


from scapy.sendrecv import sendp

import probe
import socket


def rcvControlMessage(controlPort):
    """
    控制端与 controlPort 端口建立 tcp。发送的控制消息格式为 “源路由端口1,源路由端口2#”
    逗号分隔，#结尾，
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("", controlPort))
    tcp_socket.listen(2)
    while True:
        conn, addr = tcp_socket.accept()
        data = ""
        while True:
            data = data + conn.recv(1024).decode("utf-8")
            if data.endswith("#"):
                portList = data[0:-1].split(",")
                thread = threading.Thread(target=sendProbe, args=portList)
                thread.setDaemon(False)
                thread.start()
                data = ""


def sendProbe(portList):

    packet = probe.genProbe(portList)
    # 内网网卡名要设置成"eth0"
    sendp(packet, iface="eth0")


if __name__ == "__main__":
    rcvControlMessage(8888)
