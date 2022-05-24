DROP DATABASE IF EXISTS `cfint`;
CREATE DATABASE `cfint`;
USE `cfint`;
CREATE TABLE `int_data`  (
  `switchId` smallint(5) UNSIGNED NOT NULL COMMENT '交换机id',
  `ingressPort` smallint(5) UNSIGNED NOT NULL COMMENT '入端口',
  `egressPort` smallint(5) UNSIGNED NOT NULL COMMENT '出端口',
  `hopLatency` bigint(20) UNSIGNED NOT NULL COMMENT 'egress_global_timestamp - ingress_global_timestamp',
  `deqQdepth` mediumint(8) UNSIGNED NOT NULL COMMENT '出队时的队列深度',
  `deqTimedelta` int(10) UNSIGNED NOT NULL COMMENT '队列中消耗的时间',
  `interval` bigint(20) UNSIGNED NOT NULL COMMENT '遥测数据时间间隔',
  `utilization` float UNSIGNED NOT NULL COMMENT '出端口的链路利用率。bytes/microsecond',
  `totalTime` double UNSIGNED NOT NULL COMMENT '探针数据包路径总时延',
  `curTime` bigint(20) UNSIGNED NOT NULL COMMENT '遥测时间',
  `packetId` varchar(36) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '探针id',
  PRIMARY KEY (`switchId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

