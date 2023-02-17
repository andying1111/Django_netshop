from __future__ import absolute_import

import atexit
import os
import platform

from selenium import webdriver

import subprocess
from urllib.error import URLError

from urllib3.exceptions import MaxRetryError

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
driver_dir = os.path.join(root_dir, 'driver')


class ChromeDriver(object):
    def __init__(self, d, port=9515):
        self._d = d
        self._port = port

    def _launch_webdriver(self):
        print("start chromedriver instance")
        p = subprocess.Popen(['./chromedriver', '--port=' + str(self._port)])
        try:
            p.wait(timeout=2.0)
            return False
        except subprocess.TimeoutExpired:
            return True

    def driver(self, webdriver_version, device_ip=None, package=None, attach=True, activity=None, process=None):
        """
        Args:
            - package(string): default current running app
            - attach(bool): default true, Attach to an already-running app instead of launching the app with a clear data directory
            - activity(string): Name of the Activity hosting the WebView.
            - process(string): Process name of the Activity hosting the WebView (as given by ps).
                If not given, the process name is assumed to be the same as androidPackage.

        Returns:
            selenium driver
        """
        app = self._d.current_app()
        if package == 'com.tencent.mm' or app['package'] == 'com.tencent.mm':
            process = 'com.tencent.mm:toolsmp'
            activity = '.plugin.webview.ui.tools.WebViewUI'

        options = webdriver.ChromeOptions()
        options.add_experimental_option('androidDeviceSerial', device_ip or self._d.serial)
        options.add_experimental_option('androidPackage', package or app['package'])
        options.add_experimental_option('androidUseRunningApp', attach)
        options.add_experimental_option('androidProcess', process or app['package'])
        options.add_experimental_option('androidActivity', activity or app['activity'])

        driver_version_path = os.path.join(driver_dir, f"{webdriver_version}")

        if platform.system().lower().count('window') > 0:
            driver_name = "chromedriver.exe"
        else:
            driver_name = "chromedriver"
        driver_path = os.path.join(driver_version_path, driver_name)
        print(driver_path)

        try:
            dr = webdriver.Chrome(driver_path, options=options)
        except URLError:
            dr = webdriver.Chrome(driver_path, options=options)
        except MaxRetryError:
            dr = webdriver.Chrome(driver_path, options=options)
        # always quit driver when done
        atexit.register(dr.quit)
        return dr

    def windows_kill(self):
        subprocess.call(['taskkill', '/F', '/IM', 'chromedriver.exe', '/T'])


if __name__ == '__main__':
    print(os.path.join(root_dir, "driver"))
