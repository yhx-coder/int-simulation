# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/23 11:00
import copy
import json
import socket
import subprocess

from simulation.config.constants import Constants
from simulation.pojo.device import Switch, Host
from simulation.topo import thrift_API
from simulation.topo.genTopo import TopoMaker
from simulation.topo.thrift_API import ThriftAPI
from simulation.util.genAdjMatrix import genAdjMatrix
from simulation.util.genIp import genClusterHeadHostIp


class TelemetryController:
    def __init__(self, topo, clusterHeadSwitchList):
        self.topo = copy.deepcopy(topo)
        self.totalNum = Constants.NODE_NUM
        self.switchList = []
        self.clusterHeadSwitchList = copy.deepcopy(clusterHeadSwitchList)
        self.clusterHeadHostList = []
        self.clusterHeadHostDic = {}
        self.controlLink = {}
        self.rates = 100
        self.depth = 10

    def genSwitch(self):
        for i in range(self.totalNum):
            thriftPort = 9090 + i

            switch = Switch(deviceType="s", deviceId=i, thriftPort=thriftPort)
            self.switchList.append(switch)

    def genHost(self):
        for switch in self.clusterHeadSwitchList:
            host = Host("h", switch.id, genClusterHeadHostIp(switch.id, 0), genClusterHeadHostIp(switch.id, 1))
            self.clusterHeadHostList.append(host)
            self.clusterHeadHostDic[switch.id] = host

    def genSwitchLink(self):
        for i in range(self.totalNum):
            for j in range(i + 1, self.totalNum):
                if self.topo[i][j] != 0:
                    self.switchList[i].connect(self.switchList[j])

    def genClusterHeadLink(self):
        for i in range(len(self.clusterHeadHostList)):
            switchId = self.clusterHeadHostList[i].id
            self.clusterHeadHostList[i].connect(self.switchList[switchId])

    # 获取 device1 的连接端口
    def getDevPort(self, device1, device2):
        for port in device1.portList:
            if port.adjDevice == device2:
                return port.portId
        return -1

    def genSwitchIdTable(self):
        for switchId, switch in enumerate(self.switchList):
            entry = {"table_name": "MyEgress.switchId", "action_name": "MyEgress.setSwitchId",
                     "match_keys": [], "action_params": [str(switchId)]}
            switch.tables.append(entry)

    def downTables(self):
        for switch in self.switchList:
            for table in switch.tables:
                switch.runtime.table_add(table_name=table["table_name"], action_name=table["action_name"],
                                         match_keys=table["match_keys"], action_params=table["action_params"])

    def makeTopo(self):
        topoMaker = TopoMaker(self)
        topoMaker.cleanMininet()
        topoMaker.genTopo()
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
            runtime = ThriftAPI(thrift_port=switch.thriftPort, thrift_ip="localhost",
                                pre_type=thrift_API.PreType.SimplePreLAG)
            # Sets rate of all egress queues  (packets per seconds)
            runtime.client.set_all_egress_queue_rates(self.rates)
            # Sets depth of all egress queues. (number of packets)
            runtime.client.set_all_egress_queue_depths(self.depth)
            switch.runtime = runtime

    def genControlLink(self):
        for host in self.clusterHeadHostList:
            print("try connecting to {} ...".format(host.controlIp))
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((host.controlIp, Constants.CONTROL_PORT))
            self.controlLink[host.id] = tcp_socket

    def sendControlInfo(self, pathList):
        startNodeDict = {}
        for path in pathList:
            startNodeDict[path[0]] = {"portsList": []}
        for path in pathList:
            length = len(path)
            portList = []
            for i in range(length - 1):
                port = self.getDevPort(self.switchList[path[i]], self.switchList[path[i + 1]])
                if port != -1:
                    portList = portList.append(port)
                else:
                    raise Exception("交换机{}和{}间无连接".format(path[i], path[i + 1]))
            last_switch = self.switchList[path[length - 1]]
            port = self.getDevPort(last_switch, self.clusterHeadHostDic[last_switch.id])
            portList.append(port)
            startNodeDict[path[0]]["portsList"].append(portList)
        for key, value in startNodeDict.items():
            tcp_socket = self.controlLink[key]
            if tcp_socket:
                info = json.dumps(value)
                info.encode("utf-8")
                tcp_socket.send(info)

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
    topo = genAdjMatrix()
    # java程序分两行输出，第一行打印路径列表，第二行打印簇头交换机列表。
    with subprocess.Popen("java %s" % Constants.PATH_GENERATION, shell=True, stdout=subprocess.PIPE) as proc:
        i = 0
        while True:
            info = proc.stdout.readline()
            if info == '' or proc.poll() is not None:
                break
            info = info.decode("utf-8")
            info = info.replace("\r\n", "")
            if i == 0:
                pathList = info
            elif i == 1:
                clusterHeadSwitchList = info
            i += 1

    pathList = eval(pathList)
    clusterHeadSwitchList = eval(clusterHeadSwitchList)
    myController = TelemetryController(topo, clusterHeadSwitchList)
    myController.start()
    myController.sendControlInfo(pathList)