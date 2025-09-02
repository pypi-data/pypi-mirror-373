# -*- coding: utf-8 -*-
# @Time    : 2022/10/23 18:56
# @Author  : mf.liang
# @File    : tools.py
# @Software: PyCharm
# @desc    :

import hashlib
import ipaddress
import platform
import re
from argparse import Namespace
from inspect import getmodule, stack
from typing import Optional
import yaml
from scapy.compat import raw
from scapy.config import conf
from scapy.interfaces import get_working_if, get_if_list
from scapy.arch import get_if_hwaddr
from scapy.layers.dhcp import DHCPTypes, DHCP, BOOTP
from scapy.layers.dhcp6 import dhcp6types, DHCP6OptIAAddress, DHCP6OptRelayMsg, DHCP6OptIAPrefix, DUID_LLT
from scapy.layers.inet import IP, UDP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether
from scapy.utils import mac2str, str2mac
from scapy.volatile import RandMAC
from dhcptool.env_args import pkt_result, logs, summary_result, global_var
import time


class Tools:

    @staticmethod
    def mac_self_incrementing_or_subtracting(mac, num, mac_type, offset=1) -> str:
        """
        mac自增
        :param mac_type:
        :param num:
        :param offset:
        :return:
        """
        mac = ''.join(mac.split(':'))
        #  使用format格式化字符串，int函数，按照16进制算法，将输入的mac地址转换成十进制，然后加上偏移量
        # {:012X}将十进制数字，按照16进制输出。其中12表示只取12位，0表示不足的位数在左侧补0
        if mac_type == 'ASC':
            mac_address = "{:012X}".format(int(mac, 16) + offset * num)
        else:
            mac_address = "{:012X}".format(int(mac, 16) - offset * num)
        mac_address = ':'.join(re.findall('.{2}', mac_address)).lower()
        return mac_address

    @staticmethod
    def get_mac(args: Namespace = None) -> bytes:
        """
        获取mac信息
        :return:
        """
        ip_type = Tools.check_ip_version(args.dhcp_server)
        if args.mac and args.fixe:
            mac = mac2str(args.mac)
        elif args.mac and not args.fixe:
            mac = Tools.mac_self_incrementing_or_subtracting(args.mac, global_var.get('tag'), 'ASC')
            mac = mac2str(mac)
        elif not args.mac and args.broadcast and ip_type == 'ipv4':
            mac = get_if_hwaddr(get_working_if().name)
            mac = Tools.mac_self_incrementing_or_subtracting(mac, global_var.get('tag'), 'ASC')
            mac = mac2str(mac)
        else:
            mac = mac2str(RandMAC())
        global_var.update({"generate_mac": mac})
        return mac

    @staticmethod
    def get_xid_by_mac(mac) -> int:
        """
        根据mac生成hash
        :return:
        """
        mac = str2mac(mac).encode('utf-8')
        m = hashlib.md5()
        m.update(mac)
        mac_xid = int(str(int(m.hexdigest(), 16))[0:9])
        return mac_xid

    @staticmethod
    def get_xid_by_duid(duid: DUID_LLT) -> int:
        """
        根据mac生成hash
        :return:
        """
        duid = raw(duid)
        m = hashlib.md5()
        m.update(duid)
        duid_xid = int(str(int(m.hexdigest(), 16))[0:9])
        return duid_xid

    @staticmethod
    def convert_code(data) -> hex:
        """
        字节/16进制相互转换
        :param data:
        :return:
        """
        if isinstance(data, bytes):  # 转 16进制
            data = data.hex()
        else:  # 字符串转化成字节码
            data = bytes.fromhex(data)
        return data

    @staticmethod
    def get_local_address():
        # 获取网络接口信息
        interfaces = [interface for interface in get_if_list() if interface.startswith('e')]
        # 遍历网络接口，查找IP地址
        try:
            for interface in interfaces:
                # 获取网络接口的详细信息
                ipv4_info = conf.ifaces[interface].ips[4]
                ipv6_info = conf.ifaces[interface].ips[6]
                ipv4_address = [i for i in ipv4_info if not i.startswith('127.')]
                ipv6_address = [i for i in ipv6_info if not i.startswith('fe80::')]
                return {"ipv4": ipv4_address, "ipv6": ipv6_address}
        except Exception as ex:
            logs.error(ex)
            return None

    @staticmethod
    def analysis_results(pkts_list, args: Namespace = None, call_name=None) -> None:
        """
        解析结果并存入队列
        :param args:
        :param pkts_list:
        :param DHCPv6:
        :param filter:
        :return:
        """
        filter_ip = args.dhcp_server
        call_func_name = getmodule(stack()[1][0])
        call_mod = call_func_name.__name__

        for pkt in pkts_list:
            if 'dhcp4' in call_mod:
                Tools.analysis_results_v4(pkt, args, filter_ip)
            else:
                Tools.analysis_results_v6(pkt, args, filter_ip, call_name)

    @staticmethod
    def analysis_results_v4(pkt, args, filter_ip) -> None:
        if pkt[IP].src == filter_ip:
            if pkt[DHCP].options[0][1] == 2:
                pkt_result.get('dhcp4_offer').put(pkt)
                Tools.print_formart(pkt, args.debug)
            elif pkt[DHCP].options[0][1] == 5:
                pkt_result.get('dhcp4_ack').put(pkt)
                Tools.print_formart(pkt, args.debug)
            elif pkt[DHCP].options[0][1] == 6:
                pkt_result.get('dhcp4_nak').put(pkt)
                Tools.print_formart(pkt, args.debug)
        else:
            logs.info('没有监听到 server 应答报文！,请检查是否有多个DHCP server影响监听结果')

    @staticmethod
    def analysis_results_v6(pkt, args, filter_ip, call_name=None, DHCPv6=None) -> None:
        if pkt[IPv6].src == filter_ip:
            if pkt[DHCPv6].msgtype == 2:
                try:
                    assert pkt[DHCP6OptIAAddress].addr
                    pkt_result.get('dhcp6_advertise').put(pkt)
                    if call_name is None:
                        Tools.print_formart(pkt, args.debug)
                except Exception as ex:
                    try:
                        assert pkt[DHCP6OptIAPrefix].prefix
                        pkt_result.get('dhcp6_advertise').put(pkt)
                        if call_name is None:
                            Tools.print_formart(pkt, args.debug)
                    except Exception as ex:
                        logs.error('应答报文中没有携带分配ip！')
                        assert False
            elif pkt[DHCPv6].msgtype == 7:
                pkt_result.get('dhcp6_reply').put(pkt)
                if call_name is None:
                    Tools.print_formart(pkt, args.debug)

            elif pkt[DHCPv6].msgtype == 13:
                ether_ipv6_udp = Ether() / IPv6(src=pkt[IPv6].src) / UDP()
                relay_pkt = ether_ipv6_udp / pkt[DHCP6OptRelayMsg].message
                Tools.analysis_results(pkts_list=relay_pkt, args=args, call_name=1)
                Tools.print_formart(pkt, args.debug)
        else:
            logs.info('没有监听到 server 应答报文！,请检查是否有多个DHCP server影响监听结果')

    @staticmethod
    def print_formart(pkt, debug) -> None:
        """
        格式化打印
        :param pkt:
        :param level:
        :return:
        """
        response_dict = {}
        if debug:
            pkt.show2()
        else:
            detail_info = pkt[UDP][1:].summary()
            mac = str2mac(global_var.get('generate_mac')) or ''
            if pkt.payload.name == 'IPv6':
                src_dst = pkt[IPv6].mysummary().split('(')[0]
                response_dict.update({"info": "{}".format(detail_info.split('/')[0])})
                content_format = Tools.print_formart_v6(pkt, response_dict, mac)
            else:
                src_dst = pkt[IP].mysummary().split('udp')[0]
                response_dict.update({"info": "{}".format(detail_info)})
                content_format = Tools.print_formart_v4(pkt, response_dict, mac)
            logs.info(content_format)
        Tools.record_pkt_num(pkt)

    @staticmethod
    def print_formart_v4(pkt, response_dict, mac) -> str:
        """
        DHCPv6格式化打印
        :param pkt:
        :param response_dict:
        :param mac:
        :return:
        """
        yiaddr = pkt[BOOTP].yiaddr
        response_dict.update({"yiaddr": yiaddr})
        yiaddr = response_dict.get('yiaddr') or ''
        info = response_dict.get('info') or ''
        content_format = "v4 | {:<} | {:<15} | {:<}".format(mac, yiaddr, info)
        return content_format

    @staticmethod
    def print_formart_v6(pkt, response_dict, mac) -> str:
        """
        DHCPv4格式化打印
        :param pkt:
        :param response_dict:
        :param mac:
        :return:
        """
        try:
            addr = pkt[DHCP6OptIAAddress].addr
            response_dict.update({"addr": addr})
            prefix = pkt[DHCP6OptIAPrefix].prefix
            response_dict.update({"prefix": prefix})
        except Exception as ex:
            if 'DHCP6OptIAAddress' in str(ex):
                try:
                    prefix = pkt[DHCP6OptIAPrefix].prefix
                    response_dict.update({"prefix": prefix})
                except:
                    pass
        addr = str(response_dict.get('addr') or '')
        prefix = str(response_dict.get('prefix') or '')
        info = str(response_dict.get('info') or '')
        content_format = "v6 | {:<} | NA: {:<15} | PD: {:<} | {:<}".format(mac, addr, prefix, info)
        return content_format

    @staticmethod
    def record_pkt_num(pkt, DHCPv6=None) -> None:
        try:
            for i in dhcp6types:
                if pkt[DHCPv6].msgtype == i:
                    summary_result[dhcp6types.get(i)] += 1
                    if pkt[DHCPv6].msgtype in (12, 13):
                        Tools.record_pkt_num(pkt[DHCP6OptRelayMsg].message)
        except:
            for v in DHCPTypes.values():
                pkt_type = pkt[DHCP].options[0][1]
                if isinstance(pkt_type, int):
                    pkt_type = DHCPTypes.get(pkt_type)
                if pkt_type == v:
                    summary_result[v.upper()] += 1

    @staticmethod
    def rate_print(text_tips, sleep_time) -> None:
        """
        倒计时打印
        :param text_tips:
        :param sleep_time:
        :return:
        """
        if sleep_time != 0:
            for i in range(sleep_time, 0, -1):
                if i == 1:
                    print("\r", text_tips, '倒计时', "{}".format(i), '', end="\n", flush=True)
                else:
                    print("\r", text_tips, '倒计时', "{}".format(i), '', end="", flush=True)
                time.sleep(1)

    @staticmethod
    def get_version_desc() -> str:
        version_desc = """
        dhcptool@1.1:
        2. 支持广播模式下配置指定的中继
        """
        return version_desc

    @staticmethod
    def check_ip_version(address) -> Optional[str]:
        # 尝试解析地址
        try:
            ip = ipaddress.ip_address(address)
            if isinstance(ip, ipaddress.IPv4Address):
                return 'ipv4'
            elif isinstance(ip, ipaddress.IPv6Address):
                return 'ipv6'
        except ValueError:
            print("无法解析该地址。")

    @staticmethod
    def read_yaml_config() -> dict:
        os_info = platform.system()
        yaml_config_path = 'dhcptool.yaml' if os_info == 'Windows' else '/etc/dhcptool.yaml'
        # 读取YAML文件
        with open(yaml_config_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return data

    @staticmethod
    def merge_args(cmd_args, ip_type) -> Namespace:
        """
        合并 config.yaml和  cmd_args的参数
        Args:
            cmd_args:
            ip_type:

        Returns: cmd_args

        """
        try:
            # 读取config.yaml中的参数配置
            config_args = Tools.read_yaml_config()
            # 根据ip_type 选择 ipv4的参数还是ipv6的参数
            config_args = config_args['v4'] if ip_type == 'ipv4' else config_args['v6']
            # 开始合并 options选项参数
            config_options = config_args.get('options') or {}
            if cmd_args.options:
                # 如果config_options存在参数
                cmd_options = [i.split('=') for i in cmd_args.options.split('&')]
                cmd_options = dict(cmd_options)
                # 将cmd_options参数覆盖config_option参数
                config_options.update(cmd_options)
            if config_options:
                config_options = {str(key): value for key, value in config_options.items()}
                # 将config_options转化为cmd_args格式的options结果
                config_options = list(config_options.items())
                config_options = ['='.join(option) for option in config_options]
                config_options = '&'.join(config_options)
            # 合并常规参数
            if cmd_args.ip_src is None and config_args.get('ip_src'):
                cmd_args.ip_src = config_args.get('ip_src')
            if cmd_args.dhcp_server is None and config_args.get('dhcp_server'):
                cmd_args.dhcp_server = config_args.get('dhcp_server')
            if cmd_args.relay_forward is None and config_args.get('relay_forward'):
                cmd_args.relay_forward = config_args.get('relay_forward')
            cmd_args.options = config_options
        except Exception as ex:
            pass
        return cmd_args

if __name__ == '__main__':
    ipv4, ipv6 = Tools.get_local_address()
    print(ipv4, ipv6)
