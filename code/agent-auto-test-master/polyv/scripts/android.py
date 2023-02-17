import os
import re
import subprocess
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from polyv.common import ip_util
from polyv.common.chromewebdriver import ChromeDriver
from polyv.common.data_format import DataFormat
from selenium.webdriver.support import expected_conditions as EC
import uiautomator2 as u2


class AndroidAgent:
    result = DataFormat()
    device = None
    timeout = 30
    operation_delay = (1, 1)
    driver = None

    def _execCmd(self, cmd):
        """
        执行命令行
        :param cmd:
        :return:
        """
        p = os.popen(cmd)
        lines = p.readlines()
        p.close()
        return lines

    def _devices(self):
        """
        找出设备状态为device的设备号
        :return:
        """
        lines = self._execCmd('adb devices')
        print(lines)
        ds = []
        for line in lines:
            keys = re.findall("""\tdevice\n""", line, re.S)
            if len(keys) > 0:
                ds.append(line.split('\t')[0])
        return ds

    def _init(self):
        # 修改延迟为操作前延迟 1S 操作后延迟 2.5S
        self.device.settings['operation_delay'] = self.operation_delay
        # 修改延迟生效方法
        self.device.settings['operation_delay_methods'] = ['click', 'press', 'send_keys']
        # 修改默认等待
        self.device.settings['wait_timeout'] = self.timeout
        # 打不到元素时，等待 10 后再报异常
        self.device.implicitly_wait(float(self.timeout))

    def handle_watcher(self):
        """定义一个监控器"""
        # 监控器会单独起一个线程
        # 用户隐私协议
        self.device.watcher.when(
            '//*[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]').click()
        self.device.watcher.when('//*[@resource-id="com.android.packageinstaller:id/permission_allow_button"]').click()
        self.device.watcher.when(
            '//*[@resource-id="com.lbe.security.miui:id/permission_allow_onetime_button"]').click()  # 小米
        # 广告
        # 监控器写好之后，要通过start方法来启动
        self.device.watcher.start()

    def _devices_is_connected(self):
        return False if not self.device else True

    def device_info(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        return self.result.set(data=self.device.info)

    def device_size(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        return self.result.set(data=self.device.window_size())

    def push_file(self, src, dst):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.push(src, dst)
            return self.result.set(message=f"推送文件{src}至{dst}成功")
        except:
            return self.result.set(code=400, status=False, message=f"推送文件{src}至{dst}失败")

    def pull_file(self, src, dst):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.pull(src, dst)
            return self.result.set(message=f"拉取文件{src}至{dst}成功")
        except:
            return self.result.set(code=400, status=False, message=f"拉取文件{src}至{dst}失败")

    def watch_context(self, context):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            with self.device.watch_context() as ctx:
                ctx.when(context).click()
                return self.result.set(message=f'监控到存在文本{context},并点击成功')
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def connect(self, device=None):
        """
        链接设备
        device_name：设备名称
        """
        try:
            device_name = device if device else self._devices()[0]
            self.device = u2.connect(device_name)
            self._init()
            return self.result.set(message=f'连接并绑定本地设备{device_name}——> success')
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"设备链接失败-{str(e)}")

    def connect_atx_addr(self, addr):
        """
        链接设备
        device_name：设备名称
        """
        try:
            self.device = u2.connect(addr)
            self._init()
            return self.result.set(message=f'连接并绑定atx设备:{addr}——> success')
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"设备链接失败-{str(e)}")

    def connect_adb_wifi(self, wifi_addr=None):
        """
        通过adb—wifi链接链接设备
        wifi_addr：wifi的名称
        """
        try:
            self.device = u2.connect_adb_wifi(wifi_addr)
            self._init()
            return self.result.set(message=f'wifi连接adb成功，绑定设备{wifi_addr}——> success')
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"设备链接失败-{str(e)}")

    def install_app(self, url):
        """安装app
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.app_install(data=url)
            return self.result.set(message="安装app成功")

        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def uninstall_app(self, package_name):
        """卸载app
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.app_uninstall(package_name)
            return self.result.set(message="卸载app成功")

        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def current_package_name(self):
        """
        获取当前运行app的包名
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            print(self.device.current_app())
            return self.result.set(data=self.device.current_app())
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def app_open(self, package_name=None, app_name=None, is_clear=True):
        """
        启动app
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            # self.device.app_wait(package_name, 60, front=True)
            if eval(str(is_clear)):
                self.device.app_clear(package_name)
                print(f"清理app.....{package_name}")
            if app_name:
                self.device(text=app_name).click()
            else:
                self.device.app_start(package_name)

            print('启动监听弹窗....')
            self.handle_watcher()

            return self.result.set(message="启动app成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def app_stop(self, package_name):
        """
        关闭app
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            print('停止监听弹窗...')
            self.device.watcher.stop()
            self.device.app_stop(package_name)
            return self.result.set(message="关闭app成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def app_clear(self, package_name):
        """
        清空app
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.app_clear(package_name)
            return self.result.set(message="清空app数据成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def wait(self, seconds):
        """硬性等待"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        self.device.sleep(seconds)
        return self.result.set(message=f"等待{seconds}s")

    def swipe_left(self, scale=0.9):
        """
        左滑
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.swipe_ext('left', scale)
            return self.result.set(message=f"左滑屏幕,比例{scale}")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def swipe_right(self, scale=0.9):
        """
        右滑
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.swipe_ext('right', scale)
            return self.result.set(message=f"右滑屏幕,比例{scale}")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def swipe_up(self, scale=0.9):
        """
        上滑
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.swipe_ext('up', scale)
            return self.result.set(message=f"上滑屏幕,比例{scale}")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def swipe_down(self, scale=0.9):
        """
        下滑
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.swipe_ext('down', scale)
            return self.result.set(message=f"下滑屏幕,比例{scale}")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def scroll_beginning(self):
        """滚动到屏幕顶部"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:

            self.device(scrollable=True).scroll.toBeginning()
            return self.result.set(message=f"滚动到屏幕顶部成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def scroll_end(self):
        """滚动到屏幕底部"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device(scrollable=True).scroll.toEnd()
            return self.result.set(message=f"滚动到屏幕底部成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def find_element(self, tag, selector, index, wait=True):
        """查找元素"""
        ele = None
        timeout = self.timeout if wait else 1

        if tag == "resourceId":
            for i in range(self.timeout):
                ele = self.device(resourceId=selector)
                if ele.exists:
                    break
                time.sleep(1)
                print(f'未找到{tag}元素，{selector},暂停1s')

        elif tag == "xpath":
            # xpath不会执行全局轮询时间，手动写个
            if index == 0:
                ele = self.device.xpath(selector)
            else:
                for _ in range(timeout):

                    if len(self.device.xpath(selector).all()) >= index + 1:
                        ele = self.device.xpath(selector).all()[index]
                        break
                    print(f'未找到xpath元素，{selector}-{index},暂停1s')
                    time.sleep(1)

        elif tag == "text":
            ele = self.device(text=selector)

        print(ele)
        return ele

    def click(self, tag, selector, index):
        """点击元素
        tag:定位方式
        selector:元素表达式
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        try:
            if tag == 'point':
                self.device.click(*eval(selector))
            else:
                self.find_element(tag, selector, index).click()
            return self.result.set(message=f"点击元素{tag}-{selector}-{index}成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"未找到元素{tag}-{selector}-{index},{e}")

    def double_click(self, x, y, duration):
        """双击坐标
        tag:定位方式
        selector:元素表达式
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.double_click(float(x), float(y), float(duration))
            return self.result.set(message=f"双击坐标{x},{y}成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"双击坐标{x},{y}失败,{e}")

    def long_click(self, tag, selector, index):
        """长按元素
        tag:定位方式
        selector:元素表达式
        """
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.find_element(tag, selector, index).long_click(duration=1)
            return self.result.set(message=f"长按元素{tag}-{selector}成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"未找到元素{tag}-{selector},{e}")

    def clear(self, tag, selector, index):
        """输入文本"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            ele = self.find_element(tag, selector, index)
            ele.clear_text()
            return self.result.set(message=f"元素{tag}-{selector}清空文本成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"未找到元素{tag}-{selector},{e}")

    def send_keys(self, tag, selector, content, index, is_clear=True):
        """输入文本"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            ele = self.find_element(tag, selector, index)
            if is_clear:
                ele.clear_text()
            ele.set_text(content)
            return self.result.set(message=f"输入内容{content},元素{tag}-{selector}成功")
        except AttributeError as e:
            return self.result.set(code=400, status=False, message=f"输入出错，原因{e}")
        except Exception as e:
            # uiautomator2.exceptions.UiObjectNotFoundError
            return self.result.set(code=400, status=False, message=f"报错原因，原因{e}")

    def screen_on(self):
        """点亮设备屏幕"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.screen_on()
            return self.result.set(message="点亮屏幕成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message="点亮屏幕失败")

    def screen_off(self):
        """熄灭设备屏幕"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.screen_on()
            return self.result.set(message="熄灭屏幕成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message="熄灭屏幕失败")

    def press_home(self):
        """点击home键"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.press("home")
            return self.result.set(message="点击home键成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message="点击home键失败")

    def press_back(self):
        """点击back键"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.press("back")
            return self.result.set(message="点击back键成功 ")
        except Exception as e:
            return self.result.set(code=400, status=False, message="点击back键失败")

    def press_enter(self):
        """点击enter键"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.press("enter")
            return self.result.set(message="点击enter键成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message="点击enter键失败")

    def press(self, value):
        """点击enter键"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.press(value)
            return self.result.set(message=f"点击{value}键成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"点击{value}键失败,{e}")

    def send_action(self, code):
        """点击enter键"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.send_action(code)
            return self.result.set(message=f"点击{code}键成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"点击{code}键失败,{e}")

    def set_ime(self, enable=True):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.device.set_fastinput_ime(enable)
            return self.result.set(message=f"切换输入法为{enable}成功")
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"切换输入法为{enable}失败,{e}")

    def get_ele_info(self, tag, selector, index):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            ele = self.find_element(tag, selector, index)
            info = ele.info
            return self.result.set(data=info)
        except Exception as e:
            return self.result.set(code=400, status=False, message=f"获取元素info失败,{e}")

    def exists(self, tag, selector, index):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            ele = self.find_element(tag, selector, index, wait=True)
            if tag == 'xpath':
                if ele:
                    return self.result.set(message='元素存在')
                else:
                    return self.result.set(status=False, message='元素不存在')
            else:
                if ele.count > 0:
                    return self.result.set(message='元素存在')
                else:
                    return self.result.set(status=False, message='元素不存在')
        except Exception as e:
            print(e)
            return self.result.set(code=400, status=False, message="判断元素是否存在方法出错" + str(e))

    def get_text(self, tag, selector, index):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            result = self.find_element(tag, selector, index).text
            return self.result.set(data=result)
        except Exception as e:
            print(e)
            return self.result.set(code=400, status=False, message=f"获取元素文本出错,{e}")

    def get_toast(self):

        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            toast = self.device.toast.get_message(timout=5, default='no toast')
            return self.result.set(data=toast)
        except Exception as e:
            print(e)
            return self.result.set(code=400, status=False, message="获取toast方法出错")

    def drag_to(self, source_tag, source_selector, target_x, target_y, index):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.find_element(source_tag, source_selector, index).drag_to(target_x, target_y, duration=0.25)
            return self.result.set(message="拖拽元素成功")
        except Exception as e:
            print(e)
            return self.result.set(code=400, status=False, message=f"拖拽元素失败,{e}")

    def pinch_in(self, tag, selector, index):
        """元素缩小"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.find_element(tag, selector, index).pinch_in()
            return self.result.set(message=f"元素{tag}-{selector}缩小成功")
        except Exception as e:
            print(e)
            return self.result.set(code=400, status=False, message=f"元素{tag}-{selector}缩小失败,{e}")

    def pinch_out(self, tag, selector, index):
        """元素放大"""
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            self.find_element(tag, selector, index).pinch_out()
            return self.result.set(message=f"元素{tag}-{selector}放大成功")
        except Exception as e:
            print(e)
            return self.result.set(code=400, status=False, message=f"元素{tag}-{selector}放大失败,{e}")

    def assertTextin(self, text, tag, selector, index):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            if text in self.find_element(tag, selector, index).text:
                return self.result.set(message=f"{text} 在 元素中")
            else:
                return self.result.set(message=f"{text} 不在 元素中", status=False, code=400)

        except Exception as e:
            print(e)
            return self.result.set(code=400, status=False, message=f"断言方法出错,{e}")

    def assertTextNotin(self, text, tag, selector, index):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            if text not in self.find_element(tag, selector, index).text:
                return self.result.set(message=f"{text} 不在 元素中")
            else:
                return self.result.set(message=f"{text} 在 元素中", status=False, code=400)

        except Exception as e:
            print(e)
            return self.result.set(code=400, status=False, message=f"assertTextNotin断言方法出错,{e}")

    def screen_shot(self, name=None):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            if name is None:
                image_name = time.time()
            else:
                image_name = str(name) + str(time.time())
            file = os.getcwd() + "/image.temp/{}.png".format(image_name)
            remote = "http://{0}:8081/api/common/image?image_id={1}".format(ip_util.get_ip(), image_name)
            self.device.screenshot(file)
            return self.result.set(data={'remote': remote, 'file_path': file})
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def adb_shell(self, cmd):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            output, exit_code = self.device.shell(cmd, timeout=5)
            return self.result.set(data={'output': output, "exit_code": exit_code})
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def switch_webdriver(self, webdriver_version, device_ip=None):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")
        try:
            driver = ChromeDriver(self.device).driver(webdriver_version=webdriver_version, device_ip=device_ip)
            self.driver = driver
            return self.result.set(data=True, message='切换driver成功')
        except Exception as err:
            return self.result.set(code=400, status=False, message='切换driver失败' + str(err))

    def webview_get_handles(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            handles = self.driver.window_handles
            return self.result.set(data=handles, message='获取handles成功')

        except Exception as err:
            return self.result.set(code=400, status=False, message='切换driver失败' + str(err))

    def webview_find_elements(self, tag, element):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        ele_list = []
        if tag == 'id':
            ele_list = self.driver.find_elements(by='id', value=element)

        elif tag == 'xpath':
            ele_list = self.driver.find_elements(by='xpath', value=element)

        elif tag == 'css':
            ele_list = self.driver.find_elements(by='css selector', value=element)
        return ele_list

    def webview_find_element(self, tag, element, timeout=30, index=0):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        for i in range(int(timeout)):
            if elements := self.webview_find_elements(tag, element):
                return elements[int(index)]
            time.sleep(1)
            print(f'find-element 暂停1秒-【{tag}】-【{element}】')
        else:
            raise Exception('元素等待超时....')

    def webview_click(self, tag, element, timeout, index):
        try:
            ele = self.webview_find_element(tag, element, timeout, index)
            ele.click()
            return self.result.set(f'点击元素【{tag}-{element}】成功')
        except Exception as e:
            return self.result.set(f'点击元素【{tag}-{element}】失败：{e}', status=False)

    def webview_loop_wait_element_exist(self, tag, element, timeout: int):
        """循环等待元素存在"""
        for i in range(timeout):
            elements = self.webview_find_elements(tag, element)
            if elements:
                return self.result.set(status=True, data={f'元素{tag}-{element}存在'})
            time.sleep(1)
        else:
            return self.result.set(status=False, data=f'元素{tag}-{element}不存在')

    def webview_loop_wait_element_not_exist(self, tag, element, timeout: int):
        """循环等待元素不存在"""
        for i in range(timeout):
            elements = self.webview_find_elements(tag, element)
            if not elements:
                return self.result.set(status=True, data={f'元素{tag}-{element}不存在'})
            time.sleep(1)
        else:
            return self.result.set(status=False, data=f'元素{tag}-{element}存在')

    def webview_send_keys(self, tag, element, value, timeout, index):
        try:
            ele = self.webview_find_element(tag, element, timeout, index)
            ele.send_keys(value)
            return self.result.set(f'元素输入【{tag}-{element}】成功')
        except Exception as e:
            return DataFormat().set(f'元素输入【{tag}-{element}】失败：{e}', status=False)

    def webview_get_attribute(self, tag, element, attribute_name, timeout, index):
        try:
            ele = self.webview_find_element(tag, element, timeout, index)
            value = ele.get_attribute(attribute_name)
            return self.result.set(f'元素元素属性：{attribute_name}成功', data=value)
        except Exception as e:
            return self.result.set(f'元素元素属性：{attribute_name}失败：{e}', status=False)

    def webview_switch_handle(self, window_title, _type='equal'):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            handles = self.driver.window_handles
            print("handles:", handles)
            if len(handles) <= 1:
                return self.result.set(message='当前只有一个window-handle')
            else:
                for handle in handles:
                    self.driver.switch_to.window(handle)
                    title = self.driver.title
                    print(f"handles::{handle}--{title}")
                    if _type == 'equal':
                        if window_title == title:
                            return self.result.set(message=f'切换至{handle},handle_name:{title}', data=handles)
                    else:
                        if title and window_title != title:
                            return self.result.set(message=f'切换至{handle},handle_name:{title}', data=handles)
                else:
                    return self.result.set(message=f'轮询完所有handle，未发现匹配，切换至{handle},handle_name:{title}', data=handles)

        except Exception as e:
            return DataFormat().set(message=f'切换handle失败，失败原因 {e}]')

    def element_screenshot(self, tag, element, timeout, name=None, index=0):
        ele = self.webview_find_element(tag, element, timeout, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            now_t = time.time()

            if name:
                image_name = name
            else:
                image_name = now_t
            file = os.getcwd() + "/image.temp/{}.png".format(image_name)
            remote = "http://{0}:8081/api/common/image?image_id={1}".format(ip_util.get_ip(), image_name)
            ele.screenshot(file)
            return self.result.set(data={'remote': remote, 'file_path': file})
        except Exception as e:
            return self.result.set(f'截图失败：{e}', status=False, data=False)

    def webview_refresh(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            self.driver.refresh()
            return self.result.set(message='刷新页面成功')

        except Exception as e:
            return self.result.set(message=f'刷新页面失败：{e}', status=False, data=False)

    def webview_execute_js(self, js_code):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            result = self.driver.execute_script(js_code)
            return self.result.set(message=f'执行js：{js_code}成功', data=result)

        except Exception as e:
            return self.result.set(message=f'执行js失败：{e}', status=False, data=False)

    def webview_delete_all_cookies(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            self.driver.delete_all_cookies()
            return self.result.set(message=f'清除cookie成功')

        except Exception as e:
            return self.result.set(message=f'清除cookie失败：{e}', status=False, data=False)

    def webview_get_elements_num(self, tag, element, delay):
        try:
            if delay:
                time.sleep(int(delay))
            elements = self.webview_find_elements(tag, element)
            return self.result.set(message=f'获取元素个数成功', data=len(elements))

        except Exception as e:
            return self.result.set(message=f'获取元素个数失败：{e}', status=False, data=False)

    def webview_get_element_size(self, tag, element, timeout, index):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            ele = self.webview_find_element(tag, element, timeout, index)
            size = ele.size
            return self.result.set(message=f'获取元素尺寸成功', data=size)

        except Exception as e:
            return self.result.set(message=f'获取元素尺寸失败：{e}', status=False, data=False)

    def webview_drop_element_by_offset(self, tag, element, timeout, index, x_offset, y_offset=0):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            ele = self.webview_find_element(tag, element, timeout, index)
            action = ActionChains(self.driver)
            action.click_and_hold(ele).perform()
            action.drag_and_drop_by_offset(ele, x_offset, y_offset).perform()

            return self.result.set(message=f'拖拽成功')

        except Exception as e:
            return self.result.set(message=f'拖拽元素失败：{e}', status=False, data=False)

    def webview_get_current_handle(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            current_handle = self.driver.current_window_handle

            return self.result.set(data=current_handle)
        except Exception as e:
            return self.result.set(message=f'获取当前handles失败：{e}', status=False, data=False)

    def webview_get_current_title(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            current_title = self.driver.title

            return self.result.set(data=current_title)
        except Exception as e:
            return self.result.set(message=f'获取当前title失败：{e}', status=False, data=False)

    def webview_get_page_source(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            current_page_source = self.driver.page_source

            return self.result.set(data=current_page_source)
        except Exception as e:
            return self.result.set(message=f'获取current_page_source失败：{e}', status=False, data=False)

    def webview_get_current_url(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            current_url = self.driver.current_url

            return self.result.set(data=current_url)
        except Exception as e:
            return self.result.set(message=f'获取当前url失败：{e}', status=False, data=False)

    def webview_switch_to_iframe(self, tag, element, timeout, index):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            ele = self.webview_find_element(tag, element, timeout, index)
            self.driver.switch_to.frame(ele)
            return self.result.set(data=True)
        except Exception as e:
            return self.result.set(message=f'切换iframe失败：{e}', status=False, data=False)

    def webview_switch_to_default_content(self):
        if not self._devices_is_connected():
            return self.result.set(code=500, status=False, message="未连接上设备")

        if not self.driver:
            return self.result.set(code=500, status=False, message="未切换至webview")

        try:
            self.driver.switch_to.default_content()
            return self.result.set(data=True)
        except Exception as e:
            return self.result.set(message=f'切换iframe回主文档失败：{e}', status=False, data=False)


if __name__ == '__main__':
    a = AndroidAgent()
    print(a.connect())
    print(a.current_package_name())
