"""
@Author  :  Bobby
@Date    :  26/01/2022 10:42
@Desc    :
"""
import base64
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import pyautogui as auto
import pyperclip
import pytesseract
import requests
from PIL import Image
from fastapi import Response
from pynput.mouse import Controller

from polyv.common import ip_util
from polyv.common.PolyvOcr import CallingOCR
from polyv.common.data_format import DataFormat
from polyv.config import Config
from polyv.scripts.keyboard import KeyBroad
from polyv.scripts.web_driver import WebDriverAgent
from settings import IMAGE_SERVER_URL, ROOT_PATH

df = DataFormat()
cp = os.path.abspath(os.path.dirname(__file__))
tmp_path = os.path.dirname(os.path.dirname(cp))
mouse = Controller()
key_tool = KeyBroad()

ocr = CallingOCR()


def urllib_parse(url):
    """将URL转义恢复"""
    return urllib.parse.unquote(url)


def download_image(image):
    """下载图片元素"""
    url = urllib_parse(image)
    image_file_name = url.split('=')[1].split('&')[0]
    print(image_file_name)
    image_file = os.path.join(tempfile.gettempdir(), 'temp.png')

    content = requests.get(url).content
    with open(image_file, 'wb') as f:
        f.write(content)
    return image_file, url


def get_position_by_image(image, index):
    """从电脑当前屏幕识别要查找的元素，并返回识别坐标结果"""
    try:
        image_file, url = download_image(image)
        if index > 0:
            location = list(auto.locateAllOnScreen(image=image_file))
            if index >= len(location):
                location = location[len(location) - 1]
            print('-------')
        else:
            location = auto.locateOnScreen(image=image_file)
        x, y = auto.center(location)
        return x, y
    except Exception as err:
        print(err)
        return None


def error(e, image=None, t=True, data=None):
    return df.set(code=400, status=False,
                  message=f"操作失败！   {e}\n没有有找到匹配对象： {image}", data=data) \
        if t else df.set(code=400, status=False, message=f"操作失败！   {e}", data=data)


def fail(message=None, status=False, data=None):
    return df.set(code=400, status=status, message=message, data=data)


def info(message=None, data=None):
    return df.set(message=message, data=data)


def cmd(command):
    """执行cmd命令"""
    print(command)
    return subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding="utf-8", timeout=300)


class ImageLocation(object):
    """
    Image location
    """
    CHS = 'chi_sim'  # 中文字库
    ENG = 'eng'  # 英文字库

    @staticmethod
    def get_image(locator_id: str):
        """
        从服务器上获取图片
        """
        url = requests.get(IMAGE_SERVER_URL + 'image/manage/{}/source/'.format(locator_id)).json().get('url')
        image_file = os.path.join(tempfile.gettempdir(), url.split('/')[-1])  # tempfile.gettempdir() 用于返回保存临时文件的文件夹路径
        if os.path.exists(image_file):
            print("{}已经存在".format(image_file))
        else:
            print("{}不存在".format(image_file))
            content = requests.get(url).content
            with open(image_file, 'wb') as f:
                f.write(content)
        return image_file

    @staticmethod
    def click(image, index=0):
        """
        通过图片定位并点击
        :param image: 图片文件
        :param index: 屏幕中多个相同图片，用index来指定
        :return: None
        """
        try:
            x, y = get_position_by_image(image, index)
            auto.click(x, y)
            auto.moveTo(x - 60, y - 60, duration=0.25)
            return info(message='通过图片定位并点击')
        except Exception as e:
            return error(e, urllib_parse(image))

    @staticmethod
    def right_click(image):
        """
        通过图片定位并右击
        :param image:图片文件
        :return:
        """
        try:
            auto.rightClick(ImageLocation.get_image(image))
            x, y = mouse.position
            auto.moveTo(x - 60, y - 60, duration=0.25)
            return info(message='通过图片定位并右击', data=image)
        except Exception as e:
            return error(e, image)

    @staticmethod
    def double_click(image):
        """
        通过图片定位并双击
        :param image:图片文件
        :return:
        """
        try:
            auto.doubleClick(ImageLocation.get_image(image))
            x, y = mouse.position
            auto.moveTo(x - 60, y - 60, duration=0.25)
            return info(message='通过图片定位并双击', data=image)
        except Exception as e:
            return error(e, image)

    @staticmethod
    def input(text):
        """
        :param text: 普通输入，不知支持中文
        :return:
        """
        try:
            if ImageLocation.is_chinese(text):
                return ImageLocation.input_text(text)
            auto.typewrite(text)
            return info(message='模拟用户输入文本', data=text)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def input_text(text='test'):
        """
        :param text: 普通输入，模拟复制粘贴，支持中文
        :return:
        """
        try:
            pyperclip.copy(text)
            auto.hotkey('ctrl', 'v')
            return info(message='模拟用户输入文本', data=text)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def input_text2(text='test'):
        """
        :param text: 模拟键盘输入
        :return:
        """
        try:
            key_tool.input(text)
            return info(message='模拟用户输入文本', data=text)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def press_keyboard(key):
        """
        通过模拟键盘输入，只触发单个键
        :param key: 传参键盘英文标识，例如：'enter'
        :return:
        """
        try:
            auto.press(key)
            return info(message='通过模拟键盘输入，只触发单个键', data=key)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def press_keyboard2(key):
        """
        通过模拟键盘输入，只触发单个键
        :param key: 传参键盘英文标识，例如：'enter'
        :return:
        """
        try:
            key_tool.press(key)
            return info(message='通过模拟键盘输入，只触发单个键', data=key)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def press_keyboards(*keys):
        """
        通过模拟键盘输入，可以支持组合案件
        :param keys: 传参键盘英文标识，例如：'shift','a'
        :return:
        """
        try:
            text = None
            if '%2C' in keys[0] or '%2C+' in keys[0]:
                # 兼容保利云测平台调用
                _keys = keys[0].replace('%2C+', '%2C')
                _keys = _keys.split('%2C')
                text = _keys[0]
                keys = tuple(_keys)
            if text and len(text) > 1 and (text not in (
                    'win', 'cmd', 'capslock', 'space', 'tab', 'enter', 'escape', 'backspace', 'del', 'insert', 'home',
                    'end', 'pgup', 'pgdn', 'up', 'down', 'right', 'left', 'shift', 'ctrl')):
                print('--------输入：' + text)
                return ImageLocation.input(text)
            else:
                print('--------组合按键：', keys)
                auto.hotkey(*keys)
                return info(message='通过模拟键盘输入，可以支持组合案件', data=keys)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def sleep(seconds):
        auto.sleep(seconds)

    @staticmethod
    def get_text(image, lang=ENG):
        """
        [OCR] 通过图像识别文字
        :param image: 含有文字的图片
        :param lang: 语言模板（常规用‘chi_sim’、‘eng’）
        :return:
        """
        try:
            if image.startswith('http'):
                image = urllib.request.urlretrieve(image, filename='temp.png')[0]
            else:
                image = image if Path(image).is_file() else ImageLocation.get_image(image)
            text = pytesseract.image_to_string(Image.open(image), lang)
            return info(message='通过图像识别文字', data=text.strip('\n'))
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def get_text2(image):
        try:
            _image = image
            if image.startswith('http'):
                image = urllib.request.urlretrieve(image, filename='temp.png')[0]
            else:
                image = image if Path(image).is_file() else ImageLocation.get_image(image)
            text = ocr.run(os.path.join(tmp_path, image))
            try:
                # 部分机器windows系统缺少dll文件，执行报错，转发到106机器处理
                if type(text) == dict and '10.10.102.106' not in Config.Host:
                    if int(text['code']) > 200:
                        response = requests.post(url='http://10.10.102.106:8081/api/intelligent/get_text2',
                                                 data={"image": _image})
                        text = response.json().get('data')
            except:
                pass

            return info(message='通过图像识别文字', data=text)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def get_location_text(region=(0, 0, 0, 0), lang=ENG):
        """
        [OCR] 通过图像识别文字
        :param region: 识别区域
        :param lang: 语言模板（常规用‘chi_sim’、‘eng’）
        :return:
        """
        try:
            file = f'{tempfile.gettempdir()}{ImageLocation.now_to_timestamp()}.png'
            im = auto.screenshot(file, region)
            im.save(file)
            text = pytesseract.image_to_string(file, lang)
            return info(message='通过图像识别文字', data=text.strip('\n'))
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def screenshot():
        """
        全屏截屏
        :return: None
        """
        try:
            image_name = time.time()
            file = os.path.join(ROOT_PATH, "image.temp", f"{image_name}.png")
            remote = "http://{0}:8081/api/common/image?image_id={1}".format(ip_util.get_ip(), image_name)
            im = auto.screenshot()
            im.save(file)
            return info(message='ok', data={'remote': remote, 'file_path': file})
        except Exception as err:
            return error(e=err, t=False)

    @staticmethod
    def screenshot_region(region=(0, 0, 300, 400)):
        """
        不截全屏，截取区域图片。截取区域region参数为：左上角XY坐标值、宽度和高度
        :param region:
        :return:
        """
        try:
            file = f'{tempfile.gettempdir()}{ImageLocation.now_to_timestamp()}.png'
            im = auto.screenshot(file, region)
            im.save(file)
            # 查看图片
            with open(file, 'rb') as f:
                image = f.read()
                resp = Response(image)
                return resp
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def get_pixel(region=(0, 400)):
        # 获取坐标(0,400)所在屏幕点的RGB颜色
        return auto.screenshot().getpixel(region)

    @staticmethod
    def get_center_location(image):
        # 获得文件图片在现在的屏幕上面的中心坐标
        x, y = auto.center(image)
        return x, y

    @staticmethod
    def image_recognition_location(image):
        """
        图像匹配，并返回坐标位置
        :param image: 图片文件
        :return:
        """
        try:
            position = auto.locateOnScreen(ImageLocation.get_image(image))
            return info(message='图像匹配，并返回坐标位置', data=str(position))
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def get_mouse_position():
        """
        获取鼠标坐标位置
        """
        try:
            return info(message='返回当前鼠标坐标', data=mouse.position)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def exists(image, time_out=0):
        """
        判断元素是否存在
        """
        try:
            exist = get_position_by_image(image, 0)
            while not exist:
                time.sleep(1)
                print(time_out)
                time_out -= 1
                exist = get_position_by_image(image, 0)
                if time_out <= 0:
                    break
            print(exist)
            if exist:
                return info(message=f'{urllib_parse(image)} -- 图片存在')
            else:
                return fail(message=f'{urllib_parse(image)} --》 图片不存在或未识别到')
        except Exception as err:
            return fail(message=f'{urllib_parse(image)} --》 识别发生未知异常:{err}')

    @staticmethod
    def wait_element_appear(image, wait_time=10, index=0):
        """
        等待图片
        """
        wait_time = int(wait_time)
        while wait_time:
            exist = get_position_by_image(image, index)
            if exist:
                return info(message=f'{urllib_parse(image)} -- 找到图片元素', data=exist)
            else:
                time.sleep(1)
                wait_time -= 1
        else:
            return error(e=f'{urllib_parse(image)} -- 超时未找到图片元素', t=False)

    @staticmethod
    def alert(text='This is an alert box.', title='Test'):
        # 处理提示框/警告框
        auto.alert(text, title)

    @staticmethod
    def alert_confirm(text='选择一项', buttons=None):
        # 处理选择框
        if buttons is None:
            buttons = ['A', 'B', 'C']
        auto.confirm(text, buttons)

    @staticmethod
    def password(text='Enter password (text will be hidden)'):
        # 输入密码，显示为密文，点击确认
        return auto.password(text)

    @staticmethod
    def prompt(text='Enter test'):
        # 普通输入
        return auto.prompt(text)

    @staticmethod
    def is_chinese(string):
        """
        检查整个字符串是否包含中文
        :param string: 需要检查的字符串
        :return: bool
        """
        for ch in string:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    @staticmethod
    def now_to_timestamp(digits=10):
        # 生成当前时间的时间戳，只有一个参数即时间戳的位数，默认为10位，
        # 输入位数即生成相应位数的时间戳，比如可以生成常用的13位时间戳
        time_stamp = time.time()
        digits = 10 ** (digits - 10)
        time_stamp = int(round(time_stamp * digits))
        return time_stamp

    @staticmethod
    def mkdir(path):
        try:
            # 去除首位空格
            path = path.strip()
            # 去除尾部 \ 符号
            path = path.rstrip("\\")
            # 判断路径是否存在
            is_exists = os.path.exists(path)

            # 判断结果
            if not is_exists:
                # 如果不存在则创建目录
                os.makedirs(path)
            return path
        except Exception as e:
            print(e)
            return path

    @staticmethod
    def open(path=''):
        try:
            os.startfile(path)
            return info(message=f'成功打开Window应用：{path}', data=True)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def close(app_name=''):
        try:
            os.system(f'taskkill /F /IM {app_name}')
            return info(message=f'成功关闭Window应用：{app_name}', data=True)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def ai_click(element, event, index, contains, mobile_id, mobile_type, offset):

        def android_screen_shot(img_path):
            print(cmd(f'adb connect {mobile_id}').stdout)
            print(cmd(f'adb -s {mobile_id} shell screencap /sdcard/test.png').stdout)
            print(cmd(f'adb -s {mobile_id} pull /sdcard/test.png {img_path}').stdout)
            print(f'Android: {img_path}')
            return img_path

        try:
            file = os.path.join(ROOT_PATH, "image.temp", f"temp.png")

            if mobile_type == 'android':
                android_screen_shot(file)
            elif mobile_type == 'ios':
                # TODO
                # ios.usb_connect(udid=mobile_id.split(':')[0], port=mobile_id.split(':')[1])
                # ios.screenshot_and_save(file)
                # obj = ocr.run(file, True)
                pass
            else:
                img = auto.screenshot()
                img.save(file)
                print(f'PC: {file}')
            obj = ocr.run(file, True)
            mlist = []
            if element in str(obj):
                for s in obj['data']:
                    text = s["text"]
                    if element == text:
                        print(s)
                        mlist.append(s)
                    elif contains and element in text:
                        print(s)
                        mlist.append(s)
                number = len(mlist) - 1 if index >= len(mlist) else index
                if len(mlist) > 0:
                    try:
                        pos = mlist[number]
                        ps = pos['box']
                        if offset == 'middle':
                            x = ps[0] + abs(ps[0] - ps[2]) / 2
                            y = ps[7] - abs(ps[1] - ps[7]) / 2
                        elif offset == 'upper-left':
                            x = ps[0] + 2
                            y = ps[1] + 2
                        elif offset == 'upper-right':
                            x = ps[4] + 2
                            y = ps[5] - 2
                        elif offset == 'lower-left':
                            x = ps[2] - 2
                            y = ps[3] + 2
                        elif offset == 'lower-right':
                            x = ps[6] + 2
                            y = ps[7] - 2
                        else:
                            x, y = (0, 0)
                        print(f'找到元素： {element}: {x}, {y}')
                        if mobile_type == 'android':
                            cmd(f'adb -s {mobile_id} shell input tap {x} {y}')
                        elif mobile_type == 'ios':
                            # TODO
                            pass
                        elif event == 'left-click':
                            auto.click(x, y)
                        elif event == 'right-click':
                            auto.rightClick(x, y)
                        elif event == 'double-click':
                            auto.doubleClick(x, y)
                        elif event == 'move':
                            auto.moveTo(x, y)
                    except Exception as err:
                        return info(message=err, data=mlist)
                    return info(message=f'success', data=mlist)
                else:
                    return info(message=f'Fail: No full match found, please try use contains=true!', data=obj)
            else:
                print(f'没有找到元素： {element}')
                return info(message=f'No full match found, please check your element', data=obj)
        except Exception as e:
            return error(e=e, t=False)

    @staticmethod
    def distinguish(element, _platform, position, mobile_id=None):
        """识别定位"""

        text = element.strip()

        def android_screen_shot(img_path):
            print(cmd(f'adb connect {mobile_id}').stdout)
            print(cmd(f'adb -s {mobile_id} shell screencap /sdcard/test.png').stdout)
            print(cmd(f'adb -s {mobile_id} pull /sdcard/test.png {img_path}').stdout)
            print(f'Android: {img_path}')
            return img_path

        def win_screen_shot(img_path):
            auto.screenshot().save(img_path)
            return img_path

        def ios_screen_shot(img_path):
            # TODO
            return img_path

        def screen_shot(_platform):
            _file = os.path.join(ROOT_PATH, "image.temp", f"temp.png")
            if _platform == 'win':
                win_screen_shot(_file)
            elif _platform == 'android':
                android_screen_shot(_file)
            elif _platform == 'ios':
                ios_screen_shot(_file)
            else:
                # TODO 其它系统待实现
                pass
            return _file

        def conversion_list(str_list):
            lis = str_list[:-1]
            lis = lis.strip('[')
            lis = str(lis).split(',')
            result = []
            for i in lis:
                result.append(int(i))
            return result

        def intelligent_recognition(image):
            x = position[0]
            y = position[1]
            plist = []

            _IMG = image + '.png'
            if _platform == 'win':
                box = (x - 100, y - 30, (x - 100) + 200, (y - 30) + 75)
            elif _platform == 'android':
                box = (x - 100, y - 160, (x - 100) + 100, (y - 160) + 160)
            if x != 0 and y != 10:
                img = Image.open(image)
                img = img.crop(box)
                img.save(_IMG)
                obj = ocr.run(_IMG, True)
                if text in str(obj['data']):
                    for s in obj['data']:
                        if text in s["text"]:
                            plist.append(Element().set(s["text"], s['box']))  # 找到元素对象
            else:
                obj = ocr.run(image, True)
                if text in str(obj['data']):
                    for s in obj['data']:
                        if text in s["text"]:
                            plist.append(Element().set(s["text"], s['box']))  # 找到元素对象
            if x != 0 and y != 10:
                return plist[0]
            _list = []
            _x_c = 1000
            _y_c = 1000
            for p in plist:
                _c_x = abs(x - p.x)
                _c_y = abs(y - p.y)
                if _c_x < _x_c and _c_y < _y_c:
                    _x_c = _c_x
                    _y_c = _c_y
                    _list.clear()
                    _list.append(p)
            return _list

        try:
            file = screen_shot(_platform)
            position = conversion_list(position)
            find_result = intelligent_recognition(file)
            if find_result:
                element = find_result[0]
                print(f"AI识别成功：{element.__dict__}")
                ImageLocation.click_point(element.x, element.y)
                return info(message=f'AI识别成功', data=element)
            else:
                print(f"AI识别失败：{element}")
                x, y = position
                if x != 0 and y != 10:
                    ImageLocation.click_point(x, y)
                return info(message=f'AI识别失败：', data=element)
        except Exception as err:
            return error(e=err, t=False)

    @staticmethod
    def click_point(x, y):
        try:
            print('点击', x, y)
            auto.click(x, y)
            return info(message=f'点击指定坐标位置', data=f'{x}, {y}')
        except Exception as err:
            return error(e=err, t=False)

    @staticmethod
    def screenshot_as_base64(platform, alias, device):

        image_name = time.time()
        file = os.path.join(ROOT_PATH, "image.temp", f"{image_name}.png")

        def tobase64(image):
            f = open(image, 'rb')  # 二进制方式打开图文件
            ls_f = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
            f.close()
            return ls_f

        def android_screen_shot(img_path):
            print(cmd(f'adb connect {device}').stdout)
            print(cmd(f'adb -s {device} shell screencap /sdcard/test.png').stdout)
            print(cmd(f'adb -s {device} pull /sdcard/test.png {img_path}').stdout)
            print(f'Android: {img_path}')
            return tobase64(img_path)

        def win_screen_shot(img_path):
            auto.screenshot().save(img_path)
            return tobase64(img_path)

        if alias:
            return WebDriverAgent().get_screenshot_as_base64(alias)
        elif device and platform == 'android':
            return info(message='android屏幕截屏', data=android_screen_shot(file))
        elif platform == 'win':
            return info(message='windows 桌面截屏', data=win_screen_shot(file))
        elif platform == 'ios':
            return info(message='ios屏幕截屏暂未实现', data=None)
        else:
            return error(e='其他操作系统截屏暂未实现', t=False, data=None)

    @staticmethod
    def drag(x, y, tox, toy, duration=0.2, button='left'):
        try:
            auto.moveTo(x, y)
            auto.dragTo(tox, toy, duration, button=button)
            return info(message=f'拖拽成功（{x},{y} --> {tox},{toy}）')
        except:
            return error('拖拽鼠标异常')

    @staticmethod
    def drags(boxs, duration=0.2, button='left'):
        """
        批量拖拽，例如通过一组坐标数据绘制目标内容
        :param boxs: 一组坐标数据
        :param duration: 每次拖拽的用时
        :param button: 鼠标左键或右键
        :return:
        """
        msg = []
        boxs = str(boxs).split('&')[0].replace('%5B', '').replace('%5D', '').split('%2C+')
        i = 0
        box = []
        for num in boxs:
            i += 1
            box.append(int(num))
            if i == 4:
                msg.append(ImageLocation.drag(box[0], box[1], box[2], box[3], duration, button).message)
                i = 0
                box.clear()
        print(msg)
        return info(message='批量拖拽成功', data=msg)

    @staticmethod
    def drag_image_to_position(image, position, duration=0.2, button='left'):
        """
        识别图片元素位置，并拖拽到指定位置
        :param position: 指定的目标位置
        :param image: 要识别的图片【起始位置】
        :param duration: 起始坐标拖拽到终止坐标的使用时间
        :param button: 鼠标左键或右键（默认左键）
        :return:
        """
        x, y = get_position_by_image(image)
        return ImageLocation.drag(x, y, position[0], position[1], duration, button=button)

    @staticmethod
    def drag_image1_to_image2(image, image2, duration=0.2, button='left'):
        """
        元素1拖拽至元素2
        :param image: 画面中的图1
        :param image2: 画面中的图2
        :param duration: 起始坐标拖拽到终止坐标的使用时间
        :param button: 鼠标左键或右键（默认左键）
        :return:
        """
        x, y = get_position_by_image(image)
        x1, y1 = get_position_by_image(image2)
        return ImageLocation.drag(x, y, x1, y1, duration, button=button)

    @staticmethod
    def move_to(x, y):
        try:
            print('移动鼠标到目标位置', x, y)
            auto.moveTo(x, y)
            return info(message='移动鼠标到目标位置', data=f'{x}, {y}')
        except Exception as err:
            return fail(message=err, status=False)

    @staticmethod
    def move_to_by_image(image):
        try:
            print(urllib_parse(image))
            x, y = get_position_by_image(image, 0)
            print(x, y)
            auto.moveTo(x, y)
            return info(message=f'移动鼠标到目标图片位置:{urllib_parse(image)}', data=f'{x}, {y}')
        except Exception as err:
            return fail(message=err, status=False)


class Element(object):
    text = None
    box = None
    x = None
    y = None
    position = None

    def set(self, text, box):
        self.text = text
        self.box = box
        self.x = box[0] + abs(box[0] - box[2]) / 2
        self.y = box[7] - abs(box[1] - box[7]) / 2
        self.position = (self.x, self.y)
        return self


if __name__ == '__main__':
    # cp = os.path.abspath(os.path.dirname(__file__))
    # image_path = cp[:cp.find("agent-auto-test\\") + len("agent-auto-test\\")] + 'temp\\'
    # at = ImageLocation(image_path)  # 图像存储位置
    # result = at.get_text('help.png')
    # print(result)
    # ImageLocator().image_recognition_location(
    #     'b32116f4-a18a-4e80-a5e3-036fd29e5587')
    ...
    # image = r'C:\Users\T470\AppData\Local\Temp\test.png'
    # _object = auto.locateOnScreen(image=image)
    # x, y = auto.center(_object)
    # auto.click(x, y)
