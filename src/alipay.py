# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        alipay.py
# @Author:      lizhe
# @Created:     2021/9/14 - 22:28
# --------------------------------------------------------
from datetime import datetime
from typing import List, Dict

from automotive import logger

from src.my_money import AbsOps, TemplateExcel, read_file, outcome, income, categories, contain_keyword


class Alipay(AbsOps):

    @staticmethod
    def __filter_data(file: str) -> List:
        contents = read_file(file, encoding="gbk")
        contents = list(map(lambda x: x.replace("\n", ""), contents))
        contents = list(filter(lambda x: len(x.split(",")) == 17, contents))
        contents.pop(0)
        return contents

    @staticmethod
    def __first_filter(x: tuple) -> bool:
        detail = f"{x[7]} {x[8]}"
        keywords = ["蚂蚁财富", "李哲", "医保消费", "理财买入", "大药房连锁", "基金申购", "基金销售",
                    "医保支付", "转账", "电脑补贴", "转接线端子", "电阻", "笔记本电脑支架", "TianBakery"]
        return not contain_keyword(keywords, detail)

    def __separate_type(self, contents: List) -> tuple:
        """
        分离支出和收入
        :param contents:
        :return:
        """
        out_come_list = list(map(lambda x: x.replace("\t", "").split(","), contents))
        out_come_list = list(filter(lambda x: x[10].strip() == outcome, out_come_list))
        out_come_list = list(filter(self.__first_filter, out_come_list))
        in_come_list = list(filter(lambda x: x.replace("\t", "").split(",")[10].strip() == income, contents))
        return out_come_list, in_come_list

    def __handle_data(self, contents: List) -> List[TemplateExcel]:
        final_data = []
        for content in contents:
            # excel需要的数据是交易类型	日期	分类	子分类	账户1	账户2	金额	成员	商家	项目	备注
            logger.debug(content)
            # 付款时间
            pay_date = content[2].strip()
            # 付款金额
            pay_amount = content[9].strip()
            # 交易类型
            pay_type = content[10].strip()
            # 交易状态
            pay_status = content[16].strip()
            # 详情
            pay_detail = f"{content[8].strip()},{content[7].strip()}"
            if pay_type != "":
                template_excel = self.__handle_template(pay_date, pay_amount, pay_detail, pay_type, pay_status)
                final_data.append(template_excel)
        return final_data

    def __handle_template(self, pay_date: str, pay_amount: str, pay_detail: str, pay_type: str,
                          pay_status: str) -> TemplateExcel:
        logger.debug(f"pay_date = {pay_date}")
        logger.debug(f"pay_amount = {pay_amount}")
        logger.debug(f"pay_detail = {pay_detail}")
        logger.debug(f"pay_type = {pay_type}")
        logger.debug(f"pay_status = {pay_status}")
        template_excel = TemplateExcel()
        template_excel.exchange_type = pay_type
        template_excel.date = pay_date
        category, sub_category = self.__get_category(pay_detail, pay_amount, pay_date)
        template_excel.category = category
        template_excel.sub_category = sub_category
        template_excel.amount = pay_amount
        template_excel.account1 = self.__get_account(pay_detail)
        template_excel.comment = pay_detail
        return template_excel

    @staticmethod
    def __get_account(pay_detail: str):
        keywords = ["商品", "亲情卡", "收钱码"]
        if contain_keyword(keywords, pay_detail):
            return "支付宝P"
        else:
            return "招行信用卡P"

    def __get_category(self, pay_detail: str, pay_amount: str, pay_date: str) -> tuple:
        category_name = ""
        sub_category_name = ""
        for category, category_dict in categories.items():
            for sub_category, detail_list in category_dict.items():
                if contain_keyword(detail_list, pay_detail):
                    # 特殊处理公交地铁
                    if category == "行车交通":
                        category_name = category
                        if pay_amount in ("1.80", "2.00"):
                            sub_category_name = "公交"
                    else:
                        category_name = category
                        sub_category_name = sub_category
                    break
        if "佳佳乐" in pay_detail:
            exchange_time = self._utils.convert_string_datetime(pay_date, "%Y-%m-%d %H:%M:%S")
            year, month, day = exchange_time.year, exchange_time.month, exchange_time.day
            start = datetime(year, month, day, 7, 0, 0)
            end = datetime(year, month, day, 10, 0, 0)
            category_name = "食品酒水"
            if start <= exchange_time <= end:
                sub_category_name = "早餐"
            else:
                pay_amount = float(pay_amount)
                if pay_amount <= 6:
                    sub_category_name = "饮料"
                else:
                    sub_category_name = "调味品"
        if "wowo" in pay_detail.lower():
            exchange_time = self._utils.convert_string_datetime(pay_date, "%Y-%m-%d %H:%M:%S")
            year, month, day = exchange_time.year, exchange_time.month, exchange_time.day
            start = datetime(year, month, day, 8, 0, 0)
            end = datetime(year, month, day, 10, 0, 0)
            category_name = "食品酒水"
            if start <= exchange_time <= end:
                sub_category_name = "早餐"
            else:
                sub_category_name = "零食"
        return category_name, sub_category_name

    def read(self, file: str) -> Dict[str, List[TemplateExcel]]:
        contents = self.__filter_data(file)
        out_come_list, in_come_list = self.__separate_type(contents)
        out_come = self.__handle_data(out_come_list)
        in_come = self.__handle_data(in_come_list)
        return {income: in_come, outcome: out_come}


if __name__ == '__main__':
    alipay = Alipay()
    result = alipay.read(r"C:\Users\lizhe\Downloads\Music20210914\alipay_record_20210914_2210_1.csv")
    for value in result[outcome]:
        if value.category == "":
            print(value)
    # print(result[outcome])
