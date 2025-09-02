# 使用说明
### DHCPv4 模拟发包支持
```shell
[root@localhost ~]# ./dhcptool v4 -h
20230322 10:42:28 | 获取本机IP: 192.168.31.135
usage: dhcptool v4 [-h] [--num NUM] [--dhcp_server DHCP_SERVER] [--filter FILTER] [--relay_forward RELAY_FORWARD] [--options OPTIONS] [--message_type MESSAGE_TYPE] [--debug DEBUG] [--mac MAC]
                   [--sleep_time SLEEP_TIME]

optional arguments:
  -h, --help            show this help message and exit
  --num NUM, -n NUM     数量 例: dhcptool v4 -s 192.168.31.134 -n 10
  --dhcp_server DHCP_SERVER, -s DHCP_SERVER
                        DHCP服务器(单播) 例: dhcptool v4 -s 192.168.31.134
  --filter FILTER, -f FILTER
                        DHCP服务器(广播) 例: dhcptool v4 -f 192.168.31.134
  --relay_forward RELAY_FORWARD, -rf RELAY_FORWARD
                        填充giaddr 例: dhcptool v4 -s 192.168.31.134 -rf 192.168.31.1
  --options OPTIONS, -o OPTIONS
                        填充options 例: 格式:dhcptool v4 -s 192.168.31.134 -o [code]=[value]&[code]=[value] [dhcptool v4 -s 192.168.31.134 -o [12=yamu&7=1.1.1.1][82="eth 2/1/4:114.14 ZTEOLT001/1/1/5/0/1/000000000000001111111154
                        XE"][60=60:000023493534453……][55=12,7][50=192.168.31.199]
  --message_type MESSAGE_TYPE, -mt MESSAGE_TYPE
                        发送指定类型报文如 例: dhcptool v4 -s 192.168.31.134 -mt renew/release/decline/inform
  --debug DEBUG, -debug DEBUG
                        调试日志 例: dhcptool v4 -s 192.168.31.134 -debug on/off
  --mac MAC, -mac MAC   指定mac 例: dhcptool v4 -f 192.168.11.181 -mac 9a:cf:66:12:99:d1
  --sleep_time SLEEP_TIME, -st SLEEP_TIME
                        分配完成后的阶段设置等待进入下一阶段 例: dhcptool v4 -f 192.168.11.181 -st 1 -mt renew/release/decline/inform
```
### DHCPv6 模拟发包支持
```shell
[root@localhost ~]# ./dhcptool v6 -h
20230322 10:42:35 | 获取本机IP: 192.168.31.135
usage: dhcptool v6 [-h] [--num NUM] [--options OPTIONS] [--ipv6_src IPV6_SRC] [--message_type MESSAGE_TYPE] [--na_pd NA_PD] [--debug DEBUG] [--mac MAC] [--dhcp_server DHCP_SERVER] [--filter FILTER] [--relay_forward RELAY_FORWARD]
                   [--sleep_time SLEEP_TIME]

optional arguments:
  -h, --help            show this help message and exit
  --num NUM, -n NUM     数量 例: dhcptool v6 -f 1000:0:0:31::135 -n 10
  --options OPTIONS, -o OPTIONS
                        填充options 例: 格式:dhcptool v6 -f 1000:0:0:31::135 -o [code]=[value]&[code]=[value] [dhcptool v4 -s 192.168.31.134 -o [16=1f3……&14=][18="eth 2/1/4:114.14 ZTEOLT001/1/1/5/0/1/000000000000001111111154
                        XE"][60=60:000023493534453……][6=12,7][50=192.168.31.199]
  --ipv6_src IPV6_SRC, -src IPV6_SRC
                        指定ipv6源ip 例: dhcptool v6 -f 1000:0:0:31::135 -src 1000::31:350:9640:be36:46f6
  --message_type MESSAGE_TYPE, -mt MESSAGE_TYPE
                        发送指定类型报文如 例: dhcptool v6 -f 1000:0:0:31::135 -mt renew/release/decline
  --na_pd NA_PD, -np NA_PD
                        分配类型 例: dhcptool v6 -f 1000:0:0:31::135 -np na / pd / na/pd
  --debug DEBUG, -debug DEBUG
                        调试日志 例: dhcptool v4 -f 1000:0:0:31::135 -debug on/off
  --mac MAC, -mac MAC   指定mac 例: dhcptool v4 -f 1000:0:0:31::135 -mac 9a:cf:66:12:99:d1
  --dhcp_server DHCP_SERVER, -s DHCP_SERVER
                        中继单播发包 例: dhcptool v4 -s 1000:0:0:31::135 -rf 1000:0:0:31::1
  --filter FILTER, -f FILTER
                        DHCP服务器(广播) 例: dhcptool v4 -f 1000:0:0:31::135
  --relay_forward RELAY_FORWARD, -rf RELAY_FORWARD
                        中继地址 例: dhcptool v4 -f 1000:0:0:31::135 -rf 1000:0:0:31::1
  --sleep_time SLEEP_TIME, -st SLEEP_TIME
                        分配完成后的阶段设置等待进入下一阶段 例: dhcptool v4 -f 1000:0:0:31::135 -st 1 -mt renew/release/decline
```