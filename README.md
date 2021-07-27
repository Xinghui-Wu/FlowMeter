# FlowMeter

## 网络设备流量检测与网络行为分析

* 检测网络设备，并对指定的网络设备实时抓取数据包。
* 处理数据包，提取数据包中的基本属性。针对数据包的地理位置、关联应用进行流量地理位置、应用分析。
* 根据数据包统计连接，分析连接的基本属性，针对连接进行突发流量检测等网络行为分析。


## 环境配置

操作系统：Windows 10

&emsp;&emsp;使用conda或viturlenv创建Python虚拟环境，启动该虚拟环境后，输入以下命令来配置环境。

    pip install -r requirements.txt

&emsp;&emsp;在Windows平台下，为了保证能够进行流量抓取，还需要安装WinPcap。

&emsp;&emsp;Npcap是Windows的Nmap项目的数据包嗅探（和发送）库。它基于已停产的WinPcap库，但具有提高的速度，可移植性，安全性和效率。

    https://nmap.org/npcap/dist/npcap-1.31.exe


## Django项目启动

&emsp;&emsp;进入项目根目录并启动虚拟环境，输入以下命令启动Web服务。其中，0.0.0.0表示局域网内任意主机可访问，8000为端口号（也可替换为其它未被占用的端口号）。本机测试时，在浏览器中输入localhost:8000（或127.0.0.1:8000）来访问Web页面。

    python manage.py runserver 0.0.0.0:8000