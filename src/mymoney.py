# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        mymoney.py.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/10/27 - 14:50
# --------------------------------------------------------
import os
import math
import xlwings as xw
from datetime import datetime
from xlwings import Sheet
from automotive import *


class AliPay(object):

    def __init__(self, people: bool):
        self.people = people

    @staticmethod
    def read_alipay(alipay_file: str) -> list:
        with open(alipay_file, "r", encoding="gbk") as f:
            return f.readlines()

    @staticmethod
    def filter_data(contents: list) -> list:
        contents = list(map(lambda x: x.replace("\n", ""), contents))
        return list(filter(lambda x: len(x.split(",")) == 17, contents))

    @staticmethod
    def handle_data(contents: list) -> list:
        final_data = []
        contents.pop(0)
        for content in contents:
            # excel需要的数据是交易类型	日期	分类	子分类	账户1	账户2	金额	成员	商家	项目	备注
            logger.debug(content)
            content = content.split(",")
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
                final_data.append((pay_data, pay_amount, pay_detail, pay_type, pay_status))
        return final_data

    def __filter_condition(self, x: tuple) -> list:
        condition1 = ("蚂蚁财富" not in x[2])
        condition2 = ("李小花" not in x[2]) if self.people else ("李哲" not in x[2])
        condition3 = ("医保消费" not in x[2])
        condition4 = ("理财买入" not in x[2])
        condition5 = ("大药房连锁" not in x[2])
        condition6 = ("基金申购" not in x[2])
        condition7 = ("基金销售" not in x[2])
        return condition1 and condition2 and condition3 and condition4 and condition5 and condition6 and condition7

    def separate_type(self, contents: list) -> tuple:
        out_come = list(filter(lambda x: x[3] == "支出", contents))
        pay = list(filter(self.__filter_condition, out_come))
        in_come = list(filter(lambda x: x[3] == "收入", contents))
        return pay, in_come

    @staticmethod
    def check_detail(pay_detail: str, check_list: (list, tuple)) -> bool:
        for content in check_list:
            if content in pay_detail:
                return True
        return False

    def get_category(self, pay_detail: str, pay_amount: str) -> tuple:
        alipay = "商品", "亲情卡"
        if self.people:
            if self.check_detail(pay_detail, alipay):
                account = "支付宝P"
            else:
                account = "招行信用卡P"
        else:
            account = "花呗S"
        # 类别
        category = "食品酒水"
        sub_category = "早餐"
        outsource = "唐家臻记", "紫燕百味鸡", "敖锦记烫油鹅", "掌柜土鸡片"
        lunch = "阿蠔海鲜焖面", "卢婆婆姜鸭面", "顺旺基", "荟福源", "宜宾燃面", "享米时", "老麻抄手", "西北面点王", \
                "袁记云饺", "籣州牛肉面", "成都鸡汤抄手", "大巴山猪脚饭", "卤鹅饭", "e特黄焖鸡瓦香鸡成都店", \
                "杨铭宇黄焖鸡米饭", "八二小区干海椒抄手", "晓武林烤鸭", "乡村基", "戊丰记卤肉饭", "沙县小吃成都银泰城店", \
                "喜水饺", "兵哥豌豆面", "福记羊肉米粉", "岭南牛杂", "自小田", "搪瓷盌小面成都伏龙北巷", "蚝门圣焱", "本味简餐厅", \
                "粤饺皇", "南城香冒烤鸭卤肉饭", "贰柒拾乐山干绍面", "拾小馆", "陕西面馆", "干辣椒抄手", "豆汤饭"
        vegetables = "登梅", "雪梅", "思忠", "*琴", "兰兰姐", "*再泉", "春儿", "蔡德文", "沈德全", "小兰蔬菜店", \
                     "玲利", "邓花椒"
        meat = "金忠食品", "邓哥鱼铺", "龙仕林", "成都泥厨子大食堂", "章相山", "ZXS", "黑龙滩生态鱼铺", "谢氏冷鲜店", "良波"
        out_eat = "金翠河烧鹅餐厅", "马帮冒菜", "实惠啤酒鸭", "麦当劳", "食其家", "正反面", "青羊区东方宫牛肉拉面店", "成都港九餐饮", \
                  "八二私房水饺", "鱼吖吖（武侯店）", "口味鲜面庄", "叶抄手", "雷四孃小吃", "朱记蛙三", "火舞凉山西昌原生烧烤", \
                  "万州烤鱼", "肯德基", "巴山豆花饭成都", "卡萨马可", "老北京炸酱面", "禾木烤肉", "峨眉山周记烧烤", "青年火锅店", \
                  "茵赫餐饮管理", "汉堡王", "热恋冰淇淋", "初壹饺子", "点都德", "跷脚牛肉", "外卖订单"
        drink = "书亦烧仙草", "星巴克", "书亦燒仙草", "Mii Coffee", "茶百道", "瑞幸咖啡", "GREYBOX COFFEE", "可口可乐", \
                "日记咖啡馆", "丸摩堂"
        super_market = "成都市北城天街店", "成都荆竹中路店", "麦德龙", "欧尚成都市高新店", "谊品生鲜", "高新店", "成都盒马", \
                       "成都中营贸易", "招商雍华府店", "万家V+南区", "银犁冷藏"
        snacks = "永辉(成都市银泰城店)", "面包新语(银泰城店)", "雪糕批发"
        pets = "鸡胸肉鲜", "猫", "伍德氏", "激光笔", "瑞爱康宠物医院", "猫砂"
        treat = "先生的酒桌"
        if self.check_detail(pay_detail, outsource):
            sub_category = "外购凉菜"
        elif "水果" in pay_detail:
            sub_category = "水果"
        elif self.check_detail(pay_detail, super_market):
            sub_category = "超市购物"
        elif self.check_detail(pay_detail, snacks):
            sub_category = "零食"
        elif self.check_detail(pay_detail, pets):
            category = "休闲娱乐"
            sub_category = "宠物"
        elif self.check_detail(pay_detail, treat):
            category = "人情费用"
            sub_category = "请客"
        elif "亲情卡" in pay_detail:
            category = "人情费用"
            sub_category = "孝敬父母"
        elif self.check_detail(pay_detail, meat):
            sub_category = "肉类"
        elif self.check_detail(pay_detail, lunch):
            sub_category = "中餐"
        elif self.check_detail(pay_detail, drink):
            sub_category = "饮料"
        elif self.check_detail(pay_detail, ("众安在线", "相互宝")):
            category = "金融保险"
            sub_category = "人身保险"
        elif self.check_detail(pay_detail, ("成都地铁运营有限公司", "轨道交通", "成都地铁")):
            category = "行车交通"
            sub_category = "地铁"
        elif self.check_detail(pay_detail, ("天府通APP", "公共交通")):
            category = "行车交通"
            if pay_amount <= "1.80" or pay_amount == "2.00":
                sub_category = "公交"
            else:
                sub_category = "地铁"
        elif self.check_detail(pay_detail, vegetables):
            sub_category = "蔬菜"
        elif self.check_detail(pay_detail, out_eat):
            sub_category = "外出美食"
        elif self.check_detail(pay_detail, ("谢孝元", "高筋鲜面")):
            sub_category = "面"
        elif self.check_detail(pay_detail, ("无感支付", "停车场", "瑞林")):
            category = "行车交通"
            sub_category = "停车"
        elif "燃气费" in pay_detail:
            category = "居家生活"
            sub_category = "燃气费"
        elif "电费" in pay_detail:
            category = "居家生活"
            sub_category = "电费"
        elif "滴滴快车" in pay_detail:
            category = "行车交通"
            sub_category = "打车"
        elif "火车票" in pay_detail:
            category = "行车交通"
            sub_category = "火车"
        elif self.check_detail(pay_detail, ("中国移动", "中国电信")):
            category = "交流通讯"
            sub_category = "手机费"
        elif self.check_detail(pay_detail, ("重庆华宇", "物业管理费")):
            category = "居家生活"
            sub_category = "物管费"
        elif "壳牌" in pay_detail:
            category = "行车交通"
            sub_category = "加油"
        elif "宜家家居" in pay_detail:
            category = "购物消费"
            sub_category = "家居日用"
        return category, sub_category, account

    def handle_pay(self, pay: list) -> list:
        # 转换成支出支持的方式
        # 交易类型	日期	分类	子分类	账户1	账户2	金额	成员	商家	项目	备注
        contents = []
        for content in pay:
            pay_data, pay_amount, pay_detail, pay_type, pay_status = content
            category, sub_category, account = self.get_category(pay_detail, pay_amount)
            contents.append(
                (pay_type, pay_data, category, sub_category, account, "", pay_amount, "", "", "", pay_detail))
        return contents

    @staticmethod
    def handle_in_come(in_come: list) -> list:
        # 转换成收入支持的方式
        # 交易类型	日期	分类	子分类	账户1	账户2	金额	成员	商家	项目	备注
        contents = []
        for content in in_come:
            pay_data, pay_amount, pay_detail, pay_type, pay_status = content
            # 类别
            category = "职业收入"
            sub_category = "利息收入"
            account = "支付宝P"
            contents.append(
                (pay_type, pay_data, category, sub_category, account, "", pay_amount, "", "", "", pay_detail))
        return contents

    def write_excel(self, pay: list, in_come: list):
        app = xw.App(visible=True, add_book=False)
        wb = app.books.open("template.xls")
        if self.people:
            in_come_sht = wb.sheets["收入"]
            in_come_sht.range("A2").value = in_come
        pay_sht = wb.sheets["支出"]
        pay_sht.range("A2").value = pay
        file = f"template_{Utils.get_time_as_string()}.xls"
        wb.save(file)
        wb.close()
        app.quit()

    def run(self, ali_file: str):
        contents = self.read_alipay(ali_file)
        contents = self.filter_data(contents)
        contents = self.handle_data(contents)
        pay, in_come = self.separate_type(contents)
        pay = self.handle_pay(pay)
        in_come = self.handle_in_come(in_come)
        self.write_excel(pay, in_come)


class Cmb(object):

    @staticmethod
    def __read_cmd(file: str) -> list:
        with open(file, "r", encoding="utf-8") as f:
            return f.readlines()

    @staticmethod
    def __filter_data(contents: list, remove: bool) -> list:
        contents = list(map(lambda x: x.replace("\n", ""), contents))
        # 去除多余的内容
        contents = list(filter(lambda x: len(x.split(" ")) == 6, contents))
        # 只保留具体内容
        contents = list(filter(lambda x: "/" in x, contents))
        if remove:
            # 去掉支付宝
            contents = list(filter(lambda x: "支付宝" not in x and "年费" not in x, contents))
        return contents

    @staticmethod
    def __split_contents(contents: list) -> list:
        exchanges = []
        # 交易类型	日期	分类	子分类	账户1	账户2	金额	成员	商家	项目	备注
        for content in contents:
            details = content.split(" ")
            date = details[0].replace("/", "-")
            pay_data = f"2020-{date}"
            pay_amount = details[3]
            pay_detail = details[2]
            pay_type = "支出"
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
            exchanges.append(
                (pay_type, pay_data, category, sub_category, account, "", pay_amount, "", "", "", pay_detail))
        return exchanges

    @staticmethod
    def write_excel(pay: list):
        # visible设置为False的时候可能产生错误
        app = xw.App(visible=False, add_book=False)
        wb = app.books.open("template.xls", read_only=True)
        pay_sht = wb.sheets["支出"]
        pay_sht.range("A2").value = pay
        file = f"template_cmb_{Utils.get_time_as_string()}.xls"
        wb.save(file)
        wb.close()
        app.quit()

    def get_content(self, file: str, remove: bool = True) -> list:
        contents = self.__read_cmd(file)
        contents = self.__filter_data(contents, remove)
        contents = self.__split_contents(contents)
        return contents

    def run(self, file: str):
        contents = self.get_content(file)
        self.write_excel(contents)


class MyMoney(object):

    def __init__(self):
        self.format_str = "%Y-%m-%d"
        self.account_type = "招行信用卡P"

    def handle_sheet(self, sheet: Sheet, count: int, start_date: str = None, end_date: str = None):
        """
        处理每行数据返回对象，并做filter处理
        """
        start_date = datetime.strptime(start_date.strip(), self.format_str) if start_date else -1
        end_date = datetime.strptime(end_date.strip(), self.format_str) if end_date else -1
        lines = []
        for i in range(1, count):
            index = i + 1
            logger.debug(f"{index} line")
            category = sheet.range(f"B{index}").value
            account = sheet.range(f"D{index}").value
            exchange = sheet.range(f"F{index}").value
            date = sheet.range(f"J{index}").value
            date = date.split(" ")[0]
            date_time = datetime.strptime(date, self.format_str)
            logger.debug(f"{index} line's account={account}, date={date_time}")
            if start_date != -1 and end_date != -1:
                # 3. 两个都传入了就是区间
                if date_time < start_date:
                    break
                elif start_date <= date_time <= end_date:
                    lines.append((category, account, exchange, date))
            elif start_date != -1 and end_date == -1:
                # 1. 只传入start_date表示从开始第一行到start_date所在行
                if date_time < start_date:
                    break
                elif start_date <= date_time:
                    lines.append((category, account, exchange, date))
            elif start_date == -1 and end_date == -1:
                # 2. 只传入end_date表示从end_date到最后一行
                if date_time <= end_date:
                    lines.append((category, account, exchange, date))
        lines = list(filter(lambda x: x[1].strip() == self.account_type, lines))
        return lines

    def get_mymoney_content(self, excel_file: str, start_date_time: str, end_date_time: str) -> list:
        app = xw.App(visible=False, add_book=False)
        wb = app.books.open(excel_file, read_only=True)
        pay_sht = wb.sheets["支出"]
        max_row = pay_sht.used_range.last_cell.row
        lines = self.handle_sheet(pay_sht, max_row, start_date_time, end_date_time)
        logger.debug(f"total line is {len(lines)}")
        wb.close()
        return lines

    @staticmethod
    def write_to_file(save_file: str, contents: list):
        with open(save_file, "w") as f:
            for content in contents:
                category, account, exchange, date = content
                f.write(f"{category}\t{account}\t{exchange}\t{date}\n")

    @staticmethod
    def get_content_from_file(txt_file: str) -> list:
        contents = []
        with open(txt_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace("\n", "")
                logger.debug(f"line = {line}")
                if line != "":
                    line_sep = line.split("\t")
                    category = line_sep[0]
                    account = line_sep[1]
                    exchange = line_sep[2]
                    date = line_sep[3]
                    contents.append((category, account, exchange, date))
        return contents


class Compare(object):

    def __init__(self):
        self.ali = AliPay(True)
        self.cmb = Cmb()
        self.my_money = MyMoney()
        self.wechat = Wechat()

    def compare(self, save_file: str, my_money_file: str, cmb_file: str, start_time: str, end_time: str):
        missing = []
        format_str = "%Y-%m-%d"
        # 获取随手记已记录的银行卡记录
        if not os.path.exists(save_file):
            contents = self.my_money.get_mymoney_content(my_money_file, start_time, end_time)
            self.my_money.write_to_file(save_file, contents)
        my_money_contents = self.my_money.get_content_from_file(save_file)
        # 获取招商银行的记录
        cmb_contents = self.cmb.get_content(cmb_file, False)
        for cmb_bank in cmb_contents:
            flag = True
            cmb_date = cmb_bank[1]
            cmb_date = datetime.strptime(cmb_date, format_str)
            cmb_price = cmb_bank[6].strip().replace("元", "").replace(",", "")
            for my_money_web in my_money_contents:
                my_money_date = my_money_web[3]
                my_money_date = datetime.strptime(my_money_date, format_str)
                my_money_price = my_money_web[2].strip().replace(",", "")
                logger.debug(f"cmb_date{cmb_date}, my_money_date{my_money_date}, "
                             f"cmb_price{cmb_price}, my_money_price{my_money_price}")
                if cmb_date == my_money_date and math.isclose(float(cmb_price), float(my_money_price), rel_tol=1e-5):
                    logger.debug("done")
                    flag = False
                    break
            if flag:
                missing.append(cmb_bank)
        for miss in missing:
            logger.info(miss)

    def run(self):
        files = self.wechat.get_wechat_files(r"C:\Users\philo\Downloads\temp\Music1")
        contents = self.wechat.walk_files(files)
        contents = self.wechat.parse_content(contents)
        contents = self.wechat.get_fire(contents)
        self.wechat.write_excel(contents)


class Wechat(object):

    @staticmethod
    def get_wechat_files(folder: str):
        files = os.listdir(folder)
        wechat_files = list(filter(lambda x: x.startswith("微信") and x.endswith(".csv"), files))
        return list(map(lambda x: f"{folder}\\{x}", wechat_files))

    @staticmethod
    def walk_files(files: list) -> list:
        contents = []
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                line_contents = f.readlines()
                for line in line_contents:
                    contents.append(line)
        return contents

    @staticmethod
    def parse_content(contents: list) -> list:
        exchanges = []
        contents = list(filter(lambda x: len(x.split(",")) == 11, contents))
        for content in contents:
            if "元" not in content:
                line_contents = content.split(",")
                date_time = line_contents[0]
                pay_type = line_contents[1]
                exchange_people = line_contents[2]
                change_type = line_contents[4]
                amount = line_contents[5].replace("¥", "")
                account = line_contents[6].replace("/", "零钱")
                exchange = date_time, pay_type, exchange_people, change_type, amount, account
                exchanges.append(exchange)
        exchanges = list(filter(lambda x: x[5] == "零钱", exchanges))
        return exchanges

    @staticmethod
    def get_fire(contents: list):
        return list(filter(lambda x: x[4].strip() == "8.00", contents))

    @staticmethod
    def __parse_excel(contents: list) -> list:
        exchanges = []
        # 交易类型	日期	分类	子分类	账户1	账户2	金额	成员	商家	项目	备注
        for content in contents:
            date_time, pay_type, exchange_people, change_type, amount, account = content
            pay_detail = f"{pay_type} {exchange_people}"
            pay_type = "支出"
            exchanges.append(
                (pay_type, date_time, "行车交通", "打车", "微信钱包P", "", amount, "", "", "", pay_detail))
        return exchanges

    def write_excel(self, contents: list):
        # visible设置为False的时候可能产生错误
        app = xw.App(visible=False, add_book=False)
        wb = app.books.open("template.xls", read_only=True)
        pay_sht = wb.sheets["支出"]
        pay_sht.range("A2").value = self.__parse_excel(contents)
        file = f"template_wechat_{Utils.get_time_as_string()}.xls"
        wb.save(file)
        wb.close()
        app.quit()


if __name__ == '__main__':
    save = r"D:\Workspace\github\code\temp\aaa.txt"
    my_money = r"C:\Users\philo\Downloads\temp\Music1\myMoney.xls"
    cmb = r"C:\Users\philo\Downloads\temp\Music1\CreditCardReckoning.txt"
    start = "2020-01-01"
    end = "2020-10-27"
    compare = Compare()
    # compare.compare(save, my_money, cmb, start, end)
    compare.run()
