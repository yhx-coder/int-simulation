# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/16 17:00

from simulation.config.constants import Constants


def genClusterHeadHostIp(hostId, isControlIp):
    """
    用于生成和簇头相连的主机 IP，isControlIp 为 1 时生成和控制器相连的 IP，为 0 时是用于转发的 Ip。
    :param hostId: int
    :param isControlIp: int, 0 或 1
    :return: string ip地址字符串
    """
    if isControlIp:
        return Constants.CONTROL_HOST_IP_PREFIX + str(hostId + 2)
    else:
        return Constants.SWITCH_HOST_IP_PREFIX + str(hostId + 2)

