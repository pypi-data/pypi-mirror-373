# coding:utf-8
# -*- coding:utf-8 -*-
# @time: 2023/9/21 11:07
# @Author: erazhan
# @File: re_utils.py

# ----------------------------------------------------------------------------------------------------------------------
import re

def clean_illegal_character(text, illegal_flag = 1):
    '''清洗文本中的非法字符，都是不常见的不可显示字符，例如退格，响铃等
    1、illegal_flag = 1:
    匹配以下 ASCII 控制字符：​
    \000-\010：ASCII 0 到 8
    \013-\014：ASCII 11 到 12
    \016-\037：ASCII 14 到 31​
    注意，ASCII 9（水平制表符）、10（换行符）和 13（回车符）未被包含在内。
    2、illegal_flag = 2:

    3、illegal_flag = 3:
    匹配以下 ASCII 控制字符：​
    \x00-\x1F：ASCII 0 到 31
    \x7F：ASCII 127（DEL）​
    这意味着它会移除所有 ASCII 控制字符，包括换行符、回车符和制表符。
    '''
    try:
        if illegal_flag == 1:
            ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
            text = ILLEGAL_CHARACTERS_RE.sub(r'', text)
        elif illegal_flag == 2:
            text = text.encode("utf-8").decode("utf-8-sig")
        elif illegal_flag == 3:
            text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        else:
            text = text
    except:
        text = text
    return text

def extract_text_between_strings(text, start_str, end_str, show_exception = False):
    pattern = re.escape(start_str) + r"(.*?)" + re.escape(end_str)
    # pattern = "(?<=%s).*(?=%s)" % (start_str, end_str) # 找到最大范围的
    try:
        res = re.findall(pattern, text)
    except Exception as e:
        if show_exception:
            print("函数extract_text_between_strings报错:", e)
        res = []
    return res

def extract_text_after_string(text, start_str, show_exception = False):
    pattern = re.escape(start_str) + r"(.*)"
    try:
        res = re.findall(pattern, text)
    except Exception as e:
        if show_exception:
            print("函数extract_text_after_string报错:", e)
        res = []
    return res

if __name__ == "__main__":

    text = "./ic15_data/recognition_train/﻿word_1.png"
    data = {"text":text}
    print(data)
    data["new_text"] = clean_illegal_character(text)
    print(data)

    nn_text = text.encode("utf-8").decode("utf-8-sig")
    print(nn_text)

    text = """[11.11.1.111] - - [2023-09-04 11:15:06] "[POST /baichuan HTTP/1.1]" [200] [4063] [0.000495]"""
    start_str = "["
    end_str = "]"

    print(text)
    res = extract_text_between_strings(text, start_str,end_str,show_exception=True)
    print(res)

    text = "测试[[结果"
    start_str = "[["
    res = extract_text_after_string(text, start_str, show_exception=True)
    print(res)
