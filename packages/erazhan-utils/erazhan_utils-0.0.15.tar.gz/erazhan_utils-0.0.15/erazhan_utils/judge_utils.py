# coding:utf-8
# -*- coding:utf-8 -*-
# @time: 2023/8/30 17:54
# @Author: erazhan
# @File: judge_utils.py

# ----------------------------------------------------------------------------------------------------------------------
from .constants import SUFFIX_TYPE_DICT
import unicodedata
import math
import numpy as np

def judge_not(entity, record):
    """保留原名称，兼容老版本"""
    return judge_negative_entity(entity, record)


def judge_negative_entity(entity, record):
    """判断entity和否定词的组合是否包含在原句子中，用于检查NER是否仅识别到不加否定前缀或后缀的entity。
    比如：entity='没有发烧'，NER如果仅识别到'发烧'，则可通过此函数粗略判断到识别内容不全，
    """
    neg_words = ["没有", "没", "无", "不", "不是"]
    re_neg_words = ["没有", "没", "无"]
    # 否定词在前
    flag = any(nw + entity in record for nw in neg_words)
    # 否定词在后
    re_flag = any(entity + rnw in record for rnw in re_neg_words)
    return flag or re_flag


def judge_suffix(text, suffix_list):
    """判断文本是否包含列表中的后缀，如果包含后缀返回纯的文件名和后缀名称"""
    return any(text.strip().endswith(suffix) for suffix in suffix_list)


def split_name_and_suffix(text, suffix_list):
    """将文本中的后缀名分离成名称+后缀，比如'123.jpg' -> '123'+'.jpg'"""
    text = text.strip()
    hit_name = None
    hit_suffix = None
    for suffix in suffix_list:
        if text.endswith(suffix):
            hit_name = text.split(suffix)[0]
            hit_suffix = suffix
            break
    return hit_name, hit_suffix


def judge_suffix_type(text, suffix_type_dict = SUFFIX_TYPE_DICT):
    """判断文本字符串的后缀类型，适用于多种后缀类型文件的判断，默认采用SUFFIX_TYPE_DICT"""
    text = text.strip()
    for suffix_type, suffix_list in suffix_type_dict.items():
        if judge_suffix(text,suffix_list):
            return suffix_type
    return "文字"

def split_hit_prefix_or_suffix(text, hit_candi_list, hit_type="prefix"):
    """找出文本中是否命中候选集中的前缀/后缀，如果命中则返回相应的前缀/后缀，以及剩下的文本，是split_name_and_suffix的进阶版"""
    text = text.strip()

    hit_prefix_suffix = ""
    hit_result = ""

    for hit_candi in hit_candi_list:
        if hit_type == "prefix" and text.startswith(hit_candi):
            hit_result = text.split(hit_candi)[1]
            hit_prefix_suffix = hit_candi
            break
        elif hit_type=="suffix" and text.endswith(hit_candi):
            hit_result = text.split(hit_candi)[0]
            hit_prefix_suffix = hit_candi
            break
        else:
            pass

    return hit_result, hit_prefix_suffix

def is_chinese(char,version="v2"):
    if version == "v1":
        return '\u4e00' <= char <= '\u9fff'
    elif version == "v2":
        cp = ord(char)
        return (
        0x3400 <= cp <= 0x4DBF or   # CJK 扩展 A
        0x4E00 <= cp <= 0x9FFF or   # CJK 基本汉字
        0x20000 <= cp <= 0x2A6DF or # CJK 扩展 B
        0x2A700 <= cp <= 0x2B73F or # CJK 扩展 C
        0x2B740 <= cp <= 0x2B81F or # CJK 扩展 D
        0x2B820 <= cp <= 0x2CEAF or # CJK 扩展 E
        0x2CEB0 <= cp <= 0x2EBEF or # CJK 扩展 F
        0x30000 <= cp <= 0x3134F or # CJK 扩展 G
        0x2F800 <= cp <= 0x2FA1F    # CJK 兼容汉字补充
    )
    else:
        raise ValueError(f"version {version} error")


def is_pinyin_letter(pinyin_char, hit_categories=None):
    """
    :param pinyin_char:
    :param hit_categories: List，'Lu'是大写字母，'Ll'是小写字母，包括加了声调的，比如："ǎ"/"à"，'Lt'是标题字母，比如"ǅ"。
    :return:
    判断单个字符是否是拼音字母，包括英文字母和声调等情况
    """
    if hit_categories is None:
        hit_categories = ['Lu','Ll']

    char_name = unicodedata.name(pinyin_char)
    char_category = unicodedata.category(pinyin_char)
    if "LATIN" in char_name and char_category in hit_categories:
        return True
    return False

def judge_nan(data):
    """
    :param data: 单条数据，文本数据或者数字类数据
    :return: True/False，用于判断数据是否为NaN
    """

    if type(data) not in [float, np.float64, np.float32]:
        return False

    if math.isnan(data) or np.isnan(data):
        return True

    return False

if __name__ == "__main__":

    text = "123.jpg"
    suffix_list = [".jpg",".png"]

    res = judge_suffix(text,suffix_list=suffix_list)
    print(res)

    hit_name, hit_suffix = split_name_and_suffix(text,suffix_list)
    print(hit_name)
    print(hit_suffix)

    text_type = judge_suffix_type(text)
    print(text_type)

    ent = "发烧"
    raw_text = "发烧的没有"
    a = judge_negative_entity(ent, raw_text)

    print(a)

    char = "㿠"
    res = is_chinese(char, version="v1")
    print(res)

    res = is_chinese(char,version="v2")
    print(res)

    char = "ǎ"
    res = is_pinyin_letter(char)
    print(res)
