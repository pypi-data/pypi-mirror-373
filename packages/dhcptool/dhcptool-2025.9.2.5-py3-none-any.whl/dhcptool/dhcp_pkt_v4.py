# -*- coding: utf-8 -*-
# @Time    : 2022/10/23 19:00
# @Author  : mf.liang
# @File    : dhcp_pkt_v6.py
# @Software: PyCharm
# @desc    :
from argparse import Namespace
from scapy.layers.dhcp import BOOTP, DHCP
from dhcptool.base_dhcp_pkt import BasePkt
from dhcptool.env_args import pkt_result
from dhcptool.options import Dhcp4Options
from dhcptool.tools import Tools


class Dhcp4Pkt(BasePkt):

    def __init__(self, args: Namespace) -> None:
        super(Dhcp4Pkt, self).__init__(args)
        self.udp.sport = 67
        self.udp.dport = 67

        self.ip.src = self.args.ip_src or Tools.get_local_address().get('ipv4') or '0.0.0.0'
        self.ip.dst = self.args.dhcp_server or '255.255.255.255'
        if self.args.broadcast:
            self.ether.dst = 'ff:ff:ff:ff:ff:ff'
            self.ip.src = '0.0.0.0'
            self.ip.dst = '255.255.255.255'
        self.bootp.giaddr = self.args.relay_forward or self.args.ip_src or Tools.get_local_address().get('ipv4')
        self.ether_ip_udp_bootp = self.ether / self.ip / self.udp / self.bootp
        self.make_options = Dhcp4Options(self.args)
        self.options_list = self.make_options.make_options_list()

    def make_pkts(self, message_type, **kwargs) -> DHCP:
        """
        组装  discover/request/decline/inform报文，
        :param message_type: 请求类型
        :return:
        """
        options = [("message-type", message_type)]
        if not self.args.single and message_type != 'discover':
            if message_type == 'request':
                response_pkt = pkt_result.get('dhcp4_offer').get(timeout=self.timeout)
                if kwargs.get('message') == 'exception_request':
                    response_pkt = BOOTP(yiaddr='0.0.0.1')
            else:
                response_pkt = pkt_result.get('dhcp4_ack').get(timeout=self.timeout)

            yiaddr = response_pkt[BOOTP].yiaddr
            options.append(("requested_addr", yiaddr))

        [options.append(i) for i in self.options_list]
        make_pkt = self.ether_ip_udp_bootp / DHCP(options=options)
        return make_pkt

    def dhcp4_discover(self) -> DHCP:
        """
        制作 discover包
        :return:
        """
        discover_pkt = self.make_pkts("discover")
        return discover_pkt

    def dhcp4_offer(self) -> DHCP:
        pass

    def dhcp4_request(self) -> DHCP:
        """
        制作 request包
        :return:
        """
        request_pkt = self.make_pkts('request')
        return request_pkt

    def dhcp4_exception_request(self) -> DHCP:
        """
        制作 一个会回nak的request包
        :return:
        """
        request_pkt = self.make_pkts('request', message='exception_request')
        return request_pkt

    def dhcp4_ack(self) -> DHCP:
        pass

    def dhcp4_decline(self) -> DHCP:
        """
        制作 decline包
        :return:
        """
        decline_pkt = self.make_pkts('decline')
        return decline_pkt

    def dhcp4_release(self) -> DHCP:
        """
        制作 release包
        :return:
        """
        release_pkt = self.make_pkts('release')
        return release_pkt

    def dhcp4_inform(self) -> DHCP:
        """
        制作 inform包
        :return:
        """
        inform_pkt = self.make_pkts('inform')
        return inform_pkt
