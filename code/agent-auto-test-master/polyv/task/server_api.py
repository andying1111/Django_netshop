import requests

from polyv.config import Config
from polyv.task.test_case import TestCase


class PlatformGetApi(object):
    PREFIX = "/openGetApi"

    def get_task_scheduling(self, taskid):
        """通过taskid获取调度对象"""
        return requests.get(url=f'{Config.Server}{self.PREFIX}/clientGetTaskSchedulingByTaskId.do?taskId={taskid}')


class PlatformPostApi(object):
    PREFIX = "/openPostApi"

    def update_task_execute_data(self, task: TestCase, task_status: int):
        """
        更新任务执行数据
        :param task: 任务对象
        :param task_status: 任务状态 [0未执行 1执行中 2执行完成 3执行失败 4唤起客户端失败]
        :return:
        """
        param = {
            "taskId": task.taskId,
            "caseCount": task.caseCount,
            "taskStatus": task_status
        }
        return requests.post(url=f'{Config.Server}{self.PREFIX}/clientUpdateTaskExecuteData', json=param)

    def insert_task_case_execute(self, task: TestCase, case_status: int):
        """
        插入用例执行状态到数据库
        :param task: 任务对象
        :param case_status: 用例执行状态 0通过 1失败 2锁定 3执行中 4未执行
        :return:
        """
        param = {
            "taskId": task.taskId,
            "projectId": task.projectId,
            "caseId": task.caseId,
            "caseSign": task.caseSign,
            "caseName": task.caseName,
            "caseStatus": case_status,
        }
        return requests.post(url=f'{Config.Server}{self.PREFIX}/clientPostTaskCaseExecute', json=param)

    def update_task_case_execute(self, task: TestCase, case_status: int):
        """
        修改用例执行状态到数据库
        :param task: 任务对象
        :param case_status: 用例执行状态 0通过 1失败 2锁定 3执行中 4未执行
        :return:
        """
        param = {
            "taskId": task.taskId,
            "caseId": task.caseId,
            "caseStatus": case_status,
        }
        return requests.post(url=f'{Config.Server}{self.PREFIX}/clientUpdateTaskCaseExecuteStatus', json=param)

    def insert_task_case_log(self, task, log, log_grade, log_step, log_image=None):
        """
        插入用例执行明细到数据库
        :param task: 任务对象
        :param log: 详细log
        :param log_grade: log级别
        :param log_step: 第几个步骤
        :param log_image: 步骤截图
        :return:
        """
        param = {
            "taskId": task.taskId,
            "caseId": task.caseId,
            "logStep": log_step,
            "logDetail": log,
            "logGrade": log_grade,
            "Imgname": log_image,
        }
        return requests.post(url=f'{Config.Server}{self.PREFIX}/clientPostTaskCaseLog', json=param)
