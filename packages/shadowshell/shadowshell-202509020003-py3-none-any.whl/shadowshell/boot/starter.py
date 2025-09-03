#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

from shadowshell.config import Configurator
from shadowshell.monitor import function_monitor
from shadowshell.logging import LoggingConstants, LoggerFactory
from shadowshell.serialize import SerializerFactory
from shadowshell.file import FileUtil

class_mame = "Starter"

class Starter:
    
    # @function_monitor(class_mame)
    def __init__(self):
        self.work_dir = self.get_work_dir()
        self.__init_logging()
        self.__init_configs()

    # @function_monitor(class_mame)
    def __init_logging(self):
        LoggingConstants.logging_conf_dir = self.get_logging_config_file_path()
        LoggerFactory.init()
    
    # @function_monitor(class_mame)
    def get_logging_config_file_path(self):
        return f'{self.work_dir}/config/logging.conf'

    # @function_monitor(class_mame)
    def __init_configs(self):
        config_file_path = self.get_config_file_path()
        if config_file_path is not None: 
            self.configurator = Configurator(config_file_path)

    @function_monitor(class_mame)
    def get_work_dir(self):
        """获取工作目录"""
        return '.'
    @function_monitor(class_mame)
    def get_config_file_path(self):
        """ 获取配置文件路径"""
        return f'{self.work_dir}/config/app.ini'
    
    # @function_monitor(class_mame)
    def get_file_content(self, file_name):
        return FileUtil.get_all(file_name)
    
    # @function_monitor(class_mame)
    def serialize(self, object):
        return SerializerFactory.get_instance().serialize(object)
    
    # @function_monitor(class_mame)
    def deserialize(self, text):
        return SerializerFactory.get_instance().deserialize(text)

    # @function_monitor(class_mame)
    def get_logger(self, logger_name = 'root'):
        return LoggerFactory.get_logger(logger_name)
    
    