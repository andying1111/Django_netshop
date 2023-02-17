import os
import platform
import subprocess
from json import loads as jsonLoads


class CallingOCR:
    """调用OCR"""

    def __init__(self, exe_path=r".\lib\PaddleOCR\PaddleOCR_json.exe"):
        """初始化识别器。\n
        传入识别器exe路径"""
        cwd = os.path.abspath(os.path.join(exe_path, os.pardir))  # exe父文件夹
        startupinfo = None  # 静默模式设置
        if 'win32' in str(platform).lower():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        self.ret = subprocess.Popen(  # 打开管道
            exe_path,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            startupinfo=startupinfo  # 开启静默模式
        )
        self.ret.stdout.readline()  # 读掉第一行

    def run(self, img_path, flog=False):
        """对一张图片文字识别。
        输入图片路径。\n
        识别成功时，返回列表，每项是一组文字的信息。\n
        识别失败时，返回字典 {error:异常信息，text:(若存在)原始识别字符串} 。"""
        if not img_path[-1] == "\n":
            img_path += "\n"
        try:
            self.ret.stdin.write(img_path.encode("gbk"))
            self.ret.stdin.flush()
        except Exception as e:
            return {"code": 300, "data": f"向识别器进程写入图片地址失败，疑似该进程已崩溃。{e}"}
        try:
            strs = self.ret.stdout.readline().decode('utf-8', errors='ignore')
        except Exception as e:
            if img_path[-1] == "\n":
                img_path = img_path[:-1]
            return {"code": 301, "data": f"读取识别器进程输出值失败，疑似传入了不存在或无法识别的图片 \"{img_path}\" 。{e}"}
        try:
            js = jsonLoads(strs)
            if flog:
                return js
            rlist = []
            for s in js['data']:
                rlist.append(s["text"])
                print(s["text"])
            print(rlist)
            return rlist
        except Exception as e:
            if img_path[-1] == "\n":
                img_path = img_path[:-1]
            return {"code": 302, "data": f"识别器输出值反序列化JSON失败，疑似传入了不存在或无法识别的图片 \"{img_path}\" 。异常信息：{e}。原始内容：{strs}"}

    def __del__(self):
        self.ret.kill()  # 关闭子进程
        # print("关闭OCR！")
