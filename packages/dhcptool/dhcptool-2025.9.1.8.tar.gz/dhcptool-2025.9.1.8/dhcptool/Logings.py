# -*- coding: utf-8 -*-
# @Time    : 2022/10/25 0:13
# @Author  : mf.liang
# @File    : Logings.py
# @Software: PyCharm
# @desc    :

import sys
import logging


class Logings(logging.Logger):
    def __init__(self, name, level=logging.INFO, file=None):
        """
        :param name: 日志名字
        :param level: 级别
        :param file: 日志文件名称
        """
        super().__init__(name, level)
        # 设置日志格式
        formatter = logging.Formatter("%(asctime)s,%(msecs)03d | %(message)s", datefmt="%H:%M:%S")
        # 文件输出渠道
        if file:
            handle2 = logging.FileHandler(file, encoding="utf-8")
            handle2.setFormatter(formatter)
            self.addHandler(handle2)
        # 控制台渠道
        handle1 = logging.StreamHandler(sys.stdout)
        handle1.setFormatter(formatter)
        self.addHandler(handle1)
