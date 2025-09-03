#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serializer

@author: shadowshell
"""

import json
from shadowshell.logging import LoggerFactory
from .serializer import Serializer
from .serializable import Serializable

class SerializerJson(Serializer):

    def __init__(self):
        self.logger = LoggerFactory.get_logger()
        pass
     
    def serialize(self, object, encoding = 'utf-8'):
        json_text = None
        if isinstance(object, Serializable):
            json_text = object.serialize()
        else:
            json_text = json.dumps(
                object
                , indent = 4
                , ensure_ascii = False
                , sort_keys = True
            ).encode(encoding)

        self.logger.debug(f"Serialized json text: {json_text}.")
        
        return json_text

    def deserialize(self, text):
        self.logger.debug(f"Deserialized json text: {text}.")
        object = json.loads(text)
        return object

