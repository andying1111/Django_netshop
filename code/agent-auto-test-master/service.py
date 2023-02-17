import os
import time
from threading import Thread

import requests
import uvicorn

from polyv import config
from polyv.app import app
from polyv.common import ip_util
from polyv.common.device import get_android_device, get_ios_device
from polyv.common.upload_driver_log import upload_driver_log
from polyv.config import IS_UPLOAD_LOG, Config, IS_RUNNER, IS_NEW_RUNNER
from polyv.scripts.web_driver import WebDriverAgent
from polyv.task.task_runner import runner


def upload_logs():
    wa = WebDriverAgent()
    while True:
        print('当前运行时角色：', wa.alias_and_driver_session_dict)
        for role, driver in wa.alias_and_driver_session_dict.items():
            upload_driver_log(role, driver)
        time.sleep(10)


def task_runner():
    while True:
        try:
            get_task = requests.get(f'http://{Config.ClientServer}:{Config.ClientPort}/getTask').json()
        except:
            print('无法连接客户端服务...')
        try:
            print(get_task['caseName'])
            runner(get_task)
        except:
            # print(get_task)
            time.sleep(5)


def register():
    """ 向保利威云测试平台服务注册（配置自动测试平台【公共参数】中配置） """
    url = 'http://giter.igeeker.org/api/agent/agent_info'  # (新)自动化服务部署地址

    while True:
        try:
            data = {'ip': f'http://{Config.Host}:{Config.Port}', 'version': Config.Version,
                    'status': not config.IS_WORK, 'device': {'android': get_android_device(), 'ios': get_ios_device()}}
            # print(data)
            requests.post(url, json=data).json()
            # print(response)
            time.sleep(15)
        except Exception as err:
            time.sleep(10)
            print(f"注册失败！—— {err}")


if __name__ == "__main__":
    directory = os.getcwd() + "/image.temp"
    if not os.path.exists(directory):  # 如果目录不存在就返回False
        os.mkdir(directory)
    Config.Host = ip_util.get_ip()
    print(Config.Host)

    if IS_UPLOAD_LOG:
        up_log_thread = Thread(target=upload_logs)
        up_log_thread.start()

    if IS_RUNNER:
        Thread(target=task_runner).start()

    if IS_NEW_RUNNER:
        Thread(target=register).start()

    uvicorn.run(app=app, host="0.0.0.0", port=8081, workers=1)
