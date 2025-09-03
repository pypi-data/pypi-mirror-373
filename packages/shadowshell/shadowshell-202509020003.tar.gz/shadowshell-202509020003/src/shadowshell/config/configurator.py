#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configurator
@author: shadowshell
"""

import configparser

from shadowshell.monitor import function_monitor

class_name = "Configurator"

class Configurator:

    __config = None;

    @function_monitor(class_name)
    def __init__(self, config_file):
        self.__config = configparser.ConfigParser()
        self.__config.read(config_file)
        
    @function_monitor(class_name)
    def get(self, group, key):
        value = self.__config.get(group, key)
        return value

    def __repr__(self):
        return self.__class__.__name__ 

