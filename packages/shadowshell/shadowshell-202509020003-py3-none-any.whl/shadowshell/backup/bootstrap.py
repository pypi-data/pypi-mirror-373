#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# import requests
from datetime import datetime
from shadowshell.logging import LoggerFactory

logger = LoggerFactory().get_logger()

"""
ShadowShell

@author: shadowshell
"""
class ShadowShell:

    def __init__(self):
        self.logger = LoggerFactory().get_logger()
        pass

    def hello(self):
        print("Hi, i am shadow shell." )
        current_time = datetime.now()
        formatted_current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print("Now is " + formatted_current_time)

    def test(self, func, **args):
        try:
            self.logger.debug('-->> Ready')
            func(**args)            
            self. logger.debug('-->> Do something')
        except Exception as e:
            self.logger.error(e)
        except:
            self.logger.error(sys.exc_info()[0])
        finally:
            self.logger.debug('-->> Done')
        return
    
    # def request(self):
    #     print(requests.get("https://wwww.baidu.com"))

import sys

class TestTemplate:

    def __init__(self):
        self.logger = LoggerFactory().get_logger()
        return

    def test(self):

        try:
            self.logger.debug('-->> Ready')
            
            self.test0()

            self.logger.debug('-->> Do something')

        except Exception as e:
            self.logger.error(e)
        except:
            self.logger.error(sys.exc_info()[0])
        finally:
            self.logger.debug('-->> Done')
            return

    def test0(self):
        self.logger.debug('Nothing')
        return
    
def testserver():
    os.system("ping shadowshell.xyz")
    
def cnnserver():
    os.system("ssh admin@shadowshell.xyz")

def hello(**args):
    logger.info(f"Hello {args}")

def shadowshell(**args):
    logger.info(f"shadow shell : {args}")

def invoke_with_tmpl(func, **args):
    try:
        logger.debug('-->> Ready')

        func(**args)
        
        logger.debug('-->> Do something')
    except Exception as e:
        logger.error(e)
    except:
        logger.error(sys.exc_info()[0])
    finally:
        logger.debug('-->> Done')
    return

if __name__ == "__main__":
    #ShadowShell().test()
    invoke_with_tmpl(shadowshell)
    invoke_with_tmpl(shadowshell, a='1')
    invoke_with_tmpl(shadowshell, a='1', b='2')
    invoke_with_tmpl(hello, a='shell', b='shadow')
