# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/21 19:36
import os

from simulation.config.constants import Constants


def genAdjMatrix():
    cur_path = os.path.abspath("..")
    topo_file = os.path.join(os.path.dirname(cur_path), Constants.TOPOLOGY_FILE)

    adjMatrix = [[0 for _ in range(Constants.NODE_NUM)] for _ in range(Constants.NODE_NUM)]

    with open(topo_file, "r") as f:
        line = f.readline()
        while line:
            line = f.readline()
            line = line.rstrip('\n')
            nodeList = line.split(" ")
            if len(nodeList) > 1:
                node1 = int(nodeList[0])
                node2 = int(nodeList[1])
                adjMatrix[node1][node2] = 1
                adjMatrix[node2][node1] = 1
    return adjMatrix
