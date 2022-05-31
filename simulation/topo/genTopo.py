# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/16 11:00
import os

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.topo import Topo

from simulation.config.constants import Constants
from simulation.topo.p4_mininet import P4Host, P4Switch


class MyTopo(Topo):
    def build(self, main):
        mininetSwitchList = []
        mininetHostDic = {}
        for i in range(main.totalNum):
            switch = main.switchList[i]
            name = switch.type + str(switch.id)
            mininetSwitchList.append(self.addSwitch(name=name,
                                                    sw_path=Constants.SWITCH_PATH,
                                                    json_path=main.jsonFile,
                                                    thrift_port=switch.thriftPort,
                                                    pcap_dump=False))
        for i in range(len(main.clusterHeadHostList)):
            host = main.clusterHeadHostList[i]
            name = host.type + str(host.id)
            mininetHost = self.addHost(name=name, ip=host.switchIp + "/24")
            mininetHostDic[host.id] = mininetHost

        # 1000 Mbps, 1ms delay, 2% loss, 1000 packet queue
        linkOpts = dict(bw=1000, delay='1ms', loss=10, max_queue_size=1000, use_htb=True)

        for i in range(main.totalNum):
            for j in range(main.switchList[i].totalPorts):
                adjDevice = main.switchList[i].portList[j].adjDevice
                port2 = main.getDevPortId(adjDevice, main.switchList[i])
                if adjDevice.type == "s":
                    if adjDevice.id > i:
                        self.addLink(mininetSwitchList[i], mininetSwitchList[adjDevice.id],
                                     port1=main.switchList[i].portList[j].portId, port2=port2, **linkOpts)
                else:
                    self.addLink(mininetSwitchList[i], mininetHostDic[adjDevice.id],
                                 port1=main.switchList[i].portList[j].portId, port2=port2, **linkOpts)


def cleanMininet():
    os.system("sudo mn -c")


class TopoMaker:
    def __init__(self, main):
        self.topo = MyTopo(main)
        self.main = main
        self.net = None

    def genTopo(self):
        self.net = Mininet(topo=self.topo,
                           host=P4Host,
                           switch=P4Switch,
                           link=TCLink)

        s999 = self.net.addSwitch("s999", cls=OVSSwitch)

        for host in self.main.clusterHeadHostList:
            hostName = host.type + str(host.id)
            netHost = self.net.getNodeByName(hostName)
            self.net.addLink(netHost, s999)
            action = "ip addr add %s/24 dev %s" % (host.controlIp, hostName + "-eth1")
            netHost.cmd(action)
            netHost.cmd("python3 ../../packet/send_probe.py &")
            netHost.cmd("python3 ../../packet/receive_probe.py &")
        self.net.start()
        os.popen("ovs-vsctl add-port s999 %s" % Constants.NETWORK_INTERFACE_TO_RELEASE)

    def getCli(self):
        CLI(self.net)

    def stopNet(self):
        self.net.stop()
