# -*- coding: utf-8 -*-
# @author: ming
# @date: 2022/5/21 19:45
import json
import os
import struct
from concurrent.futures import ThreadPoolExecutor

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

# import subprocess
#
# with subprocess.Popen("java -jar %s" % Constants.PATH_GENERATION, shell=True,
#                       stdout=subprocess.PIPE) as proc:
#     i = 0
#     while True:
#         info = proc.stdout.readline()
#         if info == '' or proc.poll() is not None:
#             break
#         info = info.decode("utf-8")
#         info = info.replace("\r\n", "")
#         if i == 0:
#             clusterHeadSwitchList = info
#         elif i == 1:
#             pathList = info
#         i += 1
#
# pathList = eval(pathList)
# print(type(pathList))
# print(pathList)
# clusterHeadSwitchList = eval(clusterHeadSwitchList)
# print(type(clusterHeadSwitchList))
# print(clusterHeadSwitchList)
# di = {}
# di["port"].append([2,3,4])
# print(di)
# pathList = [[13, 12, 36, 13], [13, 19, 20, 13], [13, 16, 47, 13], [13, 16, 32, 13], [13, 47, 46, 13], [13, 46, 1, 13],
#             [13, 1, 7, 13], [13, 7, 36, 13], [13, 20, 32, 13], [0, 5, 35, 0], [0, 2, 32, 13], [0, 2, 20, 13],
#             [0, 4, 32, 13], [0, 15, 20, 13], [0, 2, 4, 0], [0, 2, 15, 0], [0, 15, 35, 0], [0, 14, 0], [0, 14, 18, 0],
#             [0, 18, 8, 0], [0, 4, 8, 0], [6, 37, 35, 0], [6, 5, 14, 0], [6, 26, 33, 6], [6, 38, 11, 6], [6, 11, 15, 0],
#             [6, 11, 35, 0], [6, 44, 5, 6], [6, 44, 33, 6], [6, 37, 11, 6], [6, 37, 5, 6], [24, 49, 43, 9],
#             [24, 40, 28, 24], [24, 9, 24], [24, 43, 42, 24], [24, 42, 48, 3], [24, 28, 14, 0], [24, 28, 44, 6],
#             [24, 28, 5, 6], [24, 28, 33, 6], [24, 28, 26, 23], [24, 49, 42, 24], [3, 48, 46, 13], [3, 48, 1, 13],
#             [3, 4, 30, 3], [3, 39, 8, 0], [3, 39, 4, 0], [3, 29, 47, 13], [3, 29, 46, 13], [3, 30, 32, 13],
#             [3, 30, 16, 13], [3, 30, 47, 13], [3, 45, 22, 3], [3, 45, 39, 3], [3, 48, 29, 3], [3, 48, 22, 3],
#             [3, 29, 30, 3], [9, 41, 22, 3], [9, 25, 22, 3], [9, 25, 45, 3], [9, 25, 39, 3], [9, 43, 22, 3],
#             [9, 43, 48, 3], [9, 41, 25, 9], [9, 41, 43, 9], [9, 27, 25, 9], [10, 17, 25, 9], [10, 17, 27, 9],
#             [10, 17, 39, 3], [10, 21, 8, 0], [10, 21, 18, 0], [10, 21, 39, 3], [10, 40, 14, 0], [10, 40, 18, 0],
#             [10, 24, 10], [10, 27, 9], [10, 9, 10], [10, 21, 40, 10], [10, 21, 17, 10], [23, 34, 36, 13],
#             [23, 38, 20, 13], [23, 38, 19, 13], [23, 38, 15, 0], [23, 6, 23], [23, 12, 19, 13], [23, 31, 7, 13],
#             [23, 31, 36, 13], [23, 31, 34, 23], [23, 38, 12, 23], [23, 12, 34, 23]]
# startNodeDict = {}
# for path in pathList:
#     if path[0] in startNodeDict:
#         startNodeDict[path[0]].append(path)
#     else:
#         startNodeDict[path[0]] = [path]
# m = str(startNodeDict[13])
# t = "".join((m,"#"))
# print(t)

#
# a = "[[1]]"
# b = struct.pack("i", a.__len__())
# c = struct.unpack("i",b)
# print(type(c))
# print(c)

pool = ThreadPoolExecutor(max_workers=2)
def a():
    print("hhhhh")
pool.submit(a)