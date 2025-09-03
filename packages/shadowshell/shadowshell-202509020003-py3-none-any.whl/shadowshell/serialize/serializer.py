#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serializer

@author: shadowshell
"""

from shadowshell.logging import LoggerFactory

class Serializer:

    def __init__(self):
        self.logger = LoggerFactory().get_logger()
 
    def serialize(self, object):
        self.logger.warn("No serialize")
        return None

    def deserialize(self, content):
        self.logger.warn("No deserialize")
        return None
