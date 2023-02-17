import os
import re
import subprocess
import sys
import uuid

import requests
from fastapi import Response

from polyv import config
from polyv.common.data_format import DataFormat
from polyv.config import DingTalkToken, QA_INFO, Config
from settings import ROOT_PATH


class Service:
    result = DataFormat()

    def status(self):
        return self.result.set(message='Available',
                               data=config.TOKEN) if not config.IS_WORK else self.result.set(
            message='Not Available', data=config.TOKEN)

    def set_status(self, state=True):
        config.IS_WORK = state
        config.TOKEN = uuid.uuid4() if state else None
        return self.result.set(message='set status success!', data=config.TOKEN)

    def get_network_info(self, cycle):
        cycle = int(cycle)
        log_path = os.getcwd() + '/monitor_network_log.txt'
        log_content = []
        with open(log_path, 'r') as f:
            log_content = [x.strip() for x in f.readlines()]

        return self.result.set(data=log_content[-cycle:])

    def get_image(self, image_id):
        # 查看图片
        try:
            file = os.getcwd() + "/image.temp/{}.png".format(image_id)
            with open(file, 'rb') as f:
                image = f.read()
                resp = Response(content=image)
                return resp
        except Exception as e:
            return self.result.set(code=404, status=False, message='图片不存在')

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

    def get_report(self, report_id):
        # 查看报告
        try:
            file = os.getcwd() + "/reports/{}".format(report_id)
            with open(file, 'rb') as f:
                report = f.read()
                resp = Response(report)
                return resp
        except Exception as e:
            return self.result.set(code=404, status=False, message='报告不存在')

    def send_results(self, data_json):

        print(data_json, type(data_json))

        def _get_ding_robot_token(project_name):
            return DingTalkToken.get(project_name) or DingTalkToken.get("DEBUG")

        DingTalk_token = os.environ.get('DINGTALK_TOKEN',
                                        _get_ding_robot_token(data_json.get("projectSign", "DEBUG")))
        url = "https://oapi.dingtalk.com/robot/send?access_token=" + DingTalk_token
        case_title = "## UI自动化失败告警!!\n "
        suite_title = "## UI自动化执行概要\n "
        from polyv.task.task_runner import report_name
        report_url = f"\n\n[速度查看详情](http://{Config.Host}:{Config.Port}/api/common/report?id={report_name}.html)"
        report_url_2 = "\n\n[点击查看详情](http://autotest.igeeker.org/index)"
        if data_json.get("type") == "case":
            case_detail = data_json.get("data")
            message = f" - 用例名称:{case_detail.get('name')},执行结果:{case_detail.get('result')} @{QA_INFO[case_detail.get('username')]}"
            content = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "自动化测试结果摘要",
                    "text": case_title + message + report_url
                },
                "at": {
                    "atMobiles": [phone for username, phone in QA_INFO.items()],
                    "isAtAll": False
                }
            }
            print(case_title + message)
            if case_detail.get("result") == "failure":
                resp = requests.post(url, json=content)
                return self.result.set(code=200, status=True, data=resp.json())
            else:
                return self.result.set(code=200, status=True, message=f"用例状态为{case_detail.get('result')},忽略推送~")

        if data_json.get("type") == "suite":
            suite_overview = data_json.get("data").get("overview")
            suite_name = f'### 套件名称：{suite_overview.get("name")}\n'
            suite_total = f'#### 用例总数：{suite_overview.get("total")}\n'
            suite_success = f'#### 成功用例：{suite_overview.get("success")}\n'
            suite_fail = f'#### 失败用例：{suite_overview.get("failure")}\n'
            suite_percent = f'#### 成功百分比：{str(round(int(suite_overview.get("success")) / int(suite_overview.get("total")) * 100, 2))}% \n'
            suite_time = f'#### 执行时长：{suite_overview.get("time")}\n'

            suite_case = data_json.get("data").get("case_detail")
            suite_executor = data_json.get("data").get("executor")
            suite_message = "\n"
            fail_case = [case.get('name') for case in suite_case if case.get('result') == 'failure']
            if len(fail_case) > 0:
                suite_message += "### 失败用例列表\n\n"
                for case in fail_case:
                    suite_message += f"- {case} \n"

            suite_executor = f'@{QA_INFO.get(suite_executor, QA_INFO["lihongbo"])}\n'  # 没有找到 认定洪波 准没错！！
            content = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "自动化测试结果摘要",
                    "text": suite_title + suite_name + suite_total + suite_success + suite_fail + suite_percent + suite_time + suite_executor + report_url_2
                },
                "at": {
                    "atMobiles": [phone for username, phone in QA_INFO.items()],
                    "isAtAll": False
                }
            }
            print(
                suite_name + suite_total + suite_success + suite_fail + suite_percent + suite_time + suite_message + report_url_2 + suite_executor)
            resp = requests.post(url, json=content)
            return self.result.set(code=200, status=True, data=resp.json())

    def push_flow_start(self, channel):
        try:
            data = {
                'channel_id': channel,
                'email': "web_live_test@polyv.com",
                'password': "weblivetest"
            }
            rsp = requests.post(
                f'{config.STREAM_PUSHER_INFO}/api/push/stream', json=data)
            return rsp.json()
        except Exception as e:
            print(e)
            return e

    def push_flow_stop(self, channel):
        try:
            data = {
                'channel_id': channel,
            }
            rsp = requests.post(
                f'{config.STREAM_PUSHER_INFO}/api/push/stop', json=data)
            return rsp.json()
        except Exception as e:
            print(e)
            return e

    def push_flow_status(self, channel):
        try:
            params = {
                'channel_id': channel
            }
            rsp = requests.get(
                f'{config.STREAM_PUSHER_INFO}/api/push/status', params=params)
            return rsp.json()
        except Exception as e:
            print(e)
            return e

    def get_download_file(self):
        """获取download目录下的文件"""
        try:
            path = os.path.abspath(f'./downloads/')
            file_list = os.listdir(path)
            return self.result.set(code=200, status=True, message="获取成功", data=file_list)

        except Exception as e:
            return self.result.set(code=500, status=True, message=f"获取失败：{e}")

    def delete_download_file(self, filename):
        """删除download文件"""
        try:
            if filename:
                files = [os.path.abspath(f'./downloads/{filename}')]
            else:
                path = os.path.abspath(f'./downloads/')
                files = [os.path.abspath(f'./downloads/{file_name}') for file_name in os.listdir(path)]

            for file in files:
                os.remove(file)

            return self.result.set(code=200, status=True, message="删除文件成功", data=files)

        except Exception as e:
            return self.result.set(code=500, status=True, message=f"删除文件失败：{e}")

    def get_resource_file(self, filename):
        """获取resource目录下的文件"""
        try:
            file = os.path.join(ROOT_PATH, "resources", filename)
            if os.path.exists(file):
                return self.result.set(code=200, status=True, message="获取成功", data=file)
            else:
                return self.result.set(code=500, status=True, message=f"文件{file} 不存在")

        except Exception as e:
            return self.result.set(code=500, status=True, message=f"获取失败：{e}")

    def delete_pc_process_by_name(self, application_name):
        wmic_command = f'wmic process where name="{application_name}" delete'
        if sys.platform != ('darwin'):
            os.system(wmic_command)
            return self.result.set(code=200, status=True, message=f"完成执行命令： {wmic_command}")
        else:
            return self.result.set(code=200, status=True, message=f"当前不是Windows系统，不执行命令：{wmic_command}")


class HostUtils(object):
    HOST_FILE = r"C:\Windows\System32\drivers\etc\hosts"
    result = DataFormat()

    def check_host(self, host_file=HOST_FILE):
        """
            检查host是否生效
        """
        # TODO
        host_dict = self.read_host_file(host_file)

    def read_host_file(self, host_file=HOST_FILE):
        """
            读取本机host文件
        """
        host_list = []
        host_dict = dict()
        with open(host_file, 'r', encoding='utf8') as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                if re.match(r"((25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))",
                            line) and "#" not in line and line != '\n':
                    # 符合ip正则表达式并且不包含，并且不包含“#” 并且不为换行符
                    host_list.append(line.strip().split(' '))
            for item in host_list:
                if host_dict.get(item[0]):
                    for host in item[1:]:
                        if host != "":
                            host_dict[item[0]].append(host)
                else:
                    host_dict[item[0]] = []
                    for host in item[1:]:
                        if host != "":
                            host_dict[item[0]].append(host)
        return host_dict

    def get_host(self, host_file=HOST_FILE):
        """
            获取本机host
        """
        host_dict = self.read_host_file(host_file)
        return self.result.set(code=200, status=True, data=host_dict)

    def overwrite_host(self, host_dict, host_file=HOST_FILE):
        """
            覆盖写入host配置(字典形式)
        """
        try:
            with open(host_file, 'w', encoding='utf8') as f:
                count = 0
                for ip, host_list in host_dict.items():
                    temp_host_item = ' '
                    temp_host_item = temp_host_item.join(host_list)
                    temp_host_item = str(ip) + " " + temp_host_item + '\n'

                    f.writelines(temp_host_item)
                    count += 1
        except PermissionError as e:
            # 权限问题修改失败返回-1
            return self.result.set(code=200, status=True, message="客户端无修改host权限", data=-1)

        # 返回插入内容
        return self.result.set(code=200, status=True, data=count, message="成功写入{}条host".format(count))

    def write_text_host(self, host_str, host_file=HOST_FILE):
        """
            字符串形式直接覆盖host
        """
        try:
            with open(host_file, 'w', encoding='utf8') as f:
                f.write(host_str)
        except PermissionError as e:
            # 权限问题修改失败返回-1
            return self.result.set(code=200, status=True, message="客户端无修改host权限", data=-1)

        # 返回插入内容
        return self.result.set(code=200, status=True, data=host_str, message="成功写入host字符串")
