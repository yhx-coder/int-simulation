# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/21 19:45
import os
from simulation.config.constants import Constants
# cur_path = os.path.dirname(os.path.realpath(__file__))
#
# cur_path =  os.path.dirname(cur_path)
# cur_path = os.path.abspath("..")
# print cur_path
# config_path = os.path.join(os.path.dirname(cur_path), Constants.topology_file)
# print(config_path)
#
# b = {"a":"a","c":""}
# a = [1,2,3,4,5,6]
# print(a[3])

import subprocess


with subprocess.Popen("java Test.java", shell=True, stdout=subprocess.PIPE) as proc:
    i = 0
    while True:
        info = proc.stdout.readline()
        if info == '' or proc.poll() is not None:
            break
        info = info.decode("utf-8")
        info = info.replace("\r\n","")
        if i == 0:
            pathList = info
        elif i == 1:
            clusterHeadSwitchList = info
        i += 1
print(i)
path = eval(pathList)
print(type(path))
print(path)
print("-------------------------")
print(type(clusterHeadSwitchList))
print(clusterHeadSwitchList)
