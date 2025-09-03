#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

import pandas as pd
df = pd.read_excel('/Users/shadowwalker/Downloads/线索报盘测试用例-单意图.xlsx', sheet_name = '有出租意愿')
for index, row in df.iterrows():
    print(row)