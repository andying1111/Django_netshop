import csv
import gzip
import json
import os
import platform
import subprocess
import time

import xlrd2
from selenium import webdriver  # web自动化库
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains  # 模拟事件
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from seleniumwire import webdriver as webdriverwire

from polyv.common import ip_util
from polyv.common.data_format import DataFormat
from polyv.common.file_util import ImageCompare
from polyv.common.png_quant import compress_picture
from polyv.common.webdriver_manage_extend import ChromeDriverManager
from polyv.scripts.web_interceptor import SDKInterceptor
from settings import ROOT_PATH


class WebBrowser:

    def __init__(self, mobile, size=None, use_interceptor=False, virtual_camera=False):
        """本地启动Chrome浏览器"""
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        if use_interceptor:
            # 使用拦截器
            self.driver = webdriverwire.Chrome(ChromeDriverManager().install(),
                                               options=self.chrome_options(mobile, virtual_camera),
                                               desired_capabilities=capabilities)
        else:
            # 不使用拦截器
            self.driver = webdriver.Chrome(ChromeDriverManager().install(),
                                           options=self.chrome_options(mobile, virtual_camera),
                                           desired_capabilities=capabilities)

        if mobile == False:
            self.driver.maximize_window()
        if size[0] and size[1]:
            self.driver.set_window_size(width=size[0], height=size[1])

    @staticmethod
    def chrome_options(mobile, virtual_camera):
        """
        配置chromedriver
        :return:
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--use-fake-ui-for-media-stream=1")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('ignore-certificate-errors')
        options.add_argument('--disable-popup-blocking')

        options.add_experimental_option("prefs", {"profile.default_content_setting_values.media_stream_mic": 1,
                                                  # 1:allow, 2:block
                                                  "profile.default_content_setting_values.media_stream_camera": 1,
                                                  # 1:allow, 2:block
                                                  "profile.default_content_setting_values.geolocation": 1,
                                                  # 1:allow, 2:block
                                                  "profile.default_content_setting_values.notifications": 1,
                                                  # 1:allow, 2:block
                                                  "profile.default_content_settings.popups": 0,

                                                  "download.default_directory": os.path.abspath(f'./downloads/'),
                                                  "credentials_enable_service": False,
                                                  "profile.password_manager_enabled": False
                                                  },

                                        )
        options.add_experimental_option('perfLoggingPrefs', {'enableNetwork': True})

        if virtual_camera:
            # 为媒体流使用假设备来替换实际的摄像头和麦克风
            options.add_argument('--use-fake-device-for-media-stream')
            # 通过选择媒体流的默认设备（例如 WebRTC）绕过媒体流信息栏。与 --use-fake-device-for-media-stream 一起使用。
            options.add_argument('--use-fake-ui-for-media-stream')
            options.add_argument("--no-sandbox")
            options.add_argument(f'--use-file-for-fake-audio-capture={ROOT_PATH}/0.wav')
            options.add_argument(f'--use-file-for-fake-video-capture={ROOT_PATH}/0.y4m')

        if mobile:
            if isinstance(mobile, dict):
                options.add_experimental_option("mobileEmulation", mobile)
            else:
                raise TypeError("参数`mobile` 必须是字典格式")
        # 解决Passthrough is not supported, GL is swiftshader无效报错信息
        """
        -enable-webgl --no-sandbox --disable-dev-shm-usage
        """
        # options.add_argument("--headless") 无头浏览器
        options.add_argument("--enable-webgl")
        return options


class WebDriverAgent:
    """
    Web浏览器UI自动化库
    """
    driver = None
    driver_session_set = set()
    alias_and_driver_session_dict = {}
    alias_pointer = ""
    GLOBAL_IMPLICITY_WAIT_TIME = 5.0
    GLOBAL_FIND_TOLERANCE = 15
    GLOBAL_FIND_STEP_TIME = 1
    GLOBAL_FIND_ELEMENT_NUMBER = 0
    GlOBAL_MAX_LOADING_URL_TIME = 30
    mobile_setting = {"deviceName": "iPhone X"}
    result = DataFormat()
    interceptor = SDKInterceptor()

    @staticmethod
    def cmd(command):
        """执行cmd命令"""
        print(command)
        return subprocess.run(command,
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              encoding="utf-8",
                              timeout=300).stdout

    def new_browser(self, definition_driver_alias, mobile=False, width=0, height=0, use_interceptor=False,
                    virtual_camera=False):
        """新开一个浏览器, 绑定到入参的alias"""
        try:
            driver_alias = str(definition_driver_alias)
            if driver_alias not in list(self.alias_and_driver_session_dict.keys()):
                mobile_emu_setting, is_enable_mobile_phone_mode = self.mobile_emu_parameter_analysis(mobile)
                self.driver = WebBrowser(mobile=mobile_emu_setting, size=(int(width), int(height)),
                                         use_interceptor=use_interceptor, virtual_camera=virtual_camera).driver
                if use_interceptor:
                    self.driver.request_interceptor = self.interceptor.sdk_interceptor
                session_id = self.driver.session_id
                self.driver_session_set.add(session_id)
                self.alias_and_driver_session_dict[driver_alias] = self.driver
                self.alias_pointer = driver_alias

                return self.result.set(message="浏览器新建成功",
                                       data=f"alias=[{driver_alias}] | session_id=[{session_id}] | is_mobile_mode=[{is_enable_mobile_phone_mode}] | is_virtual_camera=[{virtual_camera}]")

            return self.result.set(
                message=f"昵称为{driver_alias}的浏览器已存在| session_id=[{self.alias_and_driver_session_dict[driver_alias].session_id}]",
                data=False)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def switch_driver_cursor_by_alias(self, alias):
        """根据alias查询driver对象，针对多浏览器的场景使用"""
        if len(self.alias_and_driver_session_dict) != 0:
            if alias:
                driver = self.alias_and_driver_session_dict.get(str(alias))
                if driver:
                    # 更新指针
                    self.alias_pointer = alias
                    return driver
                else:
                    raise Exception(f"切换浏览器失败，该昵称的浏览器{alias}已不存在")
            else:
                # 当alias=None时：默认返回指针指向的那个driver
                return self.alias_and_driver_session_dict.get(self.alias_pointer)
        else:
            raise Exception("当前运行时没有浏览器，请参考接口 `api/web/new_browser` 创建.")

    @staticmethod
    def is_index_isinstance_int(index):
        if isinstance(index, str):
            try:
                return int(index)

            except Exception:
                raise TypeError(f"index={index}参数必须是整数")

        elif isinstance(index, int):
            return index

        else:
            raise TypeError(f"index={index}参数必须是整数")

    def is_exist_the_alias(self, alias):
        if alias:
            if str(alias) in list(self.alias_and_driver_session_dict.keys()):
                return True
            else:
                return False
        else:
            # alias=None时，返回True，由switch_driver_cursor_by_alias处理
            return True

    def mobile_emu_parameter_analysis(self, mobile):
        if mobile == False:
            return False, False
        elif isinstance(mobile, str):
            if mobile.capitalize() == "True":
                return self.mobile_setting, True
            elif mobile.capitalize() == "False":
                return False, False
            else:
                mobile_dict = json.loads(mobile)
                return mobile_dict, True
        else:
            raise TypeError(f"mobile={mobile}参数必须是字典")

    def check_the_running_browser(self):
        return self.result.set(data=list(self.alias_and_driver_session_dict.keys()),
                               message=f"当前运行时浏览器格式是  {len(self.driver_session_set)}")

    def automatically_drag_the_slider(self, alias, element_id):
        drag_the_slider_example_code = """
			function polyv_auto_verify() {
				var polyv_slider_button_id = "%s";

				var btn = document.getElementById(polyv_slider_button_id);
				var mousedown = document.createEvent("MouseEvents");
				var rect = btn.getBoundingClientRect();
				var x = rect.x;
				var y = rect.y;
				mousedown.initMouseEvent("mousedown", true, true, window, 0, x, y, x, y, false, false, false, false, 0, null);
				btn.dispatchEvent(mousedown);

				var dx = 0;
				var dy = 0;
				var interval = setInterval(function() {
					var mousemove = document.createEvent("MouseEvents");
					var _x = x + dx;
					var _y = y + dy;
					mousemove.initMouseEvent("mousemove", true, true, window, 0, _x, _y, _x, _y, false, false, false, false, 0, null);
					btn.dispatchEvent(mousemove);

					if (_x - x >= 304) {
						clearInterval(interval);
						var mouseup = document.createEvent("MouseEvents");
						mouseup.initMouseEvent("mouseup", true, true, window, 0, _x, _y, _x, _y, false, false, false, false, 0, null);
						btn.dispatchEvent(mouseup);

						setTimeout(function() {
							if (btn.className.indexOf("icon-ok") > -1) {
								console.log(btn.className);
							}
						},
						1000);
					} else {
						dx += Math.ceil(Math.random() * 50);
					}
				},
				30);
			};
			polyv_auto_verify();
		""" % element_id

        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                # print(drag_the_slider_example_code)
                result = driver.execute_script(drag_the_slider_example_code)
                return self.result.set(data=result, message="Execute successfully.")
            else:
                return self.result.set(code=404, status=False,
                                       message="No driver is Enabled! >>>Your parameters:`alias=[{}]`".format(alias))
        except Exception as err:
            return self.result.set(code=400, status=False, message="Execute JavaScript Code Error !" + str(err))

    def execute_js(self, alias, js_code, async_mode=False):
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                if isinstance(async_mode, bool):
                    if async_mode == False:
                        result = driver.execute_script(js_code)
                    else:
                        result = driver.execute_async_script(js_code)
                elif isinstance(async_mode, str):
                    if async_mode.capitalize() == "False":
                        result = driver.execute_script(js_code)
                    elif async_mode.capitalize() == "True":
                        result = driver.execute_async_script(js_code)
                    else:
                        raise TypeError(
                            "args `async_mode=[{}]` is not supported ! Must be a Boolean Type".format(async_mode))
                else:
                    raise TypeError(
                        "args `async_mode=[{}]` is not supported ! Must be a Boolean Type".format(async_mode))

                return self.result.set(data=result, message="Execute successfully.")
            else:
                return self.result.set(code=404, status=False,
                                       message="No driver is Enabled! >>>Your parameters:`alias=[{}]`".format(alias))
        except Exception as err:
            return self.result.set(code=400, status=False, message="Execute JavaScript Code Error !" + str(err))

    def close(self, alias):
        """关闭当前标签页"""
        try:
            if self.is_exist_the_alias(alias):
                # 如果当前浏览器仅开了1个tab，close之后删掉该浏览器的session和driver记录
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.close()
                if len(driver.window_handles) == 0:
                    self.alias_and_driver_session_dict.pop(alias)
                    self.driver_session_set.remove(driver.session_id)
                    self.alias_pointer = ""
                return self.result.set(message="Current tab is Closed.", data="ID=[{}]".format(id(self.driver)))
            else:
                return self.result.set(code=404, status=False,
                                       message="No driver is Enabled! >>>Your parameters:`alias=[{}]`".format(alias))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def quit(self, alias):
        """关闭全部标签页并退出driver"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.quit()
                self.alias_and_driver_session_dict.pop(alias)
                self.driver_session_set.remove(driver.session_id)
                self.alias_pointer = ""
                return self.result.set(message="Browser is quitted.", data="alias=[{}]".format(alias))
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to Quit! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                                           alias), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def get_window_position(self, alias):
        """获取浏览器窗口位置"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                position = driver.get_window_position()
                return self.result.set(data={"width": position.get("x"), "height": position.get("y")})
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to Quit! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                                           alias), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def set_window_position(self, alias, x, y):
        """设置浏览器窗口位置"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                position = driver.set_window_position(x, y)
                return self.result.set(message='set position success',
                                       data={"width": position.get("x"), "height": position.get("y")})
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to Quit! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                                           alias), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def get_window_size(self, alias):
        """获取浏览器窗口位置"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                size = driver.get_window_size()
                return self.result.set(data=size)
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to Quit! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                                           alias), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def quit_all_browser(self):
        try:
            if len(self.alias_and_driver_session_dict) != 0:
                for _alias in self.alias_and_driver_session_dict.keys():
                    self.driver_session_set.remove(self.switch_driver_cursor_by_alias(_alias).session_id)
                    self.switch_driver_cursor_by_alias(_alias).quit()
                self.alias_and_driver_session_dict.clear()
                self.alias_pointer = ""
                return self.result.set(message="All Browser is quitted.",
                                       data=list(self.alias_and_driver_session_dict.keys()), status=True)
            else:
                return self.result.set(message="There are currently no surviving Alias and Browser Objects ~",
                                       data=list(self.alias_and_driver_session_dict.keys()), status=True)
        except Exception as err:
            return self.result.set(code=402, status=True, message="`quit_all_browser` executed Error !" + str(err),
                                   data="The remaining Alias List={}".format(
                                       list(self.alias_and_driver_session_dict.keys())))

    def open_url(self, alias, url):
        """打开url"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                # url中带有参数需要替换,特殊处理
                url = url.replace("~", "&")
                driver.get(url)

                times = int(self.GlOBAL_MAX_LOADING_URL_TIME / self.GLOBAL_FIND_STEP_TIME)  # 最大重试次数
                while times:
                    Non_blocking = None
                    try:
                        if driver.switch_to.alert:
                            # log.info('Check alert text is {}'.format(self.driver.switch_to.alert.text))
                            Non_blocking = False
                            # 如果alert弹窗需要点击确定或关闭
                            driver.switch_to.alert.accept()
                            driver.switch_to.alert.dismiss()
                    except Exception as e:
                        # log.info('Error info =={}'.format(e))
                        Non_blocking = True
                    if Non_blocking:
                        if driver.execute_script("return document.readyState;") == "complete":
                            # 页面的dom部分已加载完成（不含ajax），跳出智能判断
                            break
                        else:
                            # log.info('Page Loading, wait {} S. The {} time'.format(get_ready_state_step_time, times))
                            time.sleep(self.GLOBAL_FIND_STEP_TIME)
                    times -= 1
                assert times > 0, "Error! URL cannot be opened."

                urls = []
                for log in driver.get_log('performance'):
                    if 'message' not in log:
                        continue
                    log_entry = json.loads(log['message'])
                    try:
                        # 该处过滤了data:开头的base64编码引用和document页面链接
                        if "data:" not in log_entry['message']['params']['request']['url'] and 'Document' not in \
                                log_entry['message']['params']['type']:
                            urls.append(log_entry['message']['params']['request']['url'])
                    except Exception as e:
                        pass

                return self.result.set(message="Open url successfully.",
                                       data=urls)
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable open URL! This alias no corresponding to driver. >>>Your parameters:`alias=[{}], url=[{}]`".format(
                                           alias, url), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Open URL Error ! >>>args `url=[{}]`".format(url) + str(err))

    def refresh(self, alias):
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.refresh()
                return self.result.set(status=True, message="The page refresh successfully.",
                                       data=True)
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to refresh ! >>>Your parameters: `alias=[{}]`".format(alias))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def window_to_max(self, alias):
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.maximize_window()
                return self.result.set(status=True, message="The page window to MAX successfully.",
                                       data=True)
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to max_window ! >>>Your parameters: `alias=[{}]`".format(alias))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def window_to_min(self, alias):
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.minimize_window()
                return self.result.set(status=True, message="The page window to MIN successfully.",
                                       data=True)
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to min_window ! >>>Your parameters: `alias=[{}]`".format(alias))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def clear_input_box(self, alias, tag='xpath', element='', index=0):
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            ele.send_keys(Keys.CONTROL, "a")
            time.sleep(self.GLOBAL_FIND_STEP_TIME)
            ele.send_keys(Keys.DELETE)
            return self.result.set(message="Clear the input box successfully.")

        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Clear input box Error ! >>>args `tag=[{}], element=[{}]`".format(tag,
                                                                                                             element) + str(
                                       err))

    def get_this_tab_title(self, alias):
        """获取当前标签页的标题"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                title = driver.title
                return self.result.set(data=title, message="Get title successfully.")
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to find the driver corresponding to alias! >>>Your parameters: `alias=[{}]`".format(
                                           self.alias_pointer), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Get title Error ! >>>args `alias=[{}]`".format(self.alias_pointer) + str(
                                       err))

    def get_current_url(self, alias):
        """获取当前url"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                url = driver.current_url
                return self.result.set(data=url, message="Get url successfully.")
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to find the driver corresponding to alias! >>>Your parameters: `alias=[{}]`".format(
                                           self.alias_pointer), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Get url Error ! >>>args `alias=[{}]`".format(self.alias_pointer) + str(
                                       err))

    def elementexist(self, alias, tag='xpath', element='', index=0, timeout=GLOBAL_FIND_TOLERANCE):
        try:
            if self.find(alias, tag, element, index, timeout=timeout):
                return self.result.set(data=True, message="The element is existed.")
            else:
                return self.result.set(data=False, message="The element is not existed!")
        except NoSuchElementException as e:
            return self.result.set(code=400, status=False,
                                   message="Check element exist Error ! >>>args `tag=[{}], element=[{}]`".format(tag,
                                                                                                                 element) + str(
                                       e))

    def is_this_element_enabled(self, alias, tag='text', element='', index=0):
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            if ele.is_enabled():
                return self.result.set(data=True, message="The element is enabled.")
            else:
                return self.result.set(data=False, message="The element is not enabled!")
        except NoSuchElementException as e:
            return self.result.set(code=400, status=False,
                                   message="Check element enabled Error ! >>>args `tag=[{}], element=[{}]`".format(tag,
                                                                                                                   element) + str(
                                       e))

    def is_this_element_displayed(self, alias, tag='text', element='', index=0):
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            if ele.is_displayed():
                return self.result.set(data=True, message="The element is displayed.")
            else:
                return self.result.set(data=False, message="The element is not displayed!")
        except NoSuchElementException as e:
            return self.result.set(code=400, status=False,
                                   message="Check element displayed Error ! >>>args `tag=[{}], element=[{}]`".format(
                                       tag, element) + str(e))

    def is_this_element_selected(self, alias, tag='text', element='', index=0):
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            if ele.is_selected():
                return self.result.set(data=True, message="The element is selected.")
            else:
                return self.result.set(data=False, message="The element is not selected!")
        except NoSuchElementException as e:
            return self.result.set(code=400, status=False, message=str(e))

    def screen_shot(self, alias, name=None):
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                now_t = time.time()
                if alias is None:
                    # alias = list(self.alias_and_driver_session_dict.keys())[0]
                    alias = self.alias_pointer
                if name:
                    image_name = name
                else:
                    image_name = now_t

                # images_path = f"/image.temp/{image_name}.png" if platform.system() != "Windows" else f'\\image.temp\\{image_name}.png'

                file = os.path.join(ROOT_PATH, "image.temp", f"{image_name}.png")
                remote = "http://{0}:8081/api/common/image?image_id={1}".format(ip_util.get_ip(), image_name)
                driver.get_screenshot_as_file(file)
                try:
                    compress_picture(file)
                    print(f"压缩{file}成功！")
                except Exception as e:
                    print(e)
                return self.result.set(data={'remote': remote, 'file_path': file},
                                       message="Screenshot belongs to `alias=[{}]` .".format(alias))
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to ScreenShot! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                                           alias), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Screenshot Error ! >>>args `alias=[{}]`".format(alias) + str(err))

    def get_screenshot_as_base64(self, alias):
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                if alias is None:
                    alias = self.alias_pointer
                return self.result.set(data=driver.get_screenshot_as_base64(),
                                       message="Screenshot belongs to `alias=[{}]` .".format(alias))
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to ScreenShot! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                                           alias), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Screenshot Error ! >>>args `alias=[{}]`".format(alias) + str(err))

    def element_screenshot(self, alias, tag='text', element='', name=None, index=0):
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            now_t = time.time()
            if alias is None:
                # alias = list(self.alias_and_driver_session_dict.keys())[0]
                alias = self.alias_pointer
            if name:
                image_name = "-".join([alias, str(name)])
            else:
                image_name = "-".join([alias, str(now_t)])
            file = os.getcwd() + "/image.temp/{}.png".format(image_name)
            remote = "http://{0}:8081/api/common/image?image_id={1}".format(ip_util.get_ip(), image_name)
            ele.screenshot(file)
            return self.result.set(data={'remote': remote, 'file_path': file},
                                   message="Element-Screenshot belongs to `alias=[{}]` .".format(alias))
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Element-Screenshot Error ! >>>args `tag=[{}], element=[{}]`".format(tag,
                                                                                                                element) + str(
                                       err))

    def set_global_find_tolerance(self, customer_tolerance, customer_step_time):
        self.GLOBAL_FIND_TOLERANCE = int(customer_tolerance)
        self.GLOBAL_FIND_STEP_TIME = float(customer_step_time)
        return self.result.set(
            message="Successfully. Set GLOBAL_FIND_TOLERANCE = [{}] Times; GLOBAL_FIND_STEP_TIME = [{}] Seconds.".format(
                self.GLOBAL_FIND_TOLERANCE, self.GLOBAL_FIND_STEP_TIME), data=True, status=True)

    def show_element(self, element):
        """高亮显示当前操作的元素，暂时没用上"""
        style_red = 'arguments[0].style.border="2px solid #FF0000"'
        style_blue = 'arguments[0].style.border="2px solid #00FF00"'
        style_null = 'arguments[0].style.border=""'

        for _ in range(2):
            self.driver.execute_script(style_blue, element)
            time.sleep(0.1)
            self.driver.execute_script(style_red, element)
            time.sleep(0.1)
        self.driver.execute_script(style_blue, element)
        time.sleep(0.1)
        self.driver.execute_script(style_null, element)

    def find(self, alias, tag='text', element='', index=0, timeout=GLOBAL_FIND_TOLERANCE):
        """
        通用定位
        :param tag: 元素类型
        :param element: 元素属性
        :return:
        """
        for _ in range(int(timeout)):
            elements = self.finds(tag=tag, element=element, alias=alias)
            if elements:
                print(f"已找到元素：tag={tag},element={element}")
                return elements[int(index)]
            print(f"暂时未找到元素:tag={tag},element={element}：暂停{self.GLOBAL_FIND_STEP_TIME} s")
            time.sleep(self.GLOBAL_FIND_STEP_TIME)
        else:
            return

    def finds(self, tag, alias, element=''):
        """
        通用定位
        :param index: 索引, 默认取第一个
        :param tag: 元素类型
        :param element: 元素属性
        :return:
        """

        def clever_inference_calculation_of_text(_driver, _element):
            match_list = ["//*[@placeholder='{}']", "//*[@value='{}']", "//*[text()='{}']", ]
            # no_ele = _element.replace(" ", "")
            for m in match_list:
                _result = _driver.find_elements_by_xpath(m.format(_element))
                if _result:
                    print("finds智能匹配成功>>> %s" % m.format(_element))
                    return _result

        if self.is_exist_the_alias(alias):
            driver = self.switch_driver_cursor_by_alias(alias)
            if tag.lower() == 'id':
                e_list = driver.find_elements_by_id(element)
            elif tag == 'xpath':
                e_list = driver.find_elements_by_xpath(element)
            elif tag == 'name':
                e_list = driver.find_elements_by_name(element)
            elif tag == 'text':
                e_list = clever_inference_calculation_of_text(driver, element)
            elif tag == 'classname':
                e_list = driver.find_elements_by_class_name(element)
            elif tag == 'tagname':
                e_list = driver.find_elements_by_tag_name(element)
            elif tag == 'linktext':
                e_list = driver.find_elements_by_link_text(element)
            elif tag == 'css':
                e_list = driver.find_elements_by_css_selector(element)
            else:
                raise TypeError(
                    "Error! Find of [tag={}] type is not supported ! Please refer to the following types [id|xpath|name|text|classname|tagname|linktext|css]".format(
                        tag))

            return e_list
        else:
            raise Exception(
                "Unable finds! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(alias))

    def click(self, alias, tag='text', element='', index=0):
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            driver = self.switch_driver_cursor_by_alias(alias)
            ele.click()
            return self.result.set(data='Click successfully.')
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Click Error ! >>>args `tag=[{}], element=[{}]`".format(tag, element) + str(
                                       err))

    def move_to_element(self, alias, tag='text', element='', index=0):
        """移动鼠标焦点"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            driver = self.switch_driver_cursor_by_alias(alias)
            ActionChains(driver).move_to_element(ele).perform()
            return self.result.set(data='Move to [{}] successfully.'.format(element))

        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Move to element Error ! >>>args `tag=[{}], element=[{}]`".format(tag,
                                                                                                             element) + str(
                                       err))

    def scroll_to_element(self, alias, tag='text', element='', index=0):
        """滑动页面到对应元素"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            driver = self.switch_driver_cursor_by_alias(alias)
            driver.execute_script("arguments[0].scrollIntoView();", ele)
            return self.result.set(data='scroll to [{}] successfully.'.format(element))

        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="scroll to element Error ! >>>args `tag=[{}], element=[{}]`".format(tag,
                                                                                                             element) + str(
                                       err))

    def drop_element_by_offset(self, alias, x_offset, y_offset=0, tag='text', element='', index=0):
        """拖拽鼠标元素"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到,请检查 tag=[{}], element=[{}]".format(tag, element))
        try:
            driver = self.switch_driver_cursor_by_alias(alias)
            action = ActionChains(driver)
            action.click_and_hold(ele).perform()
            action.drag_and_drop_by_offset(ele, x_offset, y_offset).perform()

            return self.result.set(data='drop_element_by_offset successfully.')

        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="drop_element_by_offset fail" + str(err))

    def input(self, alias, tag='text', element='', value='', is_clear=True, index=0):
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            if is_clear:
                if platform.system().lower() == "darwin":
                    ele.send_keys(Keys.COMMAND, "a")
                else:
                    ele.send_keys(Keys.CONTROL, "a")
                ele.send_keys(Keys.DELETE)
                time.sleep(self.GLOBAL_FIND_STEP_TIME)
            ele.send_keys(value)
            return self.result.set(status=True, message='Input successfully.')
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Input Error ! >>>args `tag=[{}], element=[{}]`".format(tag, element) + str(
                                       err))

    def upload_file(self, alias, tag='text', element='', file_name='test1.jpg', file_path='./resources/', index=0):
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            file = os.path.abspath(f'{file_path}{file_name}')
            ele.send_keys(file)
            return self.result.set(status=True, message='上传成功 successfully.')
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message="Input Error ! >>>args `tag=[{}], element=[{}]`".format(tag, element) + str(
                                       err))

    def parse_xlsx_sheet(self, xlsx_name, sheet_name):
        file = os.path.abspath(f'./downloads/{xlsx_name}')
        if not xlsx_name:
            return self.result.set(code=400, status=False, message=f"未找到 [{xlsx_name}] 文件")
        if not sheet_name:
            return self.result.set(code=400, status=False, message=f"文件 [{xlsx_name}] 未找到 [{sheet_name}] sheet表")
        try:
            sh = xlrd2.open_workbook(file).sheet_by_name(sheet_name)
            row_datas = []
            for i in range(sh.nrows):
                row_datas.append(sh.row_values(i))
            return self.result.set(status=True,
                                   message=f'解析xlsx文件 xlsx_name=[{xlsx_name}] 的 sheet_name=[{sheet_name}] sheet表成功： successfully.',
                                   data={'rows_num': sh.nrows, 'cols_num': sh.ncols, 'row_datas': row_datas})
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message=f"Parse xlsx Error ! >>>args `xlsx_name=[{xlsx_name}], sheet_name=[{sheet_name}]`" + str(
                                       err))

    def web_un_gz(self, gz_file_name):
        if not gz_file_name.endswith('.gz'):
            return self.result.set(code=400, status=False, message=f"文件 [{gz_file_name}] 需以.gz结尾")
        try:
            g_file = gzip.GzipFile(os.path.abspath(f'./downloads/{gz_file_name}'))

            file_name = gz_file_name.replace('.gz', '')
            open(os.path.abspath(f'./downloads/{file_name}'), "wb+").write(g_file.read())

            g_file.close()
            return self.result.set(status=True,
                                   message=f'解压 gz_file_name=[{gz_file_name}] 为[{file_name}]成功： successfully.',
                                   data={'file_name': file_name})
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message=f"web_un_gz Error ! >>>args `gz_file_name=[{gz_file_name}]`" + str(
                                       err))

    def parse_csv(self, csv_file_name):
        if not csv_file_name.endswith('.csv'):
            return self.result.set(code=400, status=False, message=f"文件 [{csv_file_name}] 需以.csv结尾")
        try:
            with open(os.path.abspath(f'./downloads/{csv_file_name}'), 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                row_datas = [row for row in reader]

            return self.result.set(status=True,
                                   message=f'解析csv文件 csv_file_name=[{csv_file_name}]成功： successfully.',
                                   data={'row_datas': row_datas})
        except Exception as err:
            return self.result.set(code=400, status=False,
                                   message=f"parse_csv Error ! >>>args `csv_file_name=[{csv_file_name}]`" + str(
                                       err))

    def get_all_keys(self):
        return self.result.set(data=dir(Keys()))

    def press(self, alias, key: str):
        """
        执行键盘按键事件
        """
        try:
            driver = self.switch_driver_cursor_by_alias(alias)
            ActionChains(driver).key_down(key).key_up(key).perform()
            return self.result.set(status=True, data='Press successfully ——> {}'.format(key))

        except Exception as err:
            return self.result.set(400, False, message=str("Press Error! " + str(err)))

    def press_combination(self, alias, key1: str, key2: str):
        """
        执行键盘2个组合键的按键事件
        """
        try:
            driver = self.switch_driver_cursor_by_alias(alias)
            driver.send_keys(key1, key2)
            return self.result.set(data='Press successfully ——> [{}, {}]'.format(key1, key2))
        except Exception as err:
            return self.result.set(400, False, message=str("Press combination Error! " + str(err)))

    def wait_element(self, alias, tag, element, times=5, index=0):
        """
        等待元素出现
        :param tag: 元素类型
        :param element: 元素属性
        :param index: 复数
        :param times: 单位秒
        :return:
        """

        times = int(times)
        count_times = times
        while True:
            try:
                eles = self.finds(tag, alias, element)
                if len(eles) >= int(index) + 1:
                    return self.result.set(status=True,
                                           message='等待 {} 秒，元素已出现: {}'.format(count_times - times, element), data=True)
            except Exception as err:
                print("Wait element countdown {} Seconds, errMsg=[{}]".format(times, err))

            time.sleep(self.GLOBAL_FIND_STEP_TIME)
            times -= self.GLOBAL_FIND_STEP_TIME
            if times <= 0:
                return self.result.set(code=400, status=False, message='等了 {} 秒，未出现元素: {}'.format(count_times, element),
                                       data=False)

    def _get_ele_numbers(self, alias, tag, element):
        """查询元素数量"""
        try:
            element_list = self.finds(tag, alias, element)
            if element_list:
                return len(element_list)
            else:
                return 0
        except Exception:
            raise NoSuchElementException()

    def get_element_numbers(self, alias, tag, element):
        """返回元素个数"""
        try:
            numbers = self._get_ele_numbers(alias, tag, element)
            return self.result.set(data="{}".format(numbers), status=True,
                                   message="Get the element_numbers successfully. >>>Your parameters: `alias=[{}], tag=[{}], element=[{}]`".format(
                                       alias, tag, element))
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def assert_element_numbers(self, alias, tag, element, assert_number):
        """断言元素个数"""
        try:
            numbers = self._get_ele_numbers(alias, tag, element)
            if numbers == int(assert_number):
                return self.result.set(data="{}".format(assert_number), status=True, message="Assertion successfully.")
            else:
                return self.result.set(status=False, data=False,
                                       message="Assertion Error ! The element_number=[{}] but assert_number=[{}] >>>Your parameters: `alias=[{}], tag=[{}], element=[{}]`".format(
                                           str(numbers), assert_number, alias, tag, element))
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def loop_wait_element_exist(self, alias, tag, element, timeout: int):
        """循环等待元素存在"""
        for i in range(timeout):
            element_list = self.finds(tag, alias, element)
            if element_list:
                return self.result.set(status=True, data=f'元素{tag}-{element}存在')
            time.sleep(1)
        else:
            return self.result.set(status=False, data=f'元素{tag}-{element}不存在')

    def loop_wait_element_not_exist(self, alias, tag, element, timeout: int):
        """循环等待元素不存在"""
        for i in range(timeout):
            element_list = self.finds(tag, alias, element)
            if not element_list:
                return self.result.set(status=True, data=f'元素{tag}-{element}不存在')
            time.sleep(1)
        else:
            return self.result.set(status=False, data=f'元素{tag}-{element}存在')

    def set_global_implicity_wait(self, global_timeout):
        # WebDriverWait(self.driver, self.GLOBAL_IMPLICITY_WAIT_TIME).until(EC.element_to_be_clickable(element))
        try:
            self.GLOBAL_IMPLICITY_WAIT_TIME = int(global_timeout)
            self.driver.implicitly_wait(self.GLOBAL_IMPLICITY_WAIT_TIME)
            return self.result.set(
                data='Set global implicity wait time successfully. GLOBAL_IMPLICITY_WAIT_TIME = [{}] seconds.'.format(
                    self.GLOBAL_IMPLICITY_WAIT_TIME))
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def get_element_attribute(self, alias, tag, element, attribute_name, index=0):
        """查询标签的属性，例如获取文本是attribute_name=textContent"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            attribute_value = ele.get_attribute(name=attribute_name)
            return self.result.set(message="Get the attribute successfully.", data='{}'.format(attribute_value))
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def get_element_value_of_css_property(self, alias, element, css_property, tag='classname', index=0):
        """查询CSS属性，例如style的background"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))

        str_value = ele.value_of_css_property(css_property)

        if str_value:
            return self.result.set(status=True, message="Get the css property value successfully.",
                                   data='{}'.format(str_value))
        else:
            # log.warning("The value of this css property is None. please check the parameter class_name={classname}".format(classname=class_name))
            return self.result.set(data=None,
                                   message="The value of this css property is None! >>>Please check the property `css_property=[{}]`".format(
                                       css_property))

    def get_element_size(self, alias, tag, element, index=0):
        """查询元素的大小"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            size = ele.size
            return self.result.set(message="successfully.", data=size)
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def get_tag_name(self, alias, element='', tag='text', index=0):
        """查询标签的类型"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            tagName = ele.tag_name
            return self.result.set(status=True, message="Select the `tagName=[{}]` successfully.".format(tagName),
                                   data=tagName)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def select_by_visible_text(self, alias, element='', tag='text', text='', index=0):
        """通过下拉框的文本进行选择"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            Select(ele).select_by_visible_text(text)
            return self.result.set(status=True, message="Select the `text=[{}]` successfully.".format(text), data=True)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def select_by_value(self, alias, element='', tag='xpath', value='', index=0):
        """通过下拉框的value属性进行选择"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            Select(ele).select_by_value(value)
            return self.result.set(status=True, message="Select the `value=[{}]` successfully.".format(value),
                                   data=True)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def select_by_index(self, alias, element, tag, select_index=0, index=0):
        """通过下拉框的index属性进行选择(默认从0开始)"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            Select(ele).select_by_index(select_index)
            return self.result.set(status=True,
                                   message="Select the `select_index=[{}]` successfully.".format(select_index),
                                   data=True)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def goto_default_content(self, alias):
        """切换到默认的主文档"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.switch_to.default_content()
                return self.result.set(status=True, message="Go to default content successfully.")
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to go to default content!")
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def goto_frame(self, alias, element, tag, index=0):
        """切换到指定的iframe"""
        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.switch_to.frame(ele)
                return self.result.set(status=True, message="Go to the iframe successfully.",
                                       data=True)
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to go to iframe! >>>Your parameters: `alias=[{}], tag=[{}], index=[{}]`".format(
                                           alias, tag, index))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def goto_parent_frame(self, alias, index=0):
        """从子iframe切换到父iframe"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.switch_to.parent_frame()
                return self.result.set(status=True, message="Go to parent iframe successfully.",
                                       data=True)
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to go to parent iframe! >>>Your parameters: `alias=[{}], index=[{}]`".format(
                                           alias, index))
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def get_current_tab_handle(self, alias):
        """获取当前tab窗口的句柄"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                this_tab_handle = driver.current_window_handle
                return self.result.set(status=True, message="Get current window handle successfully.",
                                       data="{}".format(this_tab_handle))
            else:
                return self.result.set(code=404, status=False,
                                       message="Get current window handle Error, No driver is Enabled!")
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def get_all_tab_handles(self, alias):
        """获取全部tab窗口的句柄"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                all_tab_handles_list = driver.window_handles
                return self.result.set(
                    message="Get all browser-Tab handles successfully. Count is {}".format(len(all_tab_handles_list)),
                    data=all_tab_handles_list)
            else:
                return self.result.set(code=404, status=False,
                                       message="Get all browser-Tab handles Error! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                                           alias), data=False)
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def goto_window(self, alias, handle):
        """根据handle跳转到对应窗口"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                old_handle = driver.current_window_handle
                driver.switch_to.window(handle)
                return self.result.set(status=True,
                                       message="Go to target window successfully. Current window handle is `[{}]`".format(
                                           driver.current_window_handle),
                                       data="Old window handle is [{}]".format(old_handle))
            else:
                return self.result.set(
                    message="Unable to go to window! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                        alias), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def exist_alert(self, driver):
        try:
            alert = driver.switch_to.alert
            return alert
        except Exception("No alert on this page !"):
            print("error")
            return None

    def alert_accept(self, alias):
        """弹出框点击确定"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                check_alert = self.exist_alert(driver)
                if check_alert is not None:
                    alert_text = check_alert.text
                    check_alert.accept()
                    return self.result.set(status=True, message="Click accept. The text={}".format(alert_text),
                                           data=True)
                else:
                    return self.result.set(message="No alert on this page.")
            else:
                return self.result.set(
                    message="Unable to find the driver corresponding to alias! >>>Your parameters:`alias=[{}]`".format(
                        alias), data=False)
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def alert_dismiss(self, alias):
        """弹出框点击取消"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                check_alert = self.exist_alert(driver)
                if check_alert:
                    alert_text = check_alert.text
                    check_alert.dismiss()
                    return self.result.set(status=True, message="Click dismiss. The text={}".format(alert_text),
                                           data=True)
                else:
                    return self.result.set(message="No alert on this page.")
            else:
                return self.result.set(
                    message="Unable to find the driver corresponding to alias! >>>Your parameters:`alias=[{}]`".format(
                        alias), data=False)
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def alert_get_text(self, alias):
        """获取弹出框text"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                alert_text = driver.switch_to.alert.text
                return self.result.set(status=True, message="Get the alert Text successfully.",
                                       data="{}".format(alert_text))
            else:
                return self.result.set(
                    message="Unable to find the driver corresponding to alias! >>>Your parameters:`alias=[{}]`".format(
                        alias), data=False)
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def assert_text(self, alias, element, assert_text, assert_mode="all", tag="text", index=0):

        ele = self.find(alias, tag, element, index)
        if not ele:
            return self.result.set(code=400, status=False,
                                   message="当前页面元素未找到 tag=[{}], element=[{}]".format(tag, element))

        un_expected_text = ["0", " ", "undefined", "NaN", "null"]
        count = 0
        try:
            while True:
                element_text = ele.text
                if element_text not in un_expected_text or count > self.GLOBAL_FIND_TOLERANCE or assert_text in un_expected_text:
                    break
                count += 1
                time.sleep(1)

            if assert_mode.lower() in ["all", "in", "not_in"]:
                for _ in range(self.GLOBAL_FIND_TOLERANCE):
                    if assert_mode.lower() == "all":
                        if assert_text == element_text:
                            # if clever_assert_your_text_with_the_element_text(ast=assert_text,elt=element_text, ass_mode="all"):
                            return self.result.set(status=True, data=True,
                                                   message="Assert text [{}] is [{}] matching [{}] succeeded.".format(
                                                       assert_text, assert_mode, element_text))
                        else:
                            return self.result.set(status=False,
                                                   data="The page element_text=[{}], your assert_text=[{}]".format(
                                                       element_text, assert_text),
                                                   message="Words don't match exactly !")
                    elif assert_mode.lower() == "in":
                        if assert_text in element_text:
                            return self.result.set(status=True, data=True,
                                                   message="Assert text [{}] is [{}] the element text [{}].".format(
                                                       assert_text, assert_mode, element_text))
                        else:
                            return self.result.set(status=False,
                                                   data="The page element_text=[{}], your assert_text=[{}]".format(
                                                       element_text, assert_text), message="Words assert Error !")
                    elif assert_mode.lower() == "not_in":
                        if assert_text not in element_text:
                            return self.result.set(status=True, data=True,
                                                   message="Assert text [{}] is [{}] the element text [{}].".format(
                                                       assert_text, assert_mode, element_text))
                        else:
                            return self.result.set(status=False,
                                                   data="The page element_text=[{}], your assert_text=[{}]".format(
                                                       element_text, assert_text), message="Words assert Error !")
            else:
                return self.result.set(status=False, data=False,
                                       message="This [{}] assert_mode is not Supported !".format(assert_mode))

        except Exception as e:
            return self.result.set(code=400, status=False, message=str(e))

    def image_fuzzy_matching(self, image_a_path, image_b_path, assert_value=100):
        """对2个图片的模糊比对， assert_value值表示匹配度，越大则越不匹配， 最小（完全一致）时等于浮点数0.0"""
        ic = ImageCompare()
        try:
            assert_value = float(assert_value)
        except:
            pass

        try:
            if not isinstance(assert_value, float):
                raise TypeError(
                    "The parameter `assert_value` must be of Float Type ! got assert_value=[{}]".format(assert_value))
            match_result = ic.calc_similar_by_path(image_a_path, image_b_path) * 100  # 越接近100，越匹配
            if match_result >= assert_value:
                return self.result.set(status=True, data=True,
                                       message=">>>图片比对完成, 符合您的预期 `match_result=[{}]`".format(match_result))
            else:
                print(">>>图片校验不一致, assert_value=[{}]".format(match_result))
                return self.result.set(code=500, status=False, data=True,
                                       message=">>>图片比对与您的预期不一致, 计算结果是=[{}], 您的预期是=[{}]".format(match_result,
                                                                                                assert_value))
        except Exception as err:
            return self.result.set(400, False, message=str(err), data=False)

    def image_exact_matching(self, image_a_path, image_b_path):
        """对2个图片的精确比对，验证是否完全一致"""
        from PIL import Image, ImageChops
        imageA = Image.open(image_a_path)
        imageB = Image.open(image_b_path)

        A_width, A_height = imageA.size
        B_width, B_height = imageB.size

        target_x = 1
        target_y = 2
        target_offset = 20

        # 图片的左上角是原点，x轴向右，y轴向下，canvas_box表示截取的是左上顶点坐标和右下角坐标:xmin ymin，xmax ymax
        A_canvas_box = (
            A_width / 2 - target_offset, A_height / 2 - target_offset, A_width / 2 + 300, A_height / 2 + 300)
        B_canvas_box = (
            B_width / 2 - target_offset, B_height / 2 - target_offset, B_width / 2 + 300, B_height / 2 + 300)

        result_a = imageA.crop(A_canvas_box)
        result_b = imageB.crop(B_canvas_box)

        # 清理文件
        # remove(image_a_path)
        # remove(image_b_path)

        # 图片一致性比对
        diff = ImageChops.difference(result_a, result_b)
        if diff.getbbox() is None:
            return True
        else:
            print(">>>图片校验不一致")
            return False

    def delete_all_cookies(self, alias):
        """删除所有的cookies"""
        try:
            if self.is_exist_the_alias(alias):
                driver = self.switch_driver_cursor_by_alias(alias)
                driver.delete_all_cookies()
                return self.result.set(message=f'{alias} delete all cookies successful ')
            else:
                return self.result.set(code=404, status=False,
                                       message="Unable to Quit! This alias no corresponding to driver. >>>Your parameters:`alias=[{}]`".format(
                                           alias), data=False)
        except Exception as err:
            return self.result.set(code=400, status=False, message=str(err))

    def clear_interceptor(self):
        """
            清除拦截器
        Returns:

        """
        self.interceptor.clear_interceptor()
        return self.result.set(code=200, status=True, message='ok')

    def set_interceptor(self, alias, original_link, target_link):
        """
            设置拦截器
        Returns:

        """
        self.interceptor.set_interceptor(section=alias, original_link=original_link, target_link=target_link)
        return self.result.set(code=200)

    def get_interceptor_alias_name(self):
        """
            获取拦截器配置
        Returns:

        """
        res = self.interceptor.get_interceptor_alias_name()
        return self.result.set(code=200, data=res)


if __name__ == '__main__':
    # wa = WebDriverAgent()
    # wa.new_browser("teacher-live")
    # wa.open_url("https://www.baidu.com/")
    pass
