#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2025/9/3 10:23
# @Author: zhanjiyuan
# @File: decorator_utils.py
# ----------------------------------------------------------------------------------------------------------------------
import os
import time
from functools import wraps

def execute_time(enable=True):
    def decorator(func):
        @wraps(func) # 保留原函数的__name__，__doc__, __module__等信息
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            r = func(*args, **kwargs) # 执行原函数
            end = time.perf_counter()
            if enable:
                print(f"执行{func.__name__}函数耗时:{end-start:.4f}")
                # logging.info('{}.{} 耗时: {} 秒'.format(func.__module__, func.__name__, end - start))
            return r
        return wrapper
    return decorator

@execute_time(enable=True)
def check():
    """doc文档"""
    print("你好")
    time.sleep(2)
    print("结束")

if __name__ == "__main__":
    print(os.path.basename(__file__))
    check()
    print(check.__name__)
    print(check.__doc__)
