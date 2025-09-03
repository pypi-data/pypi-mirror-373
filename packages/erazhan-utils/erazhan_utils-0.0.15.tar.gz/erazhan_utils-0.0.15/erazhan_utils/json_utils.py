# -*- coding = utf-8 -*-
# @time: 2022/2/21 10:55 上午
# @Author: erazhan
# @File: json_utils.py

# ----------------------------------------------------------------------------------------------------------------------
import json

def save_txt_file(filename,entity_list):

    with open(filename,encoding='utf-8',mode ='w') as f:
        for one_entity in entity_list:
            f.write(one_entity + '\n')

def read_txt_file(txt_filename):

    '''
    :param txt_filename:必须是txt文件并且每一行是一个实体
    :return: 实体列表
    注意这里不去重
    '''

    entity_list = []
    with open(txt_filename,encoding = 'utf-8',mode = 'r') as f:
        for line in f.readlines():
            entity_list.append(line.strip())

    return entity_list

def save_json_file(filename,entities,mode = "indent"):

    # 需要将mode改成w才行
    # mode = 'w'正常，如果mode = 'a'那么用read_json_file读数据时会报错,因为此时写数据是接着之前的数据写，不会覆盖原有数据
    with open(filename,encoding='utf-8',mode = 'w') as f:

        if mode == "indent":
            f.write(json.dumps(entities,indent = 4,ensure_ascii=False, sort_keys = False, separators=(',', ':') ))
        else:
            f.write(json.dumps(entities, ensure_ascii=False))
        # f.write(json.dumps(entities,indent = 4,ensure_ascii=False, sort_keys = False, separators=(',',':') ))

def read_json_file(filename):

    with open(filename,'r',encoding = 'utf-8') as f:
        data = json.loads(f.read())

    return data

def trans2json(data):
    return json.dumps(data,indent = 4,ensure_ascii=False, sort_keys = False, separators=(',', ':'))

def save_jsonl_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        for item in data:
            json_line = json.dumps(item, ensure_ascii=False)
            # 增加\n是为了换行，读取时也会一并读取\n，再用json.loads时，会忽略掉\n
            f.write(json_line + "\n")

def read_jsonl_file(filename):
    data_list = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            one_data = json.loads(line)
            data_list.append(one_data)
    return data_list

if __name__ == "__main__":
    data_list = [{"text":"read"},{"text":"save"}]
    savename = "./test.json"
    save_jsonl_file(savename, data_list)
    dd = read_jsonl_file(savename)
    print(trans2json(dd))