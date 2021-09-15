# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        wechat.py
# @Author:      lizhe
# @Created:     2021/9/15 - 13:54
# --------------------------------------------------------
from typing import Tuple, List, Dict

from src.my_money import AbsOps, TemplateExcel, read_file, income, outcome, categories, contain_keyword


class Wechat(AbsOps):

    def __parse_content(self, contents: List) -> List[TemplateExcel]:
        exchanges = []
        for content in contents:
            line_contents = content.split(",")
            # 交易时间
            date_time = line_contents[0]
            # 交易类型
            pay_type = line_contents[1]
            # 交易对方
            exchange_people = line_contents[2]
            # 商品
            change_type = line_contents[4]
            # 金额
            amount = line_contents[5].replace("¥", "")
            # 支付方式
            account = line_contents[6].replace("/", "零钱")
            if account not in ("招商银行(4319)", "成都银行(7157)"):
                template_excel = TemplateExcel()
                template_excel.exchange_type = change_type
                template_excel.date = date_time
                category, sub_category = self.__get_category(amount, exchange_people)
                template_excel.category = category
                template_excel.sub_category = sub_category
                template_excel.account1 = "微信钱包P"
                template_excel.amount = amount
                template_excel.comment = f"{exchange_people} {pay_type}"
                exchanges.append(template_excel)
        return exchanges

    @staticmethod
    def __get_category(amount: str, exchange_people: str) -> Tuple:
        category_name = ""
        sub_category_name = ""
        for category, category_dict in categories.items():
            for sub_category, detail_list in category_dict.items():
                if contain_keyword(detail_list, exchange_people):
                    category_name = category
                    sub_category_name = sub_category
                    break
        if amount == "8.00":
            category_name = "行车交通"
            sub_category_name = "打车"
        return category_name, sub_category_name

    @staticmethod
    def __separate_type(file: str) -> Tuple:
        contents = read_file(file)
        contents = list(filter(lambda x: len(x.split(",")) == 11, contents))
        contents.pop(0)
        contents = list(map(lambda x: x.replace("\n", ""), contents))
        in_come = list(filter(lambda x: x.split(",")[4] == income, contents))
        out_come = list(filter(lambda x: x.split(",")[4] == outcome, contents))
        return in_come, out_come

    def read(self, file: str) -> Dict[str, List[TemplateExcel]]:
        in_come, out_come = self.__separate_type(file)
        in_come_list = self.__parse_content(in_come)
        out_come_list = self.__parse_content(out_come)
        return {income: in_come_list, outcome: out_come_list}


if __name__ == '__main__':
    wechat_file = fr"C:\Users\lizhe\Downloads\Music20210914\wechat.csv"
    wechat = Wechat()
    result = wechat.read(wechat_file)
    wechat.write(result)
