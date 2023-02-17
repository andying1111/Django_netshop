"""
@DESC:图片处理工具
@TAGS:["图片对比","图片识别坐标","图片提取文字"]
@AUTHOR:BobbyLi
@time: 2022/06/13 
"""
import urllib
from functools import reduce
from io import BytesIO

import cv2
import numpy as np
import requests
from PIL.Image import Resampling
import urllib.request

from polyv.common.data_format import DataFormat


def _get_image_real_path(image):
    if image.startswith("http"):
        image = urllib.request.urlretrieve(image, filename='temp1.png')[0]
    return cv2.imdecode(np.fromfile(image, dtype=np.uint8), -1)


def _get_image_real_path2(image):
    from PIL import Image
    return get_image_by_url(image) if image.startswith("http") else Image.open(image)


def compare(pic1, pic2):
    try:
        image1 = _get_image_real_path(pic1)
        image2 = _get_image_real_path(pic2)

        diff1 = get_the_average_pixel_of_each_row(image1)
        value1 = get_calculate_the_variance(diff1)
        print('图1-方差值:', value1)

        diff11 = get_the_average_pixel_of_each_row(image2)
        value2 = get_calculate_the_variance(diff11)
        print('图2-方差值:', value2)
        max_value = max(value1, value2)
        ss1 = get_calculate_the_variance(diff1)
        ss2 = get_calculate_the_variance(diff11)
        difference = abs(ss1 - ss2)

        print("两张照片的方差为：%s" % difference)
        print(f'差距百分比：{difference / max_value}')
        similar = (1 - difference / max_value) * 100
        print(f"两种图片的相似度：{similar}")
        return DataFormat().set(data=similar)
    except Exception as err:
        return DataFormat().set(code=405, status=False, message=f'请求发生错误\n{str(err)}')


# 计算方差
def get_calculate_the_variance(ls):
    # 计算平均值
    avg = sum(ls) / len(ls)
    # 定义方差变量ss，初值为0
    ss = 0
    # 计算方差
    for l in ls:
        ss += (l - avg) * (l - avg) / len(ls)
    # 返回方差
    return ss


# 获取每行像素平均值
def get_the_average_pixel_of_each_row(img):
    # 定义边长
    side_length = 30
    # 缩放图像
    img = cv2.resize(img, (side_length, side_length), interpolation=cv2.INTER_CUBIC)
    # 灰度处理
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # avg_list列表保存每行像素平均值
    avg_list = []
    # 计算每行均值，保存到avg_list列表
    for i in range(side_length):
        avg = sum(gray[i]) / len(gray[i])
        avg_list.append(avg)
    # avg_list
    return avg_list


def get_image_by_url(file_image_url):
    from PIL import Image
    html = requests.get(file_image_url, verify=False)
    image = Image.open(BytesIO(html.content))
    return image


# 计算Hash
def p_hash(img):
    img = img.resize((8, 8), Resampling.LANCZOS).convert('L')
    avg = reduce(lambda x, y: x + y, img.getdata()) / 64.
    return reduce(
        lambda x, y: x | (y[1] << y[0]),
        enumerate(map(lambda i: 0 if i < avg else 1, img.getdata())),
        0
    )


# 计算汉明距离
def hamming_distance(obj1, obj2):
    return bin(obj1 ^ obj2).count('1')


# 计算图片相似度
def is_img_similar(image_1, image_2):
    try:
        image1 = _get_image_real_path2(image_1)
        image2 = _get_image_real_path2(image_2)
        return DataFormat().set(data=True if hamming_distance(p_hash(image1), p_hash(image2)) <= 5 else False)
    except Exception as err:
        return DataFormat().set(code=405, status=False, message=f'请求发生错误\n{str(err)}')


if __name__ == '__main__':
    img1 = r'C:\workspace\develop\python\Agent\agent-auto-test\image.temp\1111.png'
    img2 = r'C:\workspace\develop\python\Agent\agent-auto-test\image.temp\2222.png'
    compare(img1, img2)
    print('----------------------------------------------------')
    print(is_img_similar(img1, img2).data)
