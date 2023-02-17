import os

import requests
from seleniumwire.request import Request, Response

from polyv.config import Config
import configparser


class SDKInterceptor(object):

    def __init__(self):
        if not os.path.exists(os.path.join(Config.BASE_DIR, 'interceptor.ini')):
            with open(os.path.join(Config.BASE_DIR, 'interceptor.ini')) as f:
                pass
        self.__conf = None
        self.__conf_path = os.path.join(Config.BASE_DIR, 'interceptor.ini')

    def __get_interceptor_conf(self):
        """
            获取配置文件对象
            Returns:
        """
        if self.__conf is None:
            self.__conf = configparser.ConfigParser()
            self.__conf.read(self.__conf_path)

    # 设置拦截器配置
    def __set_interceptor(self, section, original_link, target_link):
        """
            设置配置
        Args:
            section: SDK
            original_link:  需要替换的link
            target_link:    目标link

        Returns:

        """
        self.__get_interceptor_conf()
        if not self.__conf.has_section(section):
            self.__conf.add_section(section)
        self.__conf.set(section, 'original_link', original_link)
        self.__conf.set(section, 'target_link', target_link)
        self.__conf.write(open(self.__conf_path,'w+'))

    # 清除拦截器配置
    def clear_interceptor(self):
        """
            清空拦截器配置
        Returns:
        """
        os.remove(os.path.join(Config.BASE_DIR, 'interceptor.ini'))
        self.__conf = None
        with open(os.path.join(Config.BASE_DIR, 'interceptor.ini'), 'w') as f:
            pass

    def get_interceptor_alias_name(self):
        """
            读取拦截器配置
        Returns:

        """
        self.__get_interceptor_conf()  # 读取配置
        return self.__conf.items()

    def set_interceptor(self, section='sdk_js', original_link=None, target_link=None):
        """
            设置拦截器
        Args:
            section:    driver name
            original_link:  需要拦截的路径
            target_link:    拦截后转换目标路径
        Returns:

        """
        if not original_link:
            original_link = 'http://player.polyv.net/resp/live-h5-player/latest/liveplayer.min.js'
        self.__set_interceptor(section=section, original_link=original_link, target_link=target_link)

    def sdk_interceptor(self, request: Request):
        """
            拦截器
        Args:
            request:
        Returns:
        """
        ""
        print("拦截器启用:{}".format(request.url))
        self.__get_interceptor_conf()  # 读取配置
        interceptor_dict = {}
        for section in self.__conf.sections():
            interceptor_dict[self.__conf.get(section, 'original_link')] = self.__conf.get(section, 'target_link')
        if interceptor_dict.get(request.url):
            print('拦截到{}'.format(request.url))
            content = requests.get(interceptor_dict[request.url]).content
            request.create_response(
                status_code=200,
                headers={'Content-Type': 'text/html'},  # Optional headers dictionary
                body=content  # Optional body
            )
            print('替换为:{}'.format(interceptor_dict[request.url]))
