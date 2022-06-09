# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/16 10:50


class Constants:
    """
    设计分配地址为 2~254
    """
    CONTROL_HOST_IP_PREFIX = "192.168.229."
    SWITCH_HOST_IP_PREFIX = "10.0.0."
    HOST_MAC_PREFIX = "00:01:00:00:00:"
    TOPOLOGY_FILE = "/home/sdn/Downloads/int/resources/topoSrc/bics.txt"
    NODE_NUM = 33
    CONTROL_PORT = 8888
    SWITCH_PATH = "simple_switch"
    JSON_FILE = "resources/p4src/my_link_monitor.json"
    PATH_GENERATION = "/home/sdn/Downloads/int_java.jar"
    NETWORK_INTERFACE_TO_RELEASE = "ens34"

