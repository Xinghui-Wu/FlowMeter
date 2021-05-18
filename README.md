# FlowMeter

Advanced Computer Networking and Communication Class Project

## 环境配置

OS: Windows 10

&emsp;&emsp;使用conda或viturlenv创建Python虚拟环境，启动该虚拟环境后，输入以下命令来配置环境。

    pip install -r requirements.txt


## Django项目启动

&emsp;&emsp;进入项目根目录并启动虚拟环境，输入以下命令启动Web服务。其中，0.0.0.0表示局域网内任意主机可访问，8000为端口号（也可替换为其它未被占用的端口号）。本机测试时，在浏览器中输入localhost:8000（或127.0.0.1:8000）来访问Web页面。

    python manage.py runserver 0.0.0.0:8000