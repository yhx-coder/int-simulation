# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/16 11:01

class Port:
    def __init__(self, portId, adjDevice):
        """
        :param portId: 端口 Id
        :param adjDevice: 端口对端设备
        """
        self.portId = portId
        self.adjDevice = adjDevice


class Table:
    def __init__(self, name, action, key, value):
        self.name = name
        self.action = action
        self.key = key
        self.value = value


class Device:
    def __init__(self, deviceType, deviceId):
        """
        :param deviceType: 设备类型 "h"或者"s"
        :param deviceId:  设备 Id
        """
        self.type = deviceType
        self.id = deviceId
        self.totalPorts = 0
        self.portList = []

    def __eq__(self, other):
        if self is None and other is not None:
            return False
        elif self is not None and other is None:
            return False
        elif self is None and other is None:
            return True
        else:
            return self.type == other.type and self.id == other.id

    def connect(self, device):
        """
        两个设备建立连接
        :param device: 对端设备
        """
        self.totalPorts += 1
        port1 = Port(self.totalPorts, device)
        self.portList.append(port1)

        device.totalPorts += 1
        port2 = Port(device.totalPorts, self)
        device.portList.append(port2)


class Switch(Device):

    def __init__(self, deviceType, deviceId, thriftPort=9090, runtime=None):
        Device.__init__(self, deviceType, deviceId)
        self.thriftPort = thriftPort
        self.runtime = runtime
        self.tables = []

    def addTable(self, name, action, key, value):
        self.tables.append(Table(name, action, key, value))


# 簇头相连的主机类
class Host(Device):
    def __init__(self, deviceType, deviceId, switchIp="", controlIp="", mac=""):
        Device.__init__(self, deviceType, deviceId)
        self.switchIp = switchIp
        self.controlIp = controlIp
        self.mac = mac
