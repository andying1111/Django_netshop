import os
import platform
import subprocess
import time

import wget
from PIL import Image


class FileUtils:

    def __init__(self):
        self.separator = '/'

    def get_separator(self):
        if 'Windows' in platform.system():
            self.separator = '\\'
        else:
            pass
        return self.separator

    def find_path(self, file):
        o_path = os.getcwd()
        separator = self.get_separator()
        stirs = o_path.split(separator)
        while len(stirs) > 0:
            spate = separator.join(stirs) + separator + file
            lend = len(stirs)
            if os.path.exists(spate):
                return spate
            stirs.remove(stirs[lend - 1])
        return ""

    def get_root_path(self):
        return os.path.dirname(os.path.abspath(__file__))

    def download_web_driver(self):
        # 网络地址
        if 'Windows' in platform.system():
            file_url = 'http://10.21.41.52:8080/server/hotax/report/chromedriver.exe'
        else:
            file_url = 'http://10.21.41.52:8080/server/hotax/report/chromedriver'
        wget.download(file_url, out='')
        time.sleep(1)
        cmd = ['chmod', "777", "chromedriver—agent"]
        res = subprocess.run(cmd, universal_newlines=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=False)
        print(res.returncode, res.stdout, res.stderr)
        pass

    def remove_files(self, breday, path):
        """
        删除N天以前的文件
        :param breday:  N 天之前
        :param path:    路径
        :return:
        """
        bretime = time.time() - 3600 * 24 * breday
        # 文件最近修改时间 ：os.path.getmtime(file)
        # 文件创建时间：os.path.getctime(file)
        # 文件最近访问时间：os.path.getatime(file)
        for file in os.listdir(path):
            filename = path + os.sep + file
            if os.path.getmtime(filename) < bretime:
                try:
                    if os.path.isfile(filename):
                        os.remove(filename)
                    elif os.path.isdir(filename):
                        os.removedirs(filename)
                    else:
                        os.remove(filename)
                    print("%s remove success." % filename)
                except Exception as error:
                    print(error)
                    print("%s remove failed." % filename)


class ImageCompare(object):
    '''
    本类实现了对两张图片通过像素比对的算法，获取文件的像素个数大小
    然后使用循环的方式将两张图片的所有项目进行一一对比，
    并计算比对结果的相似度的百分比
    '''

    def make_regalur_image(self, img, size=(256, 256)):
        # 将图片尺寸强制重置为指定的size大小
        # 然后再将其转换成RGB值
        return img.resize(size).convert('RGB')

    def split_image(self, img, part_size=(64, 64)):
        # 将图片按给定大小切分
        w, h = img.size
        pw, ph = part_size
        assert w % pw == h % ph == 0
        return [img.crop((i, j, i + pw, j + ph)).copy() \
                for i in range(0, w, pw) for j in range(0, h, ph)]

    def hist_similar(self, lh, rh):
        # 统计切分后每部分图片的相似度频率曲线
        assert len(lh) == len(rh)
        return sum(1 - (0 if l == r else float(abs(l - r)) / max(l, r)) \
                   for l, r in zip(lh, rh)) / len(lh)

    def calc_similar(self, li, ri):
        # 计算两张图片的相似度
        return sum(self.hist_similar(l.histogram(), r.histogram()) \
                   for l, r in zip(self.split_image(li), self.split_image(ri))) / 16.0

    def calc_similar_by_path(self, lf, rf):
        li, ri = self.make_regalur_image(Image.open(lf)), \
                 self.make_regalur_image(Image.open(rf))
        return self.calc_similar(li, ri)

if __name__ == '__main__':
    f = FileUtils()
    f.remove_files(7, '/Users/cvter/Downloads/BaiduTextApi-master/test/img/')
