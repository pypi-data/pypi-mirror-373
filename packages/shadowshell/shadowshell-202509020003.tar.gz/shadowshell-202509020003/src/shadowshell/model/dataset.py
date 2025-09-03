#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

import pandas as pd

class DataSet():

    def __init__(self):
        pass

    def iterate_excel(self, file_path, callback):
        df = pd.read_excel(file_path)
        for row in df.iterrows():
            callback(row)