#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   code_call_exec.py
@Time    :   2023/08/10 14:25:02
@Author  :   mf.liang
@Version :   1.0
@Contact :   mf.liang@outlook.com
@Desc    :
"""

from ipaddress import IPv4Address, IPv6Address
from typing import NewType, Text

from main import dhcp_code_call_main

MACAddress = NewType('MACAddress', str)


def dhcp4_tool(server: IPv4Address = None,
               relay: IPv4Address = None,
               filter: IPv4Address = None,
               ip_src: IPv4Address = None,
               single: bool = False,
               discover: bool = False,
               request: bool = False,
               inform: bool = False,
               nak: bool = False,
               renew: bool = False,
               release: bool = False,
               decline: bool = False,
               mac: MACAddress = None,
               num: int = 1,
               debug: bool = False,
               options: Text = None) -> None:
    """执行dhcp4发包

    Args:
        server (IPv4Address, optional): _description_. Defaults to None.
        relay (IPv4Address, optional): _description_. Defaults to None.
        filter (IPv4Address, optional): _description_. Defaults to None.
        ip_src (IPv4Address, optional): _description_. Defaults to None.
        single (bool, optional): _description_. Defaults to False.
        discover (bool, optional): _description_. Defaults to False.
        request (bool, optional): _description_. Defaults to False.
        inform (bool, optional): _description_. Defaults to False.
        nak (bool, optional): _description_. Defaults to False.
        renew (bool, optional): _description_. Defaults to False.
        release (bool, optional): _description_. Defaults to False.
        decline (bool, optional): _description_. Defaults to False.
        mac (MACAddress, optional): _description_. Defaults to None.
        num (int, optional): _description_. Defaults to 1.
        debug (bool, optional): _description_. Defaults to False.
        options (Text, optional): _description_. Defaults to None.
    """
    args_cmd_list = ['v4']

    dhcp_code_call_main(args_cmd_list)


def dhcp6_tool(server: IPv6Address = None,
               relay: IPv6Address = None,
               filter: IPv6Address = None,
               ip_src: IPv6Address = None,
               single: bool = False,
               na: bool = False,
               pd: bool = False,
               solicit: bool = False,
               renew: bool = False,
               release: bool = False,
               decline: bool = False,
               mac: MACAddress = None,
               num: int = 1,
               debug: bool = False,
               options: Text = None) -> None:
    """执行dhcp6发包

    Args:
        server (IPv6Address, optional): _description_. Defaults to None.
        relay (IPv6Address, optional): _description_. Defaults to None.
        filter (IPv6Address, optional): _description_. Defaults to None.
        ip_src (IPv6Address, optional): _description_. Defaults to None.
        single (bool, optional): _description_. Defaults to False.
        discover (bool, optional): _description_. Defaults to False.
        request (bool, optional): _description_. Defaults to False.
        inform (bool, optional): _description_. Defaults to False.
        nak (bool, optional): _description_. Defaults to False.
        renew (bool, optional): _description_. Defaults to False.
        release (bool, optional): _description_. Defaults to False.
        decline (bool, optional): _description_. Defaults to False.
        mac (MACAddress, optional): _description_. Defaults to None.
        num (int, optional): _description_. Defaults to 1.
        debug (bool, optional): _description_. Defaults to False.
        options (Text, optional): _description_. Defaults to None.
    """
    args_cmd_list = ['v6']
    dhcp_code_call_main(args_cmd_list)


if __name__ == '__main__':
    dhcp4_tool()
    # dhcp6_tool()
