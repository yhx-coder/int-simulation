# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/23 11:00
import os
import sys
import time

sys.path.append("/home/sdn/Downloads/int/")

import copy
import socket
import struct
import subprocess
from simulation.config.constants import Constants
from simulation.pojo.device import Switch, Host
from simulation.topo.genTopo import TopoMaker, cleanMininet
from simulation.topo.sswitch_thrift_API import SimpleSwitchThriftAPI
from simulation.util.genIp import genClusterHeadHostIp
from simulation.util.genMac import genMac


class TelemetryController:
    def __init__(self, topo1, clusterHeadSwitchList1):
        self.topo = copy.deepcopy(topo1)
        self.totalNum = Constants.NODE_NUM
        self.switchList = []
        self.clusterHeadSwitchList = copy.deepcopy(clusterHeadSwitchList1)
        self.clusterHeadHostList = []
        self.clusterHeadHostDic = {}
        self.controlLink = {}
        cur_path = os.path.abspath("..")
        self.jsonFile = os.path.join(os.path.dirname(cur_path), Constants.JSON_FILE)
        self.rates = 100
        self.depth = 10

    def genSwitch(self):
        for num in range(self.totalNum):
            thriftPort = 9090 + num

            switch = Switch(deviceType="s", deviceId=num, thriftPort=thriftPort)
            self.switchList.append(switch)

    def genHost(self):
        for id in self.clusterHeadSwitchList:
            host = Host("h", id, genClusterHeadHostIp(id, 0), genClusterHeadHostIp(id, 1),
                        genMac(id))
            self.clusterHeadHostList.append(host)
            self.clusterHeadHostDic[id] = host

    def genSwitchLink(self):
        for row in range(self.totalNum):
            for column in range(row + 1, self.totalNum):
                if self.topo[row][column] != 0:
                    self.switchList[row].connect(self.switchList[column])

    def genClusterHeadLink(self):
        for num in range(len(self.clusterHeadHostList)):
            switchId = self.clusterHeadHostList[num].id
            self.clusterHeadHostList[num].connect(self.switchList[switchId])

    # 获取 device1 的连接端口ID
    def getDevPortId(self, device1, device2):
        for port in device1.portList:
            if port.adjDevice == device2:
                return port.portId
        return -1

    def genArpTable(self):
        for host in self.clusterHeadHostList:
            for switch in self.switchList:
                entry = {"table_name": "MyIngress.doarp", "action_name": "MyIngress.arpreply",
                         "match_keys": ["00:00:00:00:00:00", host.switchIp], "action_params": [host.mac]}
                switch.tables.append(entry)

    def genSwitchIdTable(self):
        for switchId, switch in enumerate(self.switchList):
            entry = {"table_name": "MyEgress.swid", "action_name": "MyEgress.set_swid",
                     "match_keys": [], "action_params": [str(switchId)]}
            switch.tables.append(entry)

    def downTables(self):
        for switch in self.switchList:
            for table in switch.tables:
                switch.runtime.table_add(table_name=table["table_name"], action_name=table["action_name"],
                                         match_keys=table["match_keys"], action_params=table["action_params"])

    def makeTopo(self):
        self.topoMaker = TopoMaker(self)
        cleanMininet()
        self.topoMaker.genTopo()
        for switch in self.switchList:
            """
                The CLI include commands to program the multicast engine. 
                Because we provide 2 different engines (SimplePre and SimplePreLAG), 
                you have to specify which one your target is using when starting the CLI, using the --pre option.
                Accepted values are: None, SimplePre (default value) and SimplePreLAG. 
                The l2_switch target uses the SimplePre engine, 
                while the simple_switch target uses the SimplePreLAG engine.
                摘自：https://github.com/p4lang/behavioral-model
            """
            runtime = SimpleSwitchThriftAPI(thrift_port=switch.thriftPort)
            # Sets rate of all egress queues  (packets per seconds)
            runtime.set_queue_rate(self.rates)
            # Sets depth of all egress queues. (number of packets)
            runtime.set_queue_depth(self.depth)
            switch.runtime = runtime

    def genControlLink(self):
        for host in self.clusterHeadHostList:
            print("try connecting to {} ...".format(host.controlIp))
            try:
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.connect((host.controlIp, Constants.CONTROL_PORT))
                print(host.controlIp, 'connected')
                self.controlLink[host.id] = tcp_socket
            except Exception:
                print('socket gen failed', host.controlIp)
                self.controlLink[host.id] = None


    def sendControlInfo(self, rev_pathList):
        # 先整理下要发送的数据
        # {簇头交换机id:[[],[]]由该簇头发的包路径列表}
        startNodeDict = {}
        for path in rev_pathList:
            length = len(path)
            portList = []
            for num in range(length - 1):
                port = self.getDevPortId(self.switchList[path[num]], self.switchList[path[num + 1]])
                if port != -1:
                    portList.append(port)
                else:
                    raise Exception("交换机{}和{}间无连接".format(path[num], path[num + 1]))
            last_switch = self.switchList[path[length - 1]]
            port = self.getDevPortId(last_switch, self.clusterHeadHostDic[last_switch.id])
            portList.append(port)
            if path[0] in startNodeDict:
                startNodeDict[path[0]].append(portList)
            else:
                startNodeDict[path[0]] = [portList]

        for key, value in startNodeDict.items():
            tcp_socket = self.controlLink[key]
            if tcp_socket:
                payload = str(value).encode("utf-8")
                header = struct.pack("I", payload.__len__())
                controlMessage = header + payload
                tcp_socket.send(controlMessage)

            time.sleep(10)

    def start(self):
        self.genSwitch()
        self.genHost()
        self.genSwitchLink()
        self.genClusterHeadLink()
        self.genSwitchIdTable()
        self.makeTopo()
        self.downTables()
        self.genControlLink()


if __name__ == "__main__":
    # java程序分两行输出，第一行打印路径列表，第二行打印簇头交换机列表。

    with subprocess.Popen("java -jar {0} {1} {2}".format(Constants.PATH_GENERATION,
                                                         Constants.TOPOLOGY_FILE, Constants.NODE_NUM),
                          shell=True, stdout=subprocess.PIPE) as proc:
        i = 0
        while True:
            info = proc.stdout.readline()
            if info == '' or proc.poll() is not None:
                break
            info = info.decode("utf-8")
            info = info.replace("\r\n", "")
            if i == 0:
                clusterHeadSwitchList = info
            elif i == 1:
                pathList = info
            elif i == 2:
                topo = info
            i += 1
        pathList = eval(pathList)
        clusterHeadSwitchList = eval(clusterHeadSwitchList)
        topo = eval(topo)
    myController = TelemetryController(topo, clusterHeadSwitchList)
    myController.start()
    myController.sendControlInfo(pathList)
