#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

from base_test import BaseTest
from src.shadowshell.logging.logger_factory import LoggerFactory
from src.shadowshell.logging.logging_constants import LoggingConstants

LoggingConstants.logging_conf_dir = '/Users/shadowwalker/shadowshellxyz/shadowshell/config/logging.conf'

LoggerFactory.init()
LoggerFactory.get_logger('root').debug("日志内容")




