#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ConsoleLogger

author: shadow shell
"""

from .logger import Logger
from .logging_constants import LoggingConstants

class ConsoleLogger(Logger):

    def debug(self, content):
        if LoggingConstants.LEVEL_DEBUG is True:
            self.__log("DEBUG", content)     
    def info(self, content):
        if LoggingConstants.LEVEL_INFO is True:
            self.__log("INFO", content)

    def warn(self, content):
        if LoggingConstants.LEVEL_WARN is True:
            self.__log("WARN", content)
    
    def error(self, content):
        if LoggingConstants.LEVEL_ERROR is True:
            self.__log("ERROR", content)

    def __log(self, key, content):
        print("[%s]%s" % (key, content))
