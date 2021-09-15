# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        cmb.py
# @Author:      lizhe
# @Created:     2021/9/14 - 22:16
# --------------------------------------------------------
from typing import List, Tuple, Dict

from src.my_money import TemplateExcel, AbsOps, read_file, outcome


class Cmb(AbsOps):

    @staticmethod
    def __filter_data(file: str) -> List:
        contents = read_file(file)
        contents = list(map(lambda x: x.replace("\n", ""), contents))
        # 去除多余的内容
        contents = list(filter(lambda x: len(x.split(" ")) == 6 and "/" in x, contents))
        # 只保留具体内容
        # 去掉支付宝
        contents = list(filter(lambda x: "支付宝" not in x and "年费" not in x, contents))
        return contents

    @staticmethod
    def __split_contents(contents: List) -> List[TemplateExcel]:
        exchanges = []
        # 交易类型	日期	分类	子分类	账户1	账户2	金额	成员	商家	项目	备注
        for content in contents:
            details = content.split(" ")
            date = details[0].replace("/", "-")
            pay_data = f"2020-{date}"
            pay_amount = details[3]
            pay_detail = details[2]
            category = "购物消费"
            sub_category = "电子数码"
            account = "招行信用卡P"
            if "7FRESH" in content or "四季优选" in content:
                category = "食品酒水"
                sub_category = "超市购物"
            elif "餐饮" in content:
                category = "食品酒水"
                sub_category = "外出美食"
            elif "虾仁水饺" in content:
                category = "食品酒水"
                sub_category = "中餐"
            template_excel = TemplateExcel()
            template_excel.date = pay_data
            template_excel.category = category
            template_excel.sub_category = sub_category
            template_excel.account1 = account
            template_excel.amount = pay_amount
            template_excel.comment = pay_detail
            exchanges.append(template_excel)
        return exchanges

    def read(self, file: str) -> Dict[str, List[TemplateExcel]]:
        contents = self.__filter_data(file)
        return {outcome: self.__split_contents(contents)}


if __name__ == '__main__':
    cmb_file = r"C:\Users\lizhe\Downloads\Music20210914\CreditCardReckoning.txt"
    cmb = Cmb()
    result = cmb.read(cmb_file)
    cmb.write(result)
