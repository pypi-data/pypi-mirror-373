# coding = 'utf-8'
"""
@File:          extend_tools_controller.py
@Time:          2023/7/20 16:30
@Author:        mf.liang
@Email:         mf.liang@yamu.com
@Desc:          请注明模块要实现的功能

"""
import ipaddress
from scapy.volatile import RandMAC
from dhcptool.env_args import logs
from dhcptool.tools import Tools


class ExtendToolsController:

    def __init__(self, args):
        self.args = args

    def generate_print_mac(self) -> None:
        """
        生成并打印mac
        :return:
        """
        init_mac = str(RandMAC())
        for i in range(self.args.num if self.args.num != 1 else 100):
            if self.args.generate_mac == 'random':
                mac = str(RandMAC())
            elif self.args.generate_mac == 'asc':
                mac = Tools.mac_self_incrementing_or_subtracting(init_mac, i, 'ASC')
            else:
                mac = Tools.mac_self_incrementing_or_subtracting(init_mac, i, 'DESC')
            print(mac)

    def calculate_address_range(self) -> None:
        """
        计算IPv4/IPv6的地址范围
        :return:
        """
        address, mask_length = tuple(self.args.generate_address.split('/'))
        if self.args.ipv4:
            network = ipaddress.IPv4Network(address + '/' + str(mask_length), strict=False)
        if self.args.ipv6:
            network = ipaddress.IPv6Network(address + '/' + str(mask_length), strict=False)
            if self.args.pd:
                network = ipaddress.IPv6Network(address + '/' + str(mask_length), strict=False)
                network_pd = network.subnets(new_prefix=self.args.pd)
                pd_address = [str(ip) for ip in network_pd]
                logs.info(f"前缀地址：{pd_address}")

        logs.info(f"地址划分：{self.args.generate_address}")
        logs.info(f"地址类型：{network.version}")
        logs.info(f"主机掩码：{network.with_hostmask}")
        logs.info(f"地址数量：{network.num_addresses}")
        logs.info(f"起始范围：{network.network_address} - {network.broadcast_address}")
        addresses = [str(ip) for ip in network]
        logs.info(f"起始地址：{addresses[:256 // 2] + ['...'] + addresses[-256 // 2:]}")
