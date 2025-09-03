#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base_test import BaseTest
from src.shadowshell.serialize.serializable import Serializable
from src.shadowshell.serialize.serializer_factory import SerializerFactory

class Item(Serializable):

    def __init__(self, id, name = None):
        self.id = id
        self.name = name

print(SerializerFactory.get_instance().serialize(Item("shadowshell", "ShadowShell")))