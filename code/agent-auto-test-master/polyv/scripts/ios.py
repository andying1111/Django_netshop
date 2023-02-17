# coding=utf-8

import os
import json
import time

import wda

from polyv.common import ip_util
from polyv.common.data_format import DataFormat


class IOSBase:
    result = DataFormat()
    device = None
    app = None

    # wda 全局配置
    wda.DEBUG = True
    wda.HTTP_TIMEOUT = 240.0
    wda.DEVICE_WAIT_TIMEOUT = 240.0

    @staticmethod
    def exec_cmd(cmd):
        """
        执行命令行
        """
        p = os.popen(cmd)
        lines = p.readlines()
        p.close()
        return lines

    def devices(self):
        """
        获取iOS设备列表
            修复：json转换字符串时报错
        """
        device_list = []

        cmd_results = self.exec_cmd('tidevice list')
        if len(cmd_results) == 0:
            return []

        try:
            for device in cmd_results:
                _msg = device.split()
                _udid = _msg[0]
                del _msg[0]
                _name = ''.join(_msg)
                device_list.append({'udid': _udid, "name": _name})

            return device_list
        except:
            return []

    def wait(self, time_out=1.0):
        """
        iOS 等待API，默认等待1秒
            目前使用time.sleep，wda中没有提供显示等待API
        """
        time.sleep(int(time_out))
        return self.result.set(f'等待{time_out}秒')


class IOSDevice(IOSBase):
    def init_ios_device(self):
        """
        初始化iOS设备
        """
        con_status = self.device.status()
        if con_status['state'] == 'success':
            self.device.home()
            return True
        else:
            return False

    def usb_connect(self, udid=None, port=8100):
        """
        连接iOS设备(目前仅USB设备，不支持模拟器设备)
            连接方式：设备udid连接（wda提供USBdevice可以直接通过wda启动webdeviceAgent）
        """
        ios_devices = self.devices()
        if len(ios_devices) == 0:
            return self.result.set(code=500, status=False, message='没有连接任何设备,请重新连接设备后再尝试')

        try:
            if udid is None:
                ios_device = ios_devices[0]
                device_name = ios_device['name']
                device_udid = ios_device['udid']
                self.device = wda.USBClient(udid=device_udid, port=port)
                self.init_ios_device()
                return self.result.set(message=f'设备已成功连接{device_name}: success')
            else:
                self.device = wda.USBClient(udid=udid, port=port)
                return self.result.set(message=f'设备已成功连接{udid}: success')
        except Exception as e:
            return self.result.set(code=500, status=False, message=f'设备连接失败{e}')

    def url_connect(self, adr='localhost', port=8100):
        """
        连接iOS设备(目前仅USB设备，不支持模拟器设备)
            连接方式：url连接（需要手动通过tidevice命令启动webdeviceAgent）
        """
        try:
            if not adr.startswith('http://'):
                device_url = f'http://{adr}:{port}'
            else:
                device_url = f'{adr}:{port}'

            self.device = wda.Client(url=device_url)
            init_result = self.init_ios_device()
            if init_result:
                return self.result.set(message=f'设备已成功连接{device_url}: success')
            else:
                return self.result.set(code=500,status=False, message=f'设备连接不成功{device_url}')

        except Exception as e:
            return self.result.set(code=500, status=False, message=f'设备连接失败{e}')

    def disconnect(self):
        """
        断开连接
        """
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备，无需断开链接')
        else:
            self.device = None
            return self.result.set(message='成功断开连接')

    def home(self):
        """
        点击home键
        """
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备, 请先连接设备')
        else:
            try:
                self.device.home()
                return self.result.set(message='返回桌面成功')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'返回桌面失败:{e}')

    def lock(self):
        """
        锁屏
        """
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备, 请先连接设备')
        else:
            try:
                self.device.lock()
                if self.device.locked():
                    return self.result.set(message='锁屏成功')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'锁屏失败:{e}')

    def unlock(self):
        """
        解锁屏幕
        """
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备, 请先连接设备')
        else:
            try:
                self.device.unlock()
                if self.device.locked() is False:
                    return self.result.set(message='解锁屏幕成功')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'解锁屏幕失败:{e}')

    def screenshot_and_save(self, filename=None):
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备, 请先连接设备')

        try:
            if filename is None:
                img_name = str(time.time())
            else:
                img_name = str(filename)

            img_path = os.path.join(os.path.join(os.getcwd(), 'image.temp'), img_name + '.png')
            remote = "http://{0}:8081/api/common/image?image_id={1}".format(ip_util.get_ip(), img_name)

            self.device.screenshot().save(img_path)
            return self.result.set(
                message=f'IOS创建截图成功{img_name}',
                data={
                    "remote": remote,
                    "file_path": img_path
                }
            )
        except Exception as e:
            return self.result.set(message=f'IOS创建截图失败，报错：{e}')

    def page_source(self):
        """
        source
        """
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备, 请先连接设备')
        else:
            try:
                source = self.device.source(accessible=True)
                return self.result.set(data=source)
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'获取page_source失败:{e}')


class IOSApp(IOSBase):
    def __app_init(self):
        """
        app 参数初始化
        """
        self.app.implicitly_wait(30.0)

    def open_app(self, app_bundle_id):
        """
        打开app应用
        """
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备, 请先连接设备')
        else:
            try:
                self.app = self.device.session(app_bundle_id, alert_action="accept")
                self.__app_init()
                return self.result.set(message=f'打开app: {app_bundle_id} 成功')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'打开app: {app_bundle_id} 失败，报错:{e}')

    def open_browser_app_url(self, browser_bundle_id, url):
        """"""
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备, 请先连接设备')
        else:
            try:
                self.app = self.device.session(browser_bundle_id, ['-u', url])
                self.__app_init()
                return self.result.set(message=f'打开浏览器:{browser_bundle_id}成功,打开网页{url}成功')
            except Exception as e:
                return self.result.set(code=500, status=False,
                                       message=f'打开浏览器:{browser_bundle_id}失败,打开网页{url}失败，报错:{e}')

    def close_app(self, package_name):
        """
        关闭app
        """
        if self.device is None:
            return self.result.set(code=400, status=False, message='没有连接绑定任何设备, 请先连接设备')
        else:
            self.device.app_stop(package_name)
            self.device.home()
            self.app = None
            return self.result.set(message=f'关闭app: {package_name}')

    def find_element(self, element, find_type=''):
        """
        查找元素
        """
        try:
            # find_type为空值时默认查找方式为xpath
            if find_type == '':
                el_obj = self.app(xpath=element, enabled=True)
                return el_obj
            else:
                if find_type == 'xpath':
                    el_obj = self.app(xpath=element, enabled=True)
                    return el_obj
                elif find_type == 'id':
                    el_obj = self.app(id=element, enabled=True)
                    return el_obj
                elif find_type == 'classname':
                    el_obj = self.app(className=element, enabled=True)
                    return el_obj
                elif find_type == 'name':
                    el_obj = self.app(name=element, enabled=True)
                    return el_obj
                elif find_type == 'label':
                    el_obj = self.app(label=element, enabled=True)
                    return el_obj
                elif find_type == 'value':
                    el_obj = self.app(value=element, enabled=True)
                    return el_obj
        except:
            el_obj = None
            return el_obj

    def element_click(self, element, find_type=''):
        """
        点击元素
        """
        if self.app is None:
            return self.result.set(code=400, status=False, message='应用没有启动成功，请重新启动应用')
        else:
            try:
                ele_obj = self.find_element(element, find_type)
                ele_obj.click()
                return self.result.set(message=f'{element} 点击元素')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'{element} 点击失败{e}')

    def element_send_text(self, element, value, find_type=''):
        """
        向元素输入字符
        """
        if self.app is None:
            return self.result.set(code=400, status=False, message='应用没有启动成功，请重新启动应用')
        else:
            try:
                ele = self.find_element(element, find_type)
                # 需要先点击输入框
                ele.click()
                ele.clear_text()
                ele.set_text(value)
                return self.result.set(message=f'在元素{element}内输入{value}成功')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'在元素{element}内输入{value}失败：{e}')

    def element_click_hold(self, element, hold_time=1, find_type=''):
        """
        长按元素
        """
        if self.app is None:
            return self.result.set(code=400, status=False, message='应用没有启动成功，请重新启动应用')
        else:
            try:
                self.find_element(element, find_type).tap_hold(hold_time)
                return self.result.set(message=f'长按元素-{element}')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'长按元素-{element}-失败:{e}')

    def element_swipe(self, element, direction, find_type=''):
        """
        拖动元素
            方向参数可以是： "up", "down", "left", "right"
        """
        if self.app is None:
            return self.result.set(code=400, status=False, message='应用没有启动成功，请重新启动应用')
        else:
            try:
                if direction in ['up', 'down', 'left', 'right']:
                    self.find_element(element, find_type).scorll(direction)
                    return self.result.set(message=f'向{direction}方向拖动元素{element}成功')
                else:
                    return self.result.set(code=400, status=False,
                                           message="拖动方向参数不存在，目前仅支持['up', 'down', 'left', 'right']")
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'向{direction}方向拖动元素元素{element}-失败:{e}')

    def coordinate_click(self, x, y):
        """
        坐标点击
        """
        if self.app is None:
            return self.result.set(code=400, status=False, message='应用没有启动成功，请重新启动应用')
        else:
            try:
                self.app.click(float(x), float(y))
                return self.result.set(message=f'点击坐标({x}, {y})')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'点击坐标({x}, {y})失败{e}')

    def coordinate_click_hold(self, x, y, hold_time=1):
        """
        坐标长按
        """
        if self.app is None:
            return self.result.set(code=400, status=False, message='应用没有启动成功，请重新启动应用')
        else:
            try:
                self.app.tap_hold(x, y, hold_time)
                return self.result.set(message=f'长按坐标({x}, {y})')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'长按坐标({x}, {y})失败{e}')

    def coordinate_double_click(self, x, y):
        """
        坐标双击
        """
        if self.app is None:
            return self.result.set(code=400, status=False, message='应用没有启动成功，请重新启动应用')
        else:
            try:
                self.app.double_tap(x, y)
                return self.result.set(message=f'双击坐标({x}, {y})')
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'双击坐标({x}, {y})失败{e}')

    def app_turn_page(self, direction):
        """
        app翻页
        """
        if self.app is None:
            return self.result.set(code=400, status=False, message='应用没有启动成功，请重新启动应用')
        else:
            try:
                if direction == 'up':
                    self.app.swipe_up()
                    return self.result.set(message=f'向上翻页成功')
                elif direction == 'down':
                    self.app.swipe_down()
                    return self.result.set(message=f'向下翻页成功')
                elif direction == 'left':
                    self.app.swipe_left()
                    return self.result.set(message=f'向左翻页成功')
                elif direction == 'right':
                    self.app.swipe_right()
                    return self.result.set(message=f'向右翻页成功')
                else:
                    return self.result.set(code=400, status=False,
                                           message="拖动方向参数不存在，目前仅支持['up', 'down', 'left', 'right']")
            except Exception as e:
                return self.result.set(code=500, status=False, message=f'翻页失败{e}')


class IOSAlert(IOSApp):
    """
    iOS 处理系统弹窗
    """

    def checkout_alert_exists(self):
        if self.device.alert.exists:
            alert_data = {
                "text": self.device.alert.text,
                "btn_list": self.device.alert.buttons()
            }
            return self.result.set(message='页面存在系统弹窗', data=alert_data)
        else:
            return self.result.set(code=400, status=False, message='不存在任何弹窗')

    def checkout_alert_text_assert(self, text):
        """
        警告弹窗断言
        """
        if self.device.alert.exists:
            alert_text = self.device.alert.text
            if text in alert_text:
                return self.result.set(message=f'预期文本{text}与实际文本{alert_text}一致')
            else:
                return self.result.set(code=400, status=False, message=f'预期文本{text}与实际文本{alert_text}不一致')
        else:
            return self.result.set(code=400, status=False, message='不存在任何系统弹窗')


class IOSAssert(IOSApp):
    """
    ios 断言模块
    """

    def get_element_attributes(self, element, attributes, find_type=''):
        """
        获取元素属性
        """
        el = self.find_element(element, find_type)

        if attributes == 'classname':
            return el.className
        elif attributes == 'name':
            return el.name
        elif attributes == 'value':
            return el.value
        elif attributes == 'label':
            return el.label
        elif attributes == 'text':
            return el.text
        elif attributes == 'visible':
            return el.visible
        elif attributes == 'enabled':
            return el.enabled
        elif attributes == 'displayed':
            return el.displayed

    def element_exists(self, element, timeout, find_type=''):
        """
        元素是否存在
        """
        for i in range(int(timeout)):
            el = self.find_element(element, find_type)
            if el.exists:
                return self.result.set(message=f'{element}元素存在')
            time.sleep(1)
        else:
            return self.result.set(code=400, status=False, message=f'{element}元素不存在')

    def element_text_equal_text(self, element, text, find_type=''):
        el_text = self.get_element_attributes(element, 'text', find_type)

        if text in el_text:
            return self.result.set(message=f'预设文本{text}与元素文本{el_text}一致')
        else:
            return self.result.set(code=400, status=False, message=f'预设文本{text}与元素文本{el_text}不一致')


class IOSAgent(IOSAssert, IOSAlert, IOSApp, IOSDevice):
    pass


if __name__ == '__main__':
    print(IOSDevice().devices())
