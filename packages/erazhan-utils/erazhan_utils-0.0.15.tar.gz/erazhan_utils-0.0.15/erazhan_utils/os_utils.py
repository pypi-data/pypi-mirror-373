# -*- coding = utf-8 -*-
# @time: 2022/2/21 10:52 上午
# @Author: erazhan
# @File: os_utils.py

# ----------------------------------------------------------------------------------------------------------------------
import os
import shutil

def test_os__path__dirname():
    # 得到当前文件的绝对路径
    print(os.path.dirname(os.path.abspath(__file__)))


def test_os__getcwd():
    # 获取当前路径
    ans = os.getcwd()
    print(ans)


def judge_file_or_dir(path_name):
    """判断路径是文件file还是文件夹dir，如果路径不存在或其它类型，则返回other"""

    if os.path.isfile(path_name):
        path_type = "file"
    elif os.path.isdir(path_name):
        path_type = "dir"
    else:
        path_type = "other"

    return path_type


def delete_file_or_dir(path_name, del_type="other"):
    """删除文件或者文件夹，取值为file或者dir"""

    if os.path.exists(path_name):
        del_type = judge_file_or_dir(path_name)
    print(f"del_type:{del_type}")
    if del_type == "file":
        os.remove(path_name)
    elif del_type == "dir":
        shutil.rmtree(path_name)
    else:
        print(f"path_name {path_name} is not exists")


def check_path(path_name):
    """检查文件夹(自动定位到最底层文件夹)是否存在，如果不存在则创建文件夹"""
    if os.path.dirname(path_name):
        if not os.path.exists(os.path.dirname(path_name)):
            os.makedirs(os.path.dirname(path_name))

if __name__ == "__main__":
    # path_name = "test.py"
    path_name = "test_ks"
    # os.makedirs(path_name,exist_ok=True)
    # delete_file_or_dir(path_name)
    path_name = os.path.join("/home/path/cur","test")
    print(path_name)
    res = os.path.dirname(path_name)
    print(res)
