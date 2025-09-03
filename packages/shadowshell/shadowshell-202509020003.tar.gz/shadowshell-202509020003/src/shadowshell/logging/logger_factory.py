#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LoggerFactory
@author: shadowshell
"""

import logging
import logging.config

from .logging_logger import LoggingLogger
from .logging_constants import LoggingConstants

class LoggerFactory:

    @staticmethod
    def init():
        logging.config.fileConfig(LoggingConstants.logging_conf_dir)

    @staticmethod
    def get_logger(name = 'root'):
        return LoggingLogger(logging.getLogger(name))
    
