#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ConsoleLogger

author: shadow shell
"""

from .logger import Logger

class LoggingLogger(Logger):
    
    def __init__(self, logger):
        self.__logger = logger
    def debug(self, content):
        self.__logger.debug(content)
    def info(self, content):
        self.__logger.info(content)

    def warn(self, content):
        self.__logger.warn(content, exc_info = True)
    
    def error(self, content):
        self.__logger.error(content, exc_info = True)

