# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/16 11:00
import os

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo

from simulation.config.constants import Constants
from simulation.topo.p4_mininet import P4Host, P4Switch


class MyTopo(Topo):
    def build(self, main):
        mininetSwitchList = []
        mininetHostList = []
        cur_path = os.path.abspath("..")
        jsonFile = os.path.join(os.path.dirname(cur_path), Constants.JSON_FILE)
        for i in range(main.totalNum):
            switch = main.switchList[i]
            name = switch.type + str(switch.id)
            mininetSwitchList.append(self.addSwitch(name=name,
                                                    sw_path=Constants.SWITCH_PATH,
                                                    json_path=jsonFile,
                                                    thrift_port=switch.thriftPort,
                                                    pcap_dump=False))
        for i in range(len(main.clusterHeadHostList)):
            host = main.clusterHeadHostList[i]
            name = host.type + str(host.id)
            mininetHostList.append(self.addHost(name=name, ip=host.switchIp + "/24"))

        # 1000 Mbps, 1ms delay, 2% loss, 1000 packet queue
        linkOpts = dict(bw=1000, delay='1ms', loss=10, max_queue_size=1000, use_htb=True)

        for i in range(main.totalNum):
            for j in range(main.switchList[i].totalPorts):
                adjDevice = main.switchList[i].portList[j].adjDevice
                port2 = main.getDevPort(adjDevice, main.switchList[i])
                if adjDevice.type == "s":
                    if adjDevice.id > i:
                        self.addLink(main.switchList[i], adjDevice,
                                     port1=main.switchList[i].portList[j], port2=port2, **linkOpts)
                else:
                    self.addLink(main.switchList[i], adjDevice,
                                 port1=main.switchList[i].portList[j], port2=port2, **linkOpts)


class TopoMaker:
    def __init__(self, main):
        self.topo = MyTopo(main)
        self.main = main
        self.net = None

    def genTopo(self):
        self.net = Mininet(topo=self.topo,
                           host=P4Host,
                           switch=P4Switch,
                           link=TCLink,
                           controller=None)
        controller_list = []
        c = self.net.addController('mycontroller', controller=RemoteController)
        controller_list.append(c)
        ovs = self.net.addSwitch('s999', cls=OVSSwitch)
        ovs.start(controller_list)

    def getCli(self):
        CLI(self.net)

    def cleanMininet(self):
        os.system("sudo mn -c")
