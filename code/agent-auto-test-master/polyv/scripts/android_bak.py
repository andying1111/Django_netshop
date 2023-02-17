#!/usr/bin/evn python
# -*- coding: UTF-8 -*
import os
import platform
import re
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import aircv as ac
import cv2
import numpy
from PIL import Image

from polyv.common import ip_util
from polyv.common.data_format import DataFormat
from polyv.scripts.intelligent import ImageLocation

separator = '/' if 'Windows' in platform.system() else '\\'


def match_image(img_src, img_obj, confidence=0.8):
    """
    img_src=原始图像
    img_obj=待查找的图片
    """
    img_src = ac.imread(img_src)
    img_obj = ac.imread(img_obj)
    match_result = ac.find_template(img_src, img_obj, confidence)

    if match_result is not None:
        match_result['shape'] = (img_src.shape[1], img_src.shape[0])  # 0为高，1为宽

    return match_result


def calculate(image1, image2):
    image1 = cv2.cvtColor(numpy.asarray(image1), cv2.COLOR_RGB2BGR)
    image2 = cv2.cvtColor(numpy.asarray(image2), cv2.COLOR_RGB2BGR)
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


class AndroidAgent(object):
    result = DataFormat()
    INSTRUMENT = "adb shell am instrument -w -e class 'com.cvte.hotax.ExampleInstrumentedTest#step'"
    RUNNER = "com.cvte.hotax.test/android.support.test.runner.AndroidJUnitRunner"
    ACTION = "-e step-action"
    IMAGE = None
    DEVICE = None

    def __clicks(self, operation, param, index=-1):
        if index == -1:
            command = f"{self.INSTRUMENT} {self.ACTION}  Click {operation} \\\"{param}\\\" {self.RUNNER}"
        else:
            command = f"{self.INSTRUMENT} {self.ACTION}  Click {operation} \\\"{param}\\\" -e step-order {index} {self.RUNNER}"
        return self.execute(command)

    def __exist(self, operation, param, index=-1):
        if index == -1:
            command = f"{self.INSTRUMENT} {self.ACTION} AssertExist {operation} \\\"{param}\\\" {self.RUNNER}"
        else:
            command = f"{self.INSTRUMENT} {self.ACTION} AssertExist {operation} \\\"{param}\\\" -e step-order {index} {self.RUNNER}"
        return self.execute(command)

    def __get_texts(self, operation, param, index=-1):
        try:
            if index == -1:
                command = f"{self.INSTRUMENT} {self.ACTION}  getText {operation} \\\"{param}\\\" {self.RUNNER}"
            else:
                command = f"{self.INSTRUMENT,} {self.ACTION}  getText {operation} \\\"{param}\\\" -e step-order {index} {self.RUNNER}"
            p = self.cmd(command).stdout
            print(str(p))
            text = re.findall(r'元素文本：(.+?)\nIN', str(p))[0]
            return text
        except Exception as e:
            return 'get text exception:{}'.format(str(e))

    def __inputs(self, param, param_value, text, index=-1):
        if index == -1:
            command = f"{self.INSTRUMENT} {self.ACTION}  Input -e step-reText \\\"{text}\\\" {param} \\\"{param_value}\\\" {self.RUNNER}"
        else:
            command = f"{self.INSTRUMENT} {self.ACTION} Input -e step-reText \\\"{text}\\\" {param} \\\"{param_value}\\\" -e step-order {index} {self.RUNNER}"
        return self.execute(command)

    def take_screen_shot(self):
        """
        截图
        :return:
        """
        command = f"{self.INSTRUMENT} {self.ACTION}  takeScreenShot {self.RUNNER}"
        try:
            p = self.cmd(command).stdout
            print(str(p))
            path = re.findall(r'screenshot-SUCCESS=(.+?)\nIN', str(p))[0]
            return self.save_image(path)
        except Exception as e:
            return self.result.set(code=400, status=False, message='take screenshot exception:{}'.format(str(e)),
                                   data='{"remote":""}')

    def get_action_screen_shot(self):
        """
        UiObject每个操作会自动截图，这里可以获取最近一次操作的画面
        :return:
        """
        return self.save_image(self.IMAGE)

    def save_image(self, path):
        try:
            ip = ip_util.get_ip()
            image_name = os.path.basename(path).replace('.jpg', '')
            sd_path = path.replace(image_name + '.jpg', '')
            file = f"{os.getcwd()}{separator}image.temp"
            remote = f"http://{ip}:8081/api/common/image?image_id={image_name}"

            self.adb('pull {} {}'.format(path, file))
            src = '{}{}{}.jpg'.format(file, separator, image_name)
            dst = '{}{}{}.png'.format(file, separator, image_name)
            os.rename(src, dst)
            self.shell('rm -rf {}'.format(sd_path))
            return self.result.set(data=remote)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err), data='No screenshot file found')

    def execute(self, command):
        try:
            # 解决中文乱码问题
            result = self.cmd(command)
            if result.returncode == 0:
                print("[success]打印结果：:", result.stdout)
                self.IMAGE = re.findall(r'screenshot-SUCCESS=(.+?)\nIN', str(result.stdout))[0]
            else:
                print("[error]打印结果：:", result.stderr)
            if result.stdout.find("OK") != -1:
                return "OK"
        except Exception as err:
            print(err)
        return "FAIL"

    def cmd(self, command):
        """执行cmd命令"""
        print(command)
        return subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              encoding="utf-8", timeout=300)

    def adb(self, command):
        if self.DEVICE is None:
            return self.cmd('adb {}'.format(command)).stdout
        else:
            return self.cmd('adb -s {} {}'.format(self.DEVICE, command)).stdout

    def shell(self, command):
        if self.DEVICE is None:
            return self.cmd('adb shell {}'.format(command)).stdout
        else:
            return self.cmd('adb -s {} shell {}'.format(self.DEVICE, command)).stdout

    def set_device(self, device):
        """
        绑定设备,之后所有指令发送到该设备上
        :param device: 设备IP
        :return: json
        """

        self.DEVICE = None if (device == '' or device is None) else device
        self.INSTRUMENT = "adb -s {} shell am instrument -w -e class 'com.cvte.hotax" \
                          ".ExampleInstrumentedTest#step'".format(self.DEVICE) if self.DEVICE \
            else "adb shell am instrument -w -e class 'com.cvte.hotax.ExampleInstrumentedTest#step'"
        return self.result.set(message=f'绑定设备【{device}】——> success')

    def connect(self, device):
        """
        连接设备，并绑定设备,之后所有指令发送到该设备上
        :param device: 设备IP
        :return: json
        """
        self.DEVICE = None if (device == '' or device is None) else device
        try:
            p = self.cmd('adb connect ' + device).stdout
            if (p.find("connected") != -1) or ('.' not in device):
                self.INSTRUMENT = f"adb -s {self.DEVICE} shell am instrument -w -e class 'com.cvte.hotax.ExampleInstrumentedTest#step'"
                return self.result.set(message='连接并绑定设备——> success')
            else:
                return self.result.set(code=400, status=False, message='连接并绑定设备——> fail')
        except Exception as err:
            return self.result.set(code=401, status=False, message=f'发生未知异常！\n{str(err)}')

    def open(self, package, clear=False):
        """
        打开应用
        :param package:  应用包名称
        :param clear: 是否清除应用数据
        :return: json
        """
        try:
            command = f"{self.INSTRUMENT} {self.ACTION}  OpenApplication -e step-packageName {package}  -e step-clear {clear} {self.RUNNER}"
            rst = self.execute(command)
        except Exception as err:
            return self.result.set(405, False, message=f'unknown exception\n{str(err)}')
        if rst == "OK":
            return self.result.set(message=f'打开应用：{package}')
        return self.result.set(400, False, message=f'打开应用：{package}')

    def close(self, package):
        """
        强制关闭应用
        :param package: 应用包名称
        :return: json
        """
        self.shell(f'am force-stop {package}')
        return self.result.set(message=f'关闭APP：{package}')

    def click(self, tag, element, index=-1):
        """
        点击控件
        :param tag: 控件类型
        :param element: 控件元素
        :param index: 复数
        :return: json
        """
        rst = None
        try:
            if tag == 'package':
                rst = self.__clicks('-e step-elementPackage', param=element, index=index)
            elif tag == 'clazz':
                self.__clicks('-e step-elementClazz', param=element, index=index)
            elif tag == 'desc':
                rst = self.__clicks('-e step-elementDesc', param=element, index=index)
            elif tag == 'text':
                rst = self.__clicks('-e step-elementText', param=element, index=index)
            elif tag == 'id':
                rst = self.__clicks('-e step-elementId', param=element, index=index)
            elif tag == 'image':
                rst = self.click_element_by_image(element)
        except Exception as err:
            return self.result.set(code=405, status=False, message=f'请求发生错误\n{str(err)}')

        if rst == "OK":
            return self.result.set(message=f'点击元素：{element}' if (
                    tag != 'image') else f'点击元素：<img src="{ImageLocation.get_image(element)}" width="20%">')
        return self.result.set(code=400, status=False, message=f'点击元素失败：{element}' if (
                tag != 'image') else f'点击元素失败：<img src="{ImageLocation.get_image(element)}" width="20%">')

    def input(self, tag, element, index, value):
        """
        向指定控件输入文本
        :param value: 文本内容
        :param tag: 控件类型
        :param element: 控件元素
        :param index: 复数
        :return: json
        """
        rst = None
        try:
            if tag == 'package':
                rst = self.__inputs("-e step-elementPackage", param_value=element, text=value, index=index)
            elif tag == 'clazz':
                rst = self.__inputs("-e step-elementClazz ", param_value=element, text=value, index=index)
            elif tag == 'desc':
                rst = self.__inputs("-e step-elementTextDesc", param_value=element, text=value, index=index)
            elif tag == 'text':
                rst = self.__inputs("-e step-elementText", param_value=element, text=value, index=index)
            elif tag == 'id':
                rst = self.__inputs("-e step-elementId", param_value=element, text=value, index=index)
            elif tag == 'image':
                rst = self.click_element_by_image(element)
        except Exception as err:
            return self.result.set(code=405, status=False, message=str(err), data='请求发生错误')
        if rst == "OK":
            return self.result.set(data='in element \'{}（{}）\' input {} ——> success'.format(element, index, value))
        return self.result.set(code=400, status=False, message="input fail",
                               data='in element \'{}（{}）\' input {} ——> fail'.format(element, index, value))

    def get_text(self, tag, element, index):
        """
        获取文本
        :param tag: 控件类型
        :param element: 控件元素
        :param index: 复数
        :return: json
        """
        text = None
        try:
            if tag == 'package':
                text = self.__get_texts('-e step-elementPackage', param=element, index=index)
            elif tag == 'clazz':
                self.__get_texts('-e step-elementClazz', param=element, index=index)
            elif tag == 'desc':
                text = self.__get_texts('-e step-elementDesc', param=element, index=index)
            elif tag == 'text':
                text = self.__get_texts('-e step-elementText', param=element, index=index)
            elif tag == 'id':
                text = self.__get_texts('-e step-elementId', param=element, index=index)
            elif tag == 'image':
                text = ''  # todo
        except Exception as err:
            return self.result.set(code=405, status=False, message=str(err), data='请求发生错误')
        if text is None:
            return self.result.set(code=400, status=False, message="click fail",
                                   data='this element {' + element + '}[' + str(index) + '] fail')
        else:
            return self.result.set(message='this element {' + element + '}[' + str(index) + ']', data=text)

    def exist(self, tag, element, index=-1):
        """
        点击控件
        :param tag: 控件类型
        :param element: 控件元素
        :param index: 复数
        :return: json
        """
        rst = None
        try:
            if tag == 'package':
                rst = self.__exist('-e step-elementPackage', param=element, index=index)
            elif tag == 'clazz':
                rst = self.__exist('-e step-elementClazz', param=element, index=index)
            elif tag == 'desc':
                rst = self.__exist('-e step-elementDesc', param=element, index=index)
            elif tag == 'text':
                rst = self.__exist('-e step-elementText', param=element, index=index)
            elif tag == 'id':
                rst = self.__exist('-e step-elementId', param=element, index=index)
            elif tag == 'image':
                rst = self._exist_by_image(element)
        except Exception as err:
            return self.result.set(code=405, status=False, message=str(err), data='请求发生错误')

        if rst == "OK":
            return self.result.set(data='find the element {' + element + '}[' + str(index) + ']')
        return self.result.set(code=400, status=False, message="not found",
                               data='not found the element {' + element + '}[' + str(index) + '] fail')

    def android_screen_shot(self):
        tmp_file = f'{tempfile.gettempdir()}/{time.time()}.png'
        self.shell('screencap /sdcard/test.png')
        self.adb(f'pull /sdcard/test.png {tmp_file}')
        print(tmp_file)
        return tmp_file

    def _find_position_by_image(self, image, confidence=0.8):
        cap = self.android_screen_shot()
        position = match_image(cap, ImageLocation.get_image(image), confidence)
        if position is not None:
            return position['result']
        return None

    def _exist_by_image(self, image, confidence=0.8):
        return "OK" if self._find_position_by_image(image, confidence) is not None else "FAIL"

    def get_position_by_image(self, image, confidence=0.8):
        position = self._find_position_by_image(image, confidence)
        if position is not None:
            x, y = position
            return x, y
        return None

    def click_element_by_image(self, image, confidence=0.8):
        position = self._find_position_by_image(image, confidence)
        if position is not None:
            x, y = position
            self.click_position(x, y)
            return 'OK'
        return None

    def input_element_by_image(self, image, value, confidence=0.8):
        position = self._find_position_by_image(image, confidence)
        if position is not None:
            x, y = position
            self.click_position(x, y)
            self.input_by_sys(value)
            return 'OK'
        return None

    def click_position(self, x, y):
        self.shell(f'input tap {x} {y}')

    def input_by_sys(self, value):
        self.shell(f'input text {value}')

    def start_live_play_by_chrome(self, url):
        self.shell(f'am start -a android.intent.action.VIEW  -d {url}')

    def start_live_play_by_wechat(self, url):
        self.shell(f'am start -n com.tencent.mm')

    def classify_hist_with_split(self, image1, image2, size=(256, 256)):
        """图像对比，返回相似度"""
        try:
            if image1.startswith('http'):
                if 'image_id=' in image1:
                    directory = os.getcwd() + "/image.temp/"
                    image1 = directory + str(image1).split('image_id=')[1] + '.png'
                    image2 = directory + str(image2).split('image_id=')[1] + '.png'
                else:
                    image1 = urllib.request.urlretrieve(image1, filename='temp1.png')[0]
                    image2 = urllib.request.urlretrieve(image2, filename='temp2.png')[0]
            else:
                image1 = image1 if Path(image1).is_file() else ImageLocation.get_image(image1)
                image2 = image2 if Path(image2).is_file() else ImageLocation.get_image(image2)

            image1 = Image.open(image1)
            image2 = Image.open(image2)
            # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
            image1 = cv2.cvtColor(numpy.asarray(image1), cv2.COLOR_RGB2BGR)
            image2 = cv2.cvtColor(numpy.asarray(image2), cv2.COLOR_RGB2BGR)
            image1 = cv2.resize(image1, size)
            image2 = cv2.resize(image2, size)
            sub_image1 = cv2.split(image1)
            sub_image2 = cv2.split(image2)
            sub_data = 0
            for im1, im2 in zip(sub_image1, sub_image2):
                sub_data += calculate(im1, im2)
            sub_data = sub_data / 3
            print("相似度为：" + "%.2f%%" % (sub_data * 100))
            return self.result.set(data=float(sub_data * 100))
        except Exception as err:
            return self.result.set(code=405, status=False, message=f'请求发生错误\n{str(err)}')

    def swipe_direct(self, direct):
        command = f"{self.INSTRUMENT} {self.ACTION} Swipe -e step-direction {direct} {self.RUNNER}"
        return self.execute(command)

    def swipe_right(self):
        try:
            rst = self.swipe_direct("right")
        except Exception as err:
            return self.result.set(code=405, status=False, message=str(err), data='swipe fail')
        if rst == "OK":
            return self.result.set(data='swipe right')
        return self.result.set(400, False, data="swipe fail")

    def swipe_left(self):
        try:
            rst = self.swipe_direct("left")
        except Exception as err:
            return self.result.set(code=405, status=False, message=str(err), data='swipe fail')
        if rst == "OK":
            return self.result.set(data='swipe left')
        return self.result.set(400, False, data="swipe fail")

    def swipe_down(self):
        try:
            rst = self.swipe_direct("down")
        except Exception as err:
            return self.result.set(code=405, status=False, message=str(err), data='swipe fail')
        if rst == "OK":
            return self.result.set(data='swipe down')
        return self.result.set(400, False, data="swipe fail")

    def swipe_up(self):
        try:
            rst = self.swipe_direct("up")
        except Exception as err:
            return self.result.set(code=405, status=False, message=str(err), data='swipe fail')
        if rst == "OK":
            return self.result.set(data='swipe up')
        return self.result.set(400, False, data="swipe fail")


if __name__ == '__main__':
    agent = AndroidAgent()
    agent.connect('ABXL6R1712005127')
    # agent.open('com.android.chrome')
    # agent.click(tag='text', element='Document', index=1)
    # agent.start_live_play_by_chrome('http://47.115.22.63:8000/liveMobile?vid=2905472')
    # agent.start_live_play_by_wechat('http://47.115.22.63:8000/liveMobile?vid=2905472')
    # agent.click(tag='text', element='http://47.115.22.63:8000/liveMobile?vid=2905472', index=1)
    agent.click(tag='image', element='0a4c246a-6310-4a74-b08c-153b5f974300')
