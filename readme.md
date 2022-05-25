# 分簇算法仿真实验工具

构成组件：mininet 中虚拟主机——探针收发器，mininet中交换机——bmv2，控制器（main.py）

整体思路如下：控制器和探针收发器建立TCP连接，控制器生成p4转发表的大部分参数（ipv4等常规转发为了简单就开启了一个ryu），以及生成探测路径的源路由。源路由信息发送至探针收发器，收发器构造包发送。同时收发器监听网卡，接收探针包并解析。将得到的结果传入数据库。

下一步计划：将解析的结果传至过滤器，由过滤器插入数据库，减小数据写入压力。

实现参考了：

https://github.com/p4lang/tutorials/

https://github.com/graytower/INT_PATH

在控制器写流表时使用了：https://github.com/nsg-ethz/p4-utils 中的 `thrift_API.py`。其实不用也可以，像p4lang/tutorials/utils/mininet/appcontroller.py 中开子进程，用原生的 runtim_cli 直接写入也可。但就是想偷懒，毕竟人家封装的简单嘛。

目前未完成：mininet 主机与实际主机通信。

碎碎念：

* `bm_runtime`（bmv2/tools/） 	`sswitch_runtime`（bmv2/targets/simple_switch/    由 thrift 源文件生成的）	`bmpy_utils.py`（bmv2/tools/） 都是bmv2仓库中提供的，我直接复制了下。用于下发流表的。
* 发流表没用 grpc ，也就是 target 没用 simple_switch_grpc，是因为我想设置端口的转发速率，而该功能只在thrift 提供的 API 中找到了，想着直接用一个 thrift 客户端搞定，就选择了simple_switch。还有就是不是所有的设备都支持 grpc 服务端，但都支持 thrift 服务端。
* 学到了 maven 打 jar 包：配置一个 `maven-jar-plugin` 打包插件，配置一个`maven-dependency-plugin` 依赖复制插件。另外，打成 jar 包后获取 recourses 目录下文件，就无法使用先生成路径再获取流的方式，只能直接利用类加载器获取 inputstream。
* 学到了处理 tcp 粘包的方式。在`send_probe.py`里。
