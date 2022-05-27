# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/27 11:20
from simulation.config.constants import Constants


def genMac(hostId):
    hexId = hex(hostId)[2:].upper()
    if len(hexId) == 1:
        hexId = '0' + hexId
    mac = Constants.HOST_MAC_PREFIX + hexId
    return mac
