import os
import platform
import subprocess
import time

import pyautogui
from fastapi import Response
from selenium import webdriver  # web自动化库
from selenium.webdriver import ActionChains  # 模拟事件

from polyv.common import ip_util
from polyv.common.data_format import DataFormat


def press(key):
    pyautogui.press(key)


class WebAgent(object):
    """
    Mac系统 - electron 应用UI自动化库
    """
    driver = None
    result = DataFormat()

    def status(self):
        return self.result.set(data="服务健康运行中!")

    @staticmethod
    def cmd(command):
        """执行cmd命令"""
        print(command)
        return subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              encoding="utf-8", timeout=300).stdout

    def find(self, tag='text', element=''):
        """
        通用定位
        :param tag: 元素类型
        :param element: 元素属性
        :return:
        """
        try:
            if tag.lower() == 'id':
                return self.driver.find_element_by_id(element)
            elif tag == 'xpath':
                return self.driver.find_element_by_xpath(element)
            elif tag == 'name':
                return self.driver.find_element_by_name(element)
            elif tag == 'text':
                return self.driver.find_element_by_xpath("//*[text()='{}']".format(element))
            elif tag == 'classname':
                return self.driver.find_element_by_class_name(element)
            elif tag == 'tagname':
                return self.driver.find_element_by_tag_name(element)
            elif tag == 'linktext':
                return self.driver.find_element_by_link_text(element)
        except Exception as err:
            print(err)
            return None

    def finds(self, tag='text', element='', index=0):
        """
        通用定位
        :param index: 索引
        :param tag: 元素类型
        :param element: 元素属性
        :return:
        """
        try:
            if tag.lower() == 'id':
                return self.driver.find_elements_by_id(element)[index]
            elif tag == 'xpath':
                return self.driver.find_elements_by_xpath(element)[index]
            elif tag == 'name':
                return self.driver.find_elements_by_name(element)[index]
            elif tag == 'text':
                return self.driver.find_elements_by_xpath("//*[text()='{}']".format(element))[index]
            elif tag == 'classname':
                return self.driver.find_elements_by_class_name(element)[index]
            elif tag == 'tagname':
                return self.driver.find_elements_by_tag_name(element)[index]
            elif tag == 'linktext':
                return self.driver.find_elements_by_link_text(element)[index]
        except Exception as err:
            print(err)
            return None

    def press(self, key: str):
        """
        执行键盘按键事件
        """
        try:
            keys = key.split(',')
            pyautogui.press(keys)
            return self.result.set(data='press success ——> {}'.format(key))
        except Exception as err:
            return self.result.set(400, False, message=str(err))

    def press_combination(self, key1: str, key2: str):
        """
        执行键盘按键事件
        """
        try:
            pyautogui.hotkey(key1, key2)
            return self.result.set(data='press success ——> [{}, {}]'.format(key1, key2))
        except Exception as err:
            return self.result.set(400, False, message=str(err))

    def open(self, address=None):
        """
        打开应用
        :param address: 应用路径
        :return:
        """
        try:
            if self.driver is not None:
                return self.result.set(message='is opened')  # 已打开，直接返回

            if 'Windows' in platform.system():
                path = './chromedriver.exe'
            elif 'Darwin' in platform.system():
                path = './chromedriver'
            else:
                return self.result.set(403, False, 'Unsupported operating system: %s' % platform.system())

            # if not os.path.exists(path):
            #     file_utils.FileUtils().download_web_driver()
            options = webdriver.ChromeOptions()
            options.binary_location = address
            self.driver = webdriver.Chrome(executable_path=path, chrome_options=options)
            self.driver.implicitly_wait(5)
            return self.result.set(data='open success')
        except Exception as err:
            return self.result.set(400, False, err)

    def open_url(self, url=''):
        """ 打开指定网页 """
        try:
            if self.driver is not None:
                self.driver.get(url)
                return self.result.set(message='is opened')  # 已打开，直接返回

            if 'Windows' in platform.system():
                path = './lib/chromedriver.exe'
            elif 'Darwin' in platform.system():
                path = './lib/chromedriver'
            else:
                return self.result.set(403, False, 'Unsupported operating system: %s' % platform.system())

            if not os.path.exists(path):
                print('chromedriver not found')
            self.driver = webdriver.Chrome(executable_path=path)
            # self.driver.implicitly_wait(5)
            time.sleep(1)
            self.driver.get(url)
            return self.result.set(data='open success')
        except Exception as err:
            self.close()
            return self.result.set(400, False, err)

    def close(self):
        """
        关闭当前已打开的浏览器
        :return:
        """
        try:
            self.driver.quit()
            self.driver = None
        except Exception as err:
            return self.result.set(400, False, message=str(err))
        return self.result.set(data='close success')

    def switch_handle(self, index=1):
        """
        切换窗口
        :param index:
        :return:
        """
        try:
            print(self.driver.switch_to_window(self.driver.window_handles[index]))
            return self.result.set(message='switch to window ok', data=self.driver.window_handles)
        except Exception as err:
            return self.result.set(400, False, message=str(err), data='切换 Handles 发生异常！')

    def click(self, tag, element, index=-1):
        """
        点击控件
        :param index: 下标
        :param tag: 元素类型
        :param element: 元素属性
        :return:
        """
        if index < 0:
            self.wait_element(tag, element)
            ele = self.find(tag, element)
        else:
            self.wait_element(tag, element, index)
            ele = self.finds(tag, element, index)
        try:
            ele.click()
            return self.result.set(data='click to [{}] ok!'.format(element))
        except Exception as err:
            return self.result.set(400, False, message=str(err), data='Not find [{}]'.format(element))

    def wait_element(self, tag, element, index=-1, times=5):
        """
        等待元素出现
        :param tag: 元素类型
        :param element: 元素属性
        :param index: 复数
        :param times: 单位秒
        :return:
        """
        try:
            while True:
                if index < 0:
                    ele = self.find(tag, element)
                else:
                    ele = self.finds(tag, element, index)

                times -= 1
                if ele is not None:
                    return self.result.set(message='已出现元素: {}'.format(element), data=True)
                elif times <= 0:
                    return self.result.set(message='未出现元素: {}'.format(element), data=False)
                time.sleep(1)

        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def get_text(self, tag, element, index=-1):
        """
        获取控件文本
        :param index:
        :param tag: 元素类型
        :param element: 元素属性
        :return:
        """
        print(element)
        try:
            if index < 0:
                ele = self.find(tag, element)
            else:
                ele = self.finds(tag, element, index)
                print('文本：{}'.format(ele.text))
            return self.result.set(data=ele.text)
        except Exception as err:
            return self.result.set(400, False, message=str(err))

    def input(self, tag, element, text='', index=-1):
        """
        输入文本
        :param index:
        :param tag: 元素类型
        :param element: 元素属性
        :param text: 内容
        :return:
        """
        try:
            if index < 0:
                ele = self.find(tag, element)
                ele.clear()
                ele.send_keys(text)
            else:
                ele = self.finds(tag, element, index)
                ele.clear()
                ele.send_keys(text)
            return self.result.set(data='input [{}] to [{}] success!'.format(text, element))
        except Exception as err:
            return self.result.set(400, False, message=str(err))

    def clear(self, tag, element, index=-1):
        """
        空编辑框内容
        :param index:
        :param tag: 元素类型
        :param element: 元素属性
        :return:
        """
        try:
            if index < 0:
                self.find(tag, element).clear()
            else:
                self.finds(tag, element, index).clear()
            return self.result.set(data='clear success!')
        except Exception as err:
            return self.result.set(400, False, message=str(err))

    def exist(self, tag='text', element='', index=-1):
        """
        判断元素是否存在
        :param index:
        :param tag:
        :param element:
        :return:
        """
        try:
            if index < 0:
                stirs = not self.find(tag, element) is None
            else:
                stirs = not self.finds(tag, element, index) is None
            return self.result.set(data='Whether this element [{}] exists: {}'.format(element, stirs))
        except Exception as err:
            return self.result.set(400, False, message=str(err))

    def mouse_to_element(self, tag, element, index=-1):
        """
        鼠标移动到指定元素上
        :param index: 复数
        :param tag: 元素类型
        :param element: 元素属性
        :return:
        """
        try:
            if index < 0:
                ele = self.find(tag, element)
            else:
                ele = self.finds(tag, element, index)
            ActionChains(self.driver).move_to_element(ele).perform()
            return self.result.set(data='move to [{}] success'.format(element))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def drag_element(self, tag1, source, tag2, target, index1, index2):
        """
        拖拽元素
        :param tag2:
        :param tag1:
        :param source:
        :param target:
        :return:
        """
        try:
            if index1 > 0:
                el_source = self.finds(tag1, source, index1)
            else:
                el_source = self.finds(tag1, source)
            if index2 > 0:
                el_target = self.finds(tag1, source, index2)
            else:
                el_target = self.finds(tag1, source)

            if self.driver.w3c:
                ActionChains(self.driver).drag_and_drop(el_source, el_target).perform()
            else:
                ActionChains(self.driver).click_and_hold(el_source).perform()
                ActionChains(self.driver).move_to_element(el_target).perform()
                ActionChains(self.driver).release(el_target).perform()
            self.result.set(data='drag element success!')
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def click_offset(self, x, y, direction):
        """
        :param x: 页面x坐标
        :param y: 页面y坐标
        :param direction: True为鼠标左键点击，否则为右键点击
        :return:
        """
        log = 'left-click'
        try:
            if 'left' in direction:
                ActionChains(self.driver).move_by_offset(x, y).click().perform()  # 鼠标左键点击
            else:
                ActionChains(self.driver).move_by_offset(x, y).context_click().perform()  # 鼠标右键点击
                log = 'right-click'
            ActionChains(self.driver).move_by_offset(-x, -y).perform()  # 将鼠标位置恢复到移动前
            return self.result.set(data='[{}] success'.format(log))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def mouse_click_point(self, x, y):
        """
        模拟鼠标点击 TODO
        :param x:
        :param y:
        :return:
        """
        try:
            # mouse().click(x, y, button) TODO
            return self.result.set(message='click [{0},{1}] success'.format(x, y))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def mouse_move_point(self, x, y):
        """
        模拟鼠标移动 TODO
        :param x:
        :param y:
        :return:
        """
        try:
            # mouse().move(x, y)
            # TODO
            return self.result.set(message='move [{0},{1}] success'.format(x, y))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def screen_shot(self, flog, name=None):
        try:
            if name is None:
                image_name = time.time()
            else:
                image_name = name
            file = os.getcwd() + "/image.temp/{}.png".format(image_name)
            remote = "http://{0}:8081/image?image_id={1}".format(ip_util.get_ip(), image_name)
            if flog == 0:
                self.driver.get_screenshot_as_file(file)
            else:
                pyautogui.screenshot(file)
            return self.result.set(data=remote)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    @staticmethod
    def get_image(image_id):
        # 查看图片
        file = os.getcwd() + "/image.temp/{}.png".format(image_id)
        with open(file, 'rb') as f:
            image = f.read()
            resp = Response(image)
            return resp

    @staticmethod
    def get_report(report_id):
        # 查看报告
        file = os.getcwd() + "/report/{}.html".format(report_id)
        with open(file, 'rb') as f:
            report = f.read()
            resp = Response(report)
            return resp


if __name__ == '__main__':
    print(platform.system())
    e = WebAgent()
    e.open_url('https://www.baidu.com/')
