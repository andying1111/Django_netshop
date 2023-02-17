import os
import subprocess
import time

from polyv.api.common import service
from polyv.config import Config
from polyv.scripts.common import HostUtils
from polyv.task.git import check_project_code_is_update
from polyv.task.server_api import PlatformPostApi, PlatformGetApi
from polyv.task.test_case import TestCase

api_post = PlatformPostApi()
api_get = PlatformGetApi()
host_util = HostUtils()
report_name = None


def get_command(step, report):
    if '.bat' in step.packPath:
        param = ''
        for p in step.parameters:
            param = param + " " + p
        f = open(f'{Config.BASE_DIR}\\test-directory\\{step.packPath}', 'r')
        text = f.read().split("\\")
        f.close()

        project = text[14]
        parent_path = f'{Config.BASE_DIR}/test-directory/{project}'
        venv_python = os.path.join(parent_path, 'venv\\Scripts\\python.exe -m ')
        flg = False
        parent_path = f'{Config.BASE_DIR}/test-directory'
        for t in text:
            if t == 'AgentSuite':
                flg = True
                continue
            if t == '':
                continue
            if flg and '%1\n' in t:
                break
            if flg:
                parent_path = os.path.join(parent_path, t)

        command = f'set AGENT_HOST=http://{Config.Host}:8081&&{venv_python}pytest -x --show-capture=no {parent_path}\\{param.strip()} --report=' \
                  f'{report}.html --title=UITestReport --tester=Roboter --desc=Report'
    else:
        command = f'set AGENT_HOST=http://{Config.Host}:8081&&pytest -x --show-capture=no {step.packPath} {step.parameters}' \
                  f' --report={report}.html --title=UITestReport --tester=Roboter --desc=Report'
    return command


def case_notify(task):
    try:
        data_json = {
            "projectSign": task.projectSign,
            "type": "case",
            "data": {
                "name": task.caseName,
                "result": "failure",
                "username": task.executor
            }
        }
        if task.notify:
            print(service.send_results(data_json))
    except Exception as e:
        api_post.insert_task_case_log(task, f'单条case失败通知异常：{e} \n{task}', "error", 98)
    pass


def task_notify(task, result):
    try:
        data_json = {
            "projectSign": task.projectSign,
            "type": "suite",
            "data": {
                "overview": {
                    "name": task.projectName,
                    "total": result['caseCount'],
                    "success": result['caseSuc'],
                    "failure": result['caseFail'],
                    "time": f"{time.time() - task.startTime}'s",
                },
                "case_detail": [],
                "username": task.executor
            }
        }
        if task.notify:
            service.send_results(data_json)
    except Exception as e:
        api_post.insert_task_case_log(task, f'测试套件通知遇异常：{e} \n{task}', "error", 99)
    pass


def runner(obj):
    task = TestCase()
    task.__dict__ = obj
    task.decode_step()
    print(task.__dict__)
    check_project_code_is_update(task)

    print('更新任务执行中：' + api_post.update_task_execute_data(task=task, task_status=1).text)  # 更新任务执行数据：1=执行中
    print('更新用例执行中：' + api_post.insert_task_case_execute(task=task, case_status=3).text)  # 更新用例执行数据：3=执行中
    print(api_post.insert_task_case_log(task=task, log=f'执行机器：{Config.Host} ......', log_grade='info', log_step=1).text)
    print("写入HOST: " + host_util.write_text_host(task.hostStr).message)
    _step = 1
    result = False
    try:
        for i in range(0, 3):
            # 失败重试3次
            for step in task.steps:
                _step = step.caseIndex
                api_post.insert_task_case_log(task=task, log=f'开始调用方法：{step.function} ......', log_grade='info',
                                              log_step=step.caseIndex)
                api_post.insert_task_case_log(task,
                                              f"解析步骤： 包路径【{step.packPath}】，执行函数【{step.function}】，参数【{step.parameters}】",
                                              "info", step.caseIndex)
                global report_name
                report_name = time.time()
                runner_result = execute_step(step, get_command(step, report_name))
                result = check_result(runner_result, step.expectResult)
                if not result:
                    runner_result = runner_result \
                        .replace("🚀🚀🚀", " ") \
                        .replace("📱📱📱", " ") \
                        .replace("💣💣💣", " ") \
                        .replace("🚄🚄🚄", " ")
                    logs = f"第{step.caseIndex}步，执行结果断言失败！预期结果【{step.expectResult}】，实际结果：【{runner_result}】"
                    api_post.insert_task_case_log(task, logs, "error", step.caseIndex)
                    logs = f'<a target="_blank" href="http://{Config.Host}:{Config.Port}/api/common/report?id={report_name}.html">点击查看报告详情</a>'
                    api_post.insert_task_case_log(task, logs, 'error', step.caseIndex)
                    if i > 1:
                        case_notify(task)
                    break
                else:
                    logs = f"第{step.caseIndex}步，执行结果断言通过！预期结果【{step.expectResult}】，实际结果：【{runner_result}】"
                    api_post.insert_task_case_log(task, logs, "info", step.caseIndex)
                    logs = f'<a target="_blank" href="http://{Config.Host}:{Config.Port}/api/common/report?id={report_name}.html">点击查看报告详情</a>'
                    api_post.insert_task_case_log(task, logs, 'info', step.caseIndex)
            if result:
                break
        api_post.update_task_case_execute(task=task, case_status=0 if result else 1)  # 更新用例执行数据：0=成功，1=失败

    except Exception as e:
        api_post.insert_task_case_log(task, f'执行用例发生未知错误：{e}', "error", _step)
        api_post.update_task_case_execute(task=task, case_status=2)  # 更新用例执行数据：2=锁定
    task_is_finish(task)


def task_is_finish(task):
    try:
        task_runner_status = api_post.update_task_execute_data(task=task, task_status=1).json()
        print(task_runner_status)
        status = task_runner_status['caseCount'] - (
                task_runner_status['caseSuc'] + task_runner_status['caseFail'] + task_runner_status['caseLock'] +
                task_runner_status['caseNoExec'])
        if status == 0:
            print('更新任务执行结束：' + api_post.update_task_execute_data(task=task, task_status=2).text)  # 更新任务执行数据：2=执行完成
            task_notify(task, task_runner_status)
    except Exception as e:
        print('更新任务状态异常！', e)


def execute_step(step, command):
    result = None
    flog = step.caseType
    if flog == 1:
        print('准备开始调用【Web自动化用例】......')
        pass
    elif flog == 2:
        print('准备开始调用在线【Android移动自动化用例】......')
        pass
    elif flog == 3:
        print('准备开始调用在线【iOS 自动化用例】......')
        pass
    elif flog == 4:
        print('准备开始调用在线【Windows 自动化用例】......')
        pass
    elif flog == 5:
        print('准备开始调用Http请求......')
        pass
    elif flog == 6:
        print('准备开始调用【命令驱动】......')
        if command is None:
            print(f'command={command}')
        param = ''
        for p in step.parameters:
            param = param + " " + p
        result = exec_command(command)
    return result


def check_result(content, expected_results):
    if content is None:
        return False

    if expected_results.startswith('%='):
        # 模糊匹配
        return expected_results.replace('%=', '') in content
    elif expected_results.startswith('~='):
        # 正则匹配 TODO
        return False
    else:
        # 全匹配
        return expected_results == content


def exec_command(command):
    """执行cmd命令"""
    print(command)
    execute = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding="utf-8", timeout=3000)
    return execute.stdout if execute.stdout != '' else execute.stderr
