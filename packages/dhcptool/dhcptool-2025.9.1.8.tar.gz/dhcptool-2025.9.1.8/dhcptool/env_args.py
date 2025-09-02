# -*- coding: utf-8 -*-
# @Time    : 2022/10/23 18:59
# @Author  : mf.liang
# @File    : env_args.py
# @Software: PyCharm
# @desc    :

import queue
import random
from dhcptool.Logings import Logings

# 事务id(可选)
xid = random.randint(1, 900000000)
summary_result = {}
global_var = {"tag": 0}
pkt_result = {
    "dhcp6_advertise": queue.Queue(),
    "dhcp6_reply": queue.Queue(),
    "dhcp4_offer": queue.Queue(),
    "dhcp4_ack": queue.Queue(),
    "dhcp4_nak": queue.Queue(),
}
logs = Logings("DHCP")
