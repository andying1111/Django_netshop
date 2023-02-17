import json
import os
import shutil
import stat
import subprocess
import time
from queue import Queue

import requests

from polyv.config import Config
from polyv.task.server_api import PlatformPostApi

gitlab_addr = 'git.polyv.net'
gitlab_token = 'AKM8yk_b8R4Yzudy7fed'
tasks = Queue(maxsize=0)
task_list = []
ac = 'pip install -U git+http://polyv-public:8fMCOXrYQ0iE@git.polyv.net/testdevelopment/python/agent_caller.git'
jx = 'https://pypi.tuna.tsinghua.edu.cn/simple'


class GitProject(object):
    id: int
    url: str
    name: str
    path: str


class Task(object):
    url: str
    branch: str
    name: str


def get_all_project_info():
    """
    获取项目信息
    :return:
    """
    project_list = []
    for index in range(10):
        url = "https://%s/api/v4/projects?private_token=%s&per_page=100&page=%d&order_by=name" % (
            gitlab_addr, gitlab_token, index)
        proj_dict = json.loads(requests.get(url).content)
        if len(proj_dict) == 0:
            break
        for thisProject in proj_dict:
            gp = GitProject()
            try:
                gp.id = thisProject['id']
                gp.url = thisProject['http_url_to_repo']
                gp.path = thisProject['path_with_namespace']
                gp.name = gp.path.rsplit("/", 1)
                print(f'{gp.id}, {gp.url}, {gp.path}')
                project_list.append(gp)

            except Exception as e:
                print("Error on %s: %s" % (url, e.strerror))
        return project_list


def git_pull(project_path, repo_branch=None):
    """
    拉取代码
    :return:
    """
    result = ''
    try:
        st = time.time()
        if repo_branch:
            cmd(f'pushd {project_path} && git checkout {repo_branch}')  # 检出对应分支
        result = cmd(f'pushd {project_path} && git pull')  # 拉取最新代码
        print('===================================git code====================================')
        print(f' 项目路径:{project_path}\n 更新代码：{result} \n 执行耗时：{time.time() - st}')
        result = 'Already up to date' not in result

        if result:  # 如果有代码更新则触发更新anget_caller
            install_agent_caller = 'install -U git+http://polyv-public:8fMCOXrYQ0iE@git.polyv.net/testdevelopment/python/agent_caller.git'
            venv_pip = os.path.join(project_path, 'venv\\Scripts\\pip.exe')
            command = f'pushd {project_path} && {venv_pip} {install_agent_caller}'
            print(f'install "agent_caller":\n{cmd(command)}')
        print('============================================================================')

    except Exception as e:
        print(f'拉取失败：{e}')
    return result


def git_clone(git_address, repo_branch, project_path):
    """
    拉取代码
    :return:
    """
    try:
        if os.path.exists(project_path):
            return git_pull(project_path, repo_branch)

        result = cmd(f'git clone -b {repo_branch} "{git_address}" {project_path}')
        venv_pip = os.path.join(project_path, 'venv\\Scripts\\pip.exe')
        if 'already exists and is not an empty directory.' in result:
            git_pull(project_path, repo_branch)
        else:
            print(f'git clone result: {result}')
            # 首次拉取代码，必进行一次依赖安装
            venv = 'python -m venv venv && venv\\Scripts\\activate.bat'
            command = f'pushd {project_path} && {venv} && {venv_pip} install -r requirements.txt -i {jx}&&{ac}'
            print(f'首次安装依赖：{cmd(command)}')
    except Exception as e:
        print(f'git clone 拉取失败：{e}')
    return os.path.exists(os.path.join(project_path, '.git'))


def delete_file(file_path):
    if os.path.exists(file_path):
        for fileList in os.walk(file_path):
            for name in fileList[2]:
                os.chmod(os.path.join(fileList[0], name), stat.S_IWRITE)
                os.remove(os.path.join(fileList[0], name))
        shutil.rmtree(file_path)
        return "delete ok"
    else:
        return "no filepath"


def cmd(*args, **kwargs):
    try:
        process = subprocess.Popen(shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   *args, **kwargs)
        output, unused_err = process.communicate()
        if process.poll() == 0:
            return str(output)
        else:
            return str(unused_err)
    except Exception as e:
        return str(e)


def check_project_code_is_update(task):
    try:
        for git in task.git:
            try:
                code_git_url = git.split('#')[0]
                code_git_branch = git.split('#')[1]
                project_name = (code_git_url.split('/')[-1]).split('.')[0]
                project_path = Config.BASE_DIR.joinpath('test-directory', project_name)

                git_clone(git_address=code_git_url, repo_branch=code_git_branch, project_path=project_path)

                # tag = False
                # for step in task.steps:
                #     if step.packPath.replace(f"{(code_git_url.split('/')[-1]).split('.')[0]}", "") != step.packPath:
                #         tag = True
                #         break
                # if not tag and ('\\' in task.steps[0].packPath or '/' in task.steps[0].packPath):
                #     continue
                #
                # if os.path.exists(project_path):
                #     tm_path = project_path.joinpath('.git/objects')
                #     file_modify_time = time.mktime(time.localtime(os.stat(tm_path).st_mtime))  # 文件修改时间
                #     current_time = time.mktime(time.localtime())  # 当前系统时间
                #     act_time = (current_time - file_modify_time) / (60 * 60)
                #     if act_time > 24:
                #         print(f'代码更新时间大于： {act_time} 小时')
                #         project_path = git_pull(code_git_url, code_git_branch)
                #
                # else:
                #     print(f'项目【{project_name}】首次拉取代码...')
                #     project_path = git_pull(code_git_url, code_git_branch)
                # if os.path.exists(project_path):
                #     command = f'pushd {project_path}&&' \
                #               f'pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple&&' \
                #               f'pip install -U git+http://polyv-public:8fMCOXrYQ0iE@git.polyv.net/testdevelopment/python/agent_caller.git'
                #     gitpull = cmd(command)
                #     PlatformPostApi().insert_task_case_log(task, f"拉取最新代码, 并安装到最新引入依赖： {gitpull}", "info", 1)
            except Exception as e:
                print(e)
    except Exception as e:
        print('拉取代码异常：', e)
        PlatformPostApi().insert_task_case_log(task, f"拉取最新代码, 发生异常： {e}", "error", 1)


if __name__ == '__main__':
    ...
    url = 'http://git.polyv.net/testdevelopment/python/pep.git'
    branch = 'master'
    print(git_clone(url, branch, r'C:\workspace\develop\python\Agent\agent-auto-test\test-directory\pep'))
