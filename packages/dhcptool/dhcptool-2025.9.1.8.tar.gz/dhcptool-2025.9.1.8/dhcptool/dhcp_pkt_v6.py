# -*- coding: utf-8 -*-
# @Time    : 2022/10/23 19:00
# @Author  : mf.liang
# @File    : dhcp_pkt_v6.py
# @Software: PyCharm
# @desc    :
import copy
import uuid
from scapy.layers.dhcp6 import (
    DHCP6OptClientId,
    DHCP6OptIA_NA,
    DHCP6OptIA_PD,
    DHCP6OptServerId,
    DHCP6_RelayForward,
    DUID_LLT,
    DUID_LL,
    DUID_UUID,
    DHCP6OptRelayMsg,
    DHCP6OptIfaceId,
    DUID_EN,
    DHCP6, All_DHCP_Relay_Agents_and_Servers, DHCP6OptSubscriberID
)
from dhcptool.base_dhcp_pkt import BasePkt
from dhcptool.env_args import pkt_result
from dhcptool.options import Dhcp6Options
from typing import Union

from dhcptool.tools import Tools


class Dhcp6Pkt(BasePkt):

    def __init__(self, args) -> None:
        super(Dhcp6Pkt, self).__init__(args)
        self.ipv6.src = self.args.ip_src or Tools.get_local_address().get('ipv6')
        self.ipv6.src = self.args.ip_src

        # TODO: 同网段下 使用 单播，和异网段下使用单播，可以尝试去掉或加上这个试试，具体效果没有尝试
        if not self.args.broadcast:
            self.ipv6.dst = self.args.dhcp_server or All_DHCP_Relay_Agents_and_Servers

        self.ether_ipv6_udp = self.ether / self.ipv6 / self.udp
        self.duid = DUID_LLT(lladdr=self.mac, timeval=self.xid)
        if self.args.duid:
            if self.args.duid == 'llt':
                self.duid = DUID_LLT(lladdr=self.mac, timeval=self.xid)
            elif self.args.duid == 'll':
                self.duid = DUID_LL(lladdr=self.mac)
            elif self.args.duid == 'en':
                self.duid = DUID_EN(enterprisenum=1058949886, id=bytes.fromhex('7db44f928a1d4ef7c842c434'))
            elif self.args.duid == 'uuid':
                self.duid = DUID_UUID(uuid=uuid.uuid4())
            else:
                self.duid = bytes.fromhex(self.args.duid)
        self.opt_client_id = DHCP6OptClientId(duid=self.duid)
        self.duid_en = DUID_EN(enterprisenum=1058949886, id=bytes.fromhex('7db44f928a1d4ef7c842c434'))
        self.duid_xid = Tools.get_xid_by_duid(self.duid)
        self.opt_ia_na = DHCP6OptIA_NA(iaid=self.duid_xid)
        self.opt_ia_pd = DHCP6OptIA_PD(iaid=self.duid_xid)
        self.opt_server_id = DHCP6OptServerId(duid=self.duid_en)
        self.relay_forward = DHCP6_RelayForward(linkaddr=self.args.relay_forward)
        self.make_options = Dhcp6Options(self.args)
        self.options_list, self.parent_options_list = self.make_options.make_options_list()
        self.dhcp6_options = self.make_options.parse_options()

    def make_pkts(self, message_type) -> DHCP6:
        """
        解析并制作报文
        :param message_type: 报文消息类型
        :return:
        """
        opt_client_id = self.opt_client_id / self.opt_server_id
        if self.args.single and self.dhcp6_options:
            for option in self.dhcp6_options:
                if int(option[0]) == 5:
                    self.opt_ia_na.ianaopts.append(self.make_options.sub_option_5(addr=option[1]))
                    opt_client_id.add_payload(self.opt_ia_na)
                if int(option[0]) == 26:
                    self.opt_ia_pd.iapdopt.append(self.make_options.sub_option_26(prefix=option[1]))
                    opt_client_id.add_payload(self.opt_ia_pd)
        else:
            if message_type == 'request':
                reply_pkt = pkt_result.get('dhcp6_advertise').get(timeout=self.timeout)

            else:
                reply_pkt = pkt_result.get('dhcp6_reply').get(timeout=self.timeout)
            opt_client_id = reply_pkt[DHCP6OptClientId]

        pkt = self.ether_ipv6_udp / self.dhcp6 / opt_client_id / self.options_list
        return pkt

    def dhcp6_solicit(self) -> Union[DHCP6, DHCP6_RelayForward]:
        """
        制作solicit包
        :return:
        """
        self.dhcp6.msgtype = 'SOLICIT'
        if self.dhcp6_options:
            for option in self.dhcp6_options:
                if int(option[0]) == 5:
                    self.opt_ia_na.ianaopts.append(self.make_options.sub_option_5(addr=option[1]))
                elif int(option[0]) == 26:
                    self.opt_ia_pd.iapdopt.append(self.make_options.sub_option_26(prefix=option[1]))
        # 拼接数据包
        solicit_pkt = self.ether_ipv6_udp / self.dhcp6 / self.opt_client_id
        if not self.args.pd or self.args.na:  # NA
            solicit_pkt.add_payload(self.opt_ia_na)
        if self.args.pd:  # PD
            solicit_pkt.add_payload(self.opt_ia_pd)
        solicit_pkt.add_payload(self.options_list)
        if self.args.broadcast is False:
            solicit_pkt = self.dhcp6_relay_ward(self.parent_options_list, solicit_pkt[DHCP6])
            return solicit_pkt

        return solicit_pkt

    def dhcp6_advertise(self) -> Union[DHCP6, DHCP6_RelayForward]:
        pass

    def dhcp6_request(self) -> Union[DHCP6, DHCP6_RelayForward]:
        """
        制作request包
        :return:
        """
        self.dhcp6.msgtype = 'REQUEST'
        request_pkt = self.make_pkts('request')
        if self.args.broadcast is False:
            request_pkt = self.dhcp6_relay_ward(self.parent_options_list, request_pkt[DHCP6])
            return request_pkt
        return request_pkt

    def dhcp6_reply(self) -> DHCP6:
        pass

    def dhcp6_renew(self) -> Union[DHCP6, DHCP6_RelayForward]:
        """
        制作renew包
        :return:
        """
        self.dhcp6.msgtype = 'RENEW'
        renew_pkt = self.make_pkts('renew')
        if self.args.broadcast is False:
            renew_pkt = self.dhcp6_relay_ward(self.parent_options_list, renew_pkt[DHCP6])
            return renew_pkt
        return renew_pkt

    def dhcp6_release(self) -> Union[DHCP6, DHCP6_RelayForward]:
        """
        制作release包
        :return:
        """
        self.dhcp6.msgtype = 'RELEASE'
        release_pkt = self.make_pkts('release')
        if self.args.broadcast is False:
            release_pkt = self.dhcp6_relay_ward(self.parent_options_list, release_pkt[DHCP6])
            return release_pkt
        return release_pkt

    def dhcp6_decline(self) -> Union[DHCP6, DHCP6_RelayForward]:
        """
        制作decline包
        :return:
        """
        self.dhcp6.msgtype = 'DECLINE'
        decline_pkt = self.make_pkts('decline')
        if self.args.broadcast is False:
            decline_pkt = self.dhcp6_relay_ward(self.parent_options_list, decline_pkt[DHCP6])
            return decline_pkt
        return decline_pkt


    def dhcp6_relay_ward(self,parent_options=None, pkt=None) -> DHCP6_RelayForward:
        """
        制作中继包
        :return:
        """
        relay_forward_pkt = self.ether_ipv6_udp / self.relay_forward
        if parent_options:
            relay_forward_pkt = relay_forward_pkt / parent_options
        if pkt:
            relay_forward_pkt.add_payload(DHCP6OptRelayMsg(message=pkt))
        return relay_forward_pkt
