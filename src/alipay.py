# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        alipay.py
# @Author:      lizhe
# @Created:     2021/9/14 - 22:28
# --------------------------------------------------------
from typing import List, Dict, Tuple

from automotive import logger

from src.my_money import AbsOps, TemplateExcel, read_file, outcome, income


class Alipay(AbsOps):

    @staticmethod
    def __filter_data(file: str) -> List:
        contents = read_file(file, encoding="gbk")
        contents = list(map(lambda x: x.replace("\n", ""), contents))
        contents = list(filter(lambda x: len(x.split(",")) == 17, contents))
        contents.pop(0)
        return contents

    def __separate_type(self, contents: List) -> tuple:
        out_come_list = list(map(lambda x: x.replace("\t", "").split(","), contents))
        out_come_list = list(filter(lambda x: x[10].strip() == outcome, out_come_list))
        out_come_list = list(filter(self.__filter_condition, out_come_list))
        in_come_list = list(filter(lambda x: x.replace("\t", "").split(",")[10].strip() == income, contents))
        return out_come_list, in_come_list

    def __handle_data(self, contents: List) -> List[TemplateExcel]:
        final_data = []
        for content in contents:
            # excel需要的数据是交易类型	日期	分类	子分类	账户1	账户2	金额	成员	商家	项目	备注
            logger.debug(content)
            # 付款时间
            pay_data = content[2].strip()
            # 付款金额
            pay_amount = content[9].strip()
            # 交易类型
            pay_type = content[10].strip()
            # 交易状态
            pay_status = content[16].strip()
            # 详情
            pay_detail = f"{content[8].strip()},{content[7].strip()}"
            if pay_type != "":
                template_excel = self.__handle_template(pay_data, pay_amount, pay_detail, pay_type, pay_status)
                final_data.append(template_excel)
        return final_data

    def __handle_template(self, pay_data: str, pay_amount: str, pay_detail: str, pay_type: str,
                          pay_status: str) -> TemplateExcel:
        logger.info(f"pay_data = {pay_data}")
        logger.info(f"pay_amount = {pay_amount}")
        logger.info(f"pay_detail = {pay_detail}")
        logger.info(f"pay_type = {pay_type}")
        logger.info(f"pay_status = {pay_status}")
        template_excel = TemplateExcel()
        template_excel.exchange_type = pay_type
        template_excel.date = pay_data
        category, sub_category = self.__get_category(pay_detail, pay_amount)
        template_excel.category = category
        template_excel.sub_category = sub_category
        return template_excel

    def __get_category(self, pay_detail: str, pay_amount: str) -> tuple:
        pass

    @staticmethod
    def __filter_condition(x: tuple) -> bool:
        condition1 = "蚂蚁财富" in x[2]
        condition2 = "李哲" in x[2]
        condition3 = "医保消费" in x[2]
        condition4 = "理财买入" in x[2]
        condition5 = "大药房连锁" in x[2]
        condition6 = "基金申购" in x[2]
        condition7 = "基金销售" in x[2]
        return not (condition1 or condition2 or condition3 or condition4 or condition5 or condition6 or condition7)

    def read(self, file: str) -> Dict[str, List[TemplateExcel]]:
        contents = self.__filter_data(file)
        out_come_list, in_come_list = self.__separate_type(contents)
        out_come = self.__handle_data(out_come_list)
        in_come = self.__handle_data(in_come_list)
        return {income: in_come, outcome: out_come}


if __name__ == '__main__':
    alipay = Alipay()
    alipay.read(r"C:\Users\lizhe\Downloads\Music20210505\alipay_record_20210914_2210_1.csv")
