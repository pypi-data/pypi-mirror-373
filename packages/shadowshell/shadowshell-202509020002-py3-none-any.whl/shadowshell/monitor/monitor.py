#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

import sys
import time
import inspect
from shadowshell.logging import LoggerFactory

def callback(request, response):
    logger = LoggerFactory.get_logger()  
    logger.info(f"[CALLBACK][Request]{__format_request(request)}[Response]{__format_response(response)}")

def performance_monitor(class_name = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            response = None
            is_successed = True
            try:
                response = func(*args, **kwargs)
            except:
                LoggerFactory.get_logger().error(sys.exc_info()[0])
                is_successed = False
                raise
            finally:
                cost = time.perf_counter() - start
                # log
                __record_digest_log("PERFORMANCE_MONITOR", class_name, func.__name__, cost, is_successed)
                return response
        return wrapper
    return decorator

def function_monitor(class_name = None, serialize = None, callbacks = None):
    logger = LoggerFactory.get_logger()
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            response = None
            is_successed = True
            try:
                response = func(*args, **kwargs)    
            except Exception as e:
                logger.error(e)
                is_successed = False
                raise
            except:
                logger.error(sys.exc_info()[0])
                is_successed = False
                raise
            finally:
                cost = time.perf_counter() - start
                request = args
                if inspect.ismethod(func):
                    request = args[1:]
                # log
                __record_digest_log("FUNCTION_MONITOR", class_name, func.__name__, cost, is_successed)
                __record_detail_log("FUNCTION_MONITOR", class_name, func.__name__, cost, is_successed, request, response, serialize)
                 # callback
                if callbacks is not None:
                    for callback in callbacks:
                        try:
                            callback(args, response)
                        finally:
                            logger.error(sys.exc_info()[0])  
                        
                return response
        return wrapper
    return decorator

def __get_service_name(class_name, func_name):
    service_name = func_name
    if class_name is not None:
        service_name = class_name + "." + func_name
    return service_name

def __format_request(request, serialize = None):
   if serialize is not None:
       request = serialize(request)
   return request

def __format_response(response, serialize = None):
   if serialize is not None:
       response = serialize(response)
   return response
def __record_digest_log(monitor_name, class_name, func_name, cost, is_successed):
    logger = LoggerFactory.get_logger('functionMonitorDigestLogger')
    logger.info(f'[{monitor_name}][DIGEST_LOG][{__get_service_name(class_name, func_name)}]successed={is_successed}, cost:{cost:.6f}s.')

def __record_detail_log(monitor_name, class_name, func_name, cost, is_successed, request, response, serialize = None):
    logger = LoggerFactory.get_logger()
    logger.info(f'[{monitor_name}][DETAIL_LOG][{__get_service_name(class_name, func_name)}][{is_successed}][{cost:.6f}][Request]{__format_request(request, serialize)}[Response]{__format_response(response, serialize)}')
