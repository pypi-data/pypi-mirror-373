#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger

@author: shadowshell
"""

class Logger:

    def debug(self, content):
        self.__log(content)
        
    def info(self, content):
        self.__log(content)

    def warn(self, content):
        self.__log(content)
    
    def error(self, content):
        self.__log(content)

    def __log(self, content):
        print("[LOGGER]%s" % content)

    def __repr__(self):
        return self.__class__.__name__ 
