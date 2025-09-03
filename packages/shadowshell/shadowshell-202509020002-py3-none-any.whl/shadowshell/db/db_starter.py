#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

from shadowshell.boot import Starter
from sqlalchemy.orm import DeclarativeBase

class ModelBase(DeclarativeBase):
    pass

from sqlalchemy import create_engine

class DbStarter(Starter):

    def __init__(self):
        super().__init__()
        self.config_group_datasource = 'datasource'
        self.configurator.get(self.config_group_datasource, 'api_key')
        self.username = self.configurator.get(self.config_group_datasource, "username")
        self.password = self.configurator.get(self.config_group_datasource, "password")
        self.url = self.configurator.get(self.config_group_datasource, "url")

        sqlalchemy_url = f'mysql+pymysql://{self.username}:{self.password}@{self.url}'
        self.engine = create_engine(sqlalchemy_url, echo=True)


