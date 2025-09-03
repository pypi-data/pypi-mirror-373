#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

from pathlib import Path
from shadowshell.logging import LoggerFactory
from shadowshell.monitor import function_monitor

class FileUtil:

    __logger = LoggerFactory.get_logger()

    @staticmethod
    def get_all(file_path, mode = 'r', encoding = 'utf-8'):
        path = Path(file_path)
        if path.is_file() == False:
            FileUtil.__logger.warn(f'File is not exists: {file_path}')
            return None
        with open(file_path, mode, encoding = encoding) as f:
            content = f.read()
        FileUtil.__logger.debug(f'[{file_path}][All content]{content}')
        return content
    
   