#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@Author  :  Pin
@Date    :  29/12/2021 09:49
@Desc    :
"""
import os
import os.path
import sys

from settings import ROOT_PATH

root_path = os.getcwd() + os.sep
WIN = sys.platform.startswith('win')
if WIN:
    exe_path = os.path.join(ROOT_PATH, "lib", "pngquant.exe")
else:
    exe_path = os.path.join(ROOT_PATH, "lib", "pngquant")


def compress_picture(path):
    common = exe_path + " -f --quality 10 --ext .png --speed 1 " + path
    print("*" * 10 + "\n" + path)
    os.system(common)


if __name__ == '__main__':
    print(exe_path)