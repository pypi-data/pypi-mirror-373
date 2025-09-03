#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

from base_test import BaseTest
from src.shadowshell.xyz.xyz import Xyz


url = '/Users/shadowwalker/Downloads/线索报盘测试用例-单意图.xlsx'

import pandas as pd
import ast
import csv

# 读取 Excel 文件
df = pd.read_excel(url)

items = {""}

counter = 0
for index, row in df.iterrows():
    # counter += 1
    # if counter > 2:
    #     break

    cat_codes = row[0]
    print(cat_codes)

    if isinstance(cat_codes, (int, float, type(None))):
        continue

    for cat_code in ast.literal_eval(cat_codes):
        items.add(cat_code)

print(len(items))

for item in items:
    print(item)

with open('/Users/shadowwalker/Library/CloudStorage/OneDrive-个人/Files/服务管家最近三个月工单标签汇总.csv', mode='w', encoding='utf-8', newline='') as file:

    # 创建 csv.writer 对象
    csv_writer = csv.writer(file)
   
    # 写入数据
    for item in items:
        csv_writer.writerow([item])

