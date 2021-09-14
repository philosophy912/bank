# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        my_money.py
# @Author:      lizhe
# @Created:     2021/9/14 - 22:12
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod
from typing import List, Tuple

outcome = "支出"
income = "收入"


class TemplateExcel(object):

    def __init__(self):
        # 交易类型
        self.exchange_type = ""
        # 日期
        self.date = ""
        # 分类
        self.category = ""
        # 子分类
        self.sub_category = ""
        # 账户1
        self.account1 = ""
        # 账户2
        self.account2 = ""
        # 金额
        self.amount = ""
        # 成员
        self.member = ""
        # 商家
        self.seller = ""
        # 项目
        self.project = ""
        # 备注
        self.comment = ""


class AbsOps(metaclass=ABCMeta):

    @abstractmethod
    def read(self, file: str) -> Tuple[List[TemplateExcel], List[TemplateExcel]]:
        pass

    def write(self, file: str, templates: List[TemplateExcel]):
        pass


def read_file(file: str, encoding: str = "utf-8") -> list:
    with open(file, "r", encoding=encoding) as f:
        return f.readlines()
