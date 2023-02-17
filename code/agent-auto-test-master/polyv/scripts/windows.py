import sys
import os
import typing

from polyv.common import ip_util

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Literal
else:  # pragma: no cover
    from typing_extensions import Literal

import time
import logging

from pathlib import Path

import autoit as at

from polyv.common.data_format import DataFormat, safe_agent

logger = logging.getLogger(__file__)

class MouseControl(object):
    """
    AutoIt鼠标相关操作
    """
    r = DataFormat()

    def __init__(self):
        """
        Constructor
        """
        pass

    def click(self, x, y, button, clicks, speed):
        """
        :description 执行鼠标点击操作
        """
        try:
            at.mouse_click(button=button, x=x, y=y, clicks=clicks, speed=speed)
            return self.r.set(data='click success')
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='click fail')

    def move(self, x, y):
        """
        :description 移动鼠标指针
        """
        try:
            at.mouse_move(x, y)
            return self.r.set(data='move success')
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='move fail')

    def drag(self, x1, y1, x2, y2):
        """
        :description 执行鼠标拖拽操作
        """
        try:
            # pos = at.win_get_pos(title, text=text)
            # at.mouse_click_drag(x1 + pos[0], y1 + pos[1], x2 + pos[0], y2 + pos[1])
            at.mouse_click_drag(x1, y1, x2, y2)
            return self.r.set(data='drag success')
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='drag fail')

    def wheel(self, direction="up"):
        """
        :description 产生向上或向下滚动鼠标滚轮事件.仅支持NT/2000/XP及更高.
        """
        try:
            at.mouse_wheel(direction)
            return self.r.set(data='wheel success')
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='wheel fail')


class ProcessControl(object):
    """
    AutoIt进程相关操作
    """
    r = DataFormat()

    def __init__(self):
        """
        Constructor
        """
        pass

    def close(self, process_name):
        """
        :description 终止某个进程
        :return 1:成功; 0:失败.
        """
        try:
            return self.r.set(data=at.process_close(process_name))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def exists(self, process_name):
        """
        :description 检查指定进程是否存在
        :return PID:成功; 0:进程不存在.
        """
        try:
            return self.r.set(data=at.process_exists(process_name))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)


class WinAgent(object):
    """
    AutoIt窗口相关操作
    """

    def __init__(self):
        """
        Constructor
        """
        self.r = DataFormat()

    def activate(self, title='', text=''):
        """
        :description 激活指定的窗口(设置焦点到该窗口,使其成为活动窗口).
        :return PID:窗口存在; 0:窗口不存在.
        """
        try:
            return self.r.set(data=at.win_activate(title, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def close(self, title='', text=''):
        """
        :description 关闭指定窗口.
        :return 1:成功; 0:窗口不存在.
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.win_close(title, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def exists(self, title):
        """
        :description 检查指定的窗口是否存在.
        :return 1:窗口存在; 0:窗口不存在.
        """
        try:
            return self.r.set(data=at.win_exists(title))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def get_pos(self, title='', text=''):
        """
        :description 获取指定窗口的坐标位置和大小等属性.
        :return Returns left, top, right, bottom    (x1,y1,x2,y2)
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.win_get_pos(title, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='unknown')

    def get_process(self, title='', text=''):
        """
        :description 获取指定窗口关联的进程ID(PID).
        :return PID:成功, -1:失败.
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.win_get_process(title, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=-1)

    def get_text(self, title='', text='', buf_size=256):
        """
        :description 获取指定窗口中的文本.
        :return  指定窗口里包含的文本:成功; 0:失败(没有匹配的窗口).
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.win_get_text(title, buf_size, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def kill(self, title='', text=''):
        """
        :description 强行关闭指定窗口.
        :return  1:无论成功失败.
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.win_kill(title, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='unknown')

    def set(self, title, text, x, y, width, height):
        """
        :description 移动指定的窗口或调整窗口的大小.
        :return PID:成功, 0:失败(窗口不存在).
        """
        try:
            return self.r.set(data=at.win_move(title, x, y, width, height, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def set_state(self, title, text, flag):
        """
        :description 显示,隐藏,最小化,最大化或还原一个窗口.

        @param flag: The "show" flag of the executed program:1 = 显示,2 = 最小化/隐藏,3 = 最大化,4 = 还原
        @param title
        @param text
        :return 1:成功, 0:失败(窗口不存在).
        """
        try:
            return self.r.set(data=at.win_set_state(title, flag, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def wait(self, title, text, timeout=5):
        """
        :description 暂停脚本的执行直至指定窗口存在(出现)为止.
        timeout 单位为秒.
        :return PID:成功, 0:失败(超时).
        """
        try:
            return self.r.set(data=at.win_wait(title, timeout, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def wait_active(self, title, text, timeout=5):
        """
        :description 暂停脚本的执行直至指定窗口被激活(成为活动状态)为止.
        timeout 单位为秒.
        :return PID:成功, 0:失败(超时).
        """
        try:
            return self.r.set(data=at.win_wait_active(title, timeout, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def wait_close(self, title, text, timeout=5):
        """
        :description 暂停脚本的执行直至所指定窗口不再存在为止.
        timeout 单位为秒.
        :return 1:成功, 0:失败(超时).
        """
        try:
            return self.r.set(data=at.win_wait_close(title, timeout, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def wait_not_active(self, title, text, timeout=5):
        """
        :description 暂停脚本的执行直至指定窗口不是激活状态为止.
        timeout 单位为秒.
        :return 1:成功, 0:失败(超时).
        """
        try:
            return self.r.set(data=at.win_wait_not_active(title, timeout, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def control_click(self, title, text, control, button, clicks=1):
        """
        :description 向指定控件发送鼠标点击命令.
        """
        try:
            self.activate(title, text)
            result = at.control_click(title, control, text=text, button=button, clicks=clicks)
            return self.r.set(data=result)
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='unknown')

    def control_move(self, title, text, control):
        """
        :description 将鼠标移动到指定元素控件之上
        """
        try:
            result1 = at.win_get_pos(title=title, text=text)
            result2 = at.control_get_pos(title=title, control=control, text=text)
            print(result1)
            print(result2)
            x = int(result1[0] + (result2[0] + result2[2]) / 2)
            y = int(result1[1] + (result2[1] + result2[3]) / 2)
            at.mouse_move(x, y)
            result = at.mouse_get_pos()
            return self.r.set(data=result)
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='unknown')

    def control_command(self, title, text, control, command, extra="", buf_size=256):
        """向指定控件发送命令."""
        """
        :param command, extra:                         :return
                    "IsVisible", ""                    1:可见; 0:不可见
                    "IsEnabled", ""                    1:可用; 0:禁用
                    "ShowDropDown", ""                弹出/下拉 组合框(ComboBox)的列表.
                    "HideDropDown", ""                收回/隐藏 组合框(ComboBox)的列表.
                    "AddString", "string"                在 ListBox 或 ComboBox 的编辑框后面附加指定字符串.
                    "DelString", 出现次序                                删除在 ListBox 或 ComboBox 的编辑框中指定的字符串(从0开始).
                    "FindString", "string"                返回在 ListBox 或 ComboBox 的编辑框中与指定字符串匹配项目的出现次序(从0开始).
                    "SetCurrentSelection", 出现次序            通过指定出现次序(从0开始)把 ListBox 或 ComboBox 的当前选择项设为指定的项目.
                    "SelectString","string"            通过指定字符串把 ListBox 或 ComboBox 的当前选择项设为匹配字符串的项目.
                    "IsChecked", ""                    若目标按钮(复选框/单选框)被选中则返回值为1,否则为0.
                    "Check", ""                        使目标按钮(复选框/单选框)变为选中状态.
                    "UnCheck", ""                        使目标按钮(复选框/单选框)变为非选中状态.
                    "GetCurrentLine", ""                    返回在目标编辑框中插入符(caret,光标)的所在行号.
                    "GetCurrentCol", ""                    返回在目标编辑框中插入符(caret,光标)的所在列号.
                    "GetCurrentSelection", ""                返回 ListBox 或 ComboBox 控件当前选中的项目名.
                    "GetLineCount", ""                        返回目标编辑框中的总行数.
                    "GetLine", 行号                                        返回目标编辑框中指定行的文本内容.
                    "GetSelected", ""                    返回目标编辑框中的(用户用鼠标或其它方式)选定的文本.
                    "EditPaste", 'string'                在目标编辑框中插入符(caret)所在位置后插入指定字符串.
                    "CurrentTab", ""                    返回在 SysTabControl32 控件中当前显示的标签编号(从1开始).
                    "TabRight", ""                        使 SysTabControl32 控件切换到(右边的)下一个标签.
                    "TabLeft", ""                        使 SysTabControl32 控件切换到(左边的)下一个标签.
                    "SendCommandID", 命令 ID            模拟 WM_COMMAND 消息. 通常用于 ToolbarWindow32 控件 - 使用Au3Info的工具栏标签得到命令ID.
        """
        try:
            self.activate(title, text)
            result = at.control_command(title, control, command, buf_size, text=text, extra=extra)
            return self.r.set(data=result)
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='unknown')

    def control_list_view(self, title, text, control, command, extra1, extra2="", buf_size=256):
        """
        :description 向指定的 ListView32 控件发送命令.
         @param title:
        @param text:
        @param control:
        @param command:
        @param extra1:
        @param extra2:
        @param buf_size:
        @return:    "DeSelect", 从[, 到]                        取消选定从"从"开始直到"到"的一个或多个项目.
                    "FindItem", "搜索字符串" [, 子项目]            返回与给定字符串匹配的项目的位置.若未找到指定字符串则返回值为 -1.
                    "GetItemCount"                                返回列表中项目的数量.
                    "GetSelected" [, 选项]                        返回当前选中项目的位置.若 选项=0(默认)则只返回选中的第一个项目;若 选项=1 则返回由竖线"|"作为分隔符的所有选中项目,例如:"0|3|4|10".若没有选中任何项目则返回一个空字符串"".
                    "GetSelectedCount"                            返回选中项目的数量.
                    "GetSubItemCount"                            返回子项目的数量.
                    "GetText", 项目, 子项目                                            返回指定项目/子项目的文本.
                    "IsSelected", 项目                                                    若指定项目被选中则返回值为1,否则返回值为0.
                    "Select", 从[, 到]                            选中一个或多个项目(请参考第一个命令).
                    "SelectAll"                                    选中所有项目.
                    "SelectClear"                                取消所有项目的选中状态.
                    "SelectInvert"                                切换当前的选中状态.
                    "ViewChange", "视图"                        切换当前的视图.可用的视图包括"list"(列表),"details"(详细信息),"smallicons"(小图标),"largeicons"(大图标).
        """
        try:
            self.activate(title, text)
            result = at.control_list_view(title, control, command, buf_size, text=text, extra1=extra1,
                                          extra2=extra2)
            return self.r.set(data=result)
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='unknown')

    def control_disable(self, title, text, control):
        """
        :description 禁用或使某控件变成灰色不可用状态.
        :return 1:成功; 0:失败.
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.control_disable(title, control, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def control_enable(self, title, text, control):
        """
        :description 使灰色按钮/控件变为"可用"状态.
        :return 1:成功; 0:失败.
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.control_enable(title, control, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def control_focus(self, title, text, control):
        """
        :description 设置输入焦点到指定窗口的某个控件上.
        :return 1:成功; 0:失败.
        """
        try:
            return self.r.set(data=at.control_focus(title, control, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def control_get_text(self, title, text, control):
        """
        :description 获取指定控件上的文本.
        :return 文本内容:成功; 空:失败.
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.control_get_text(title, control, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def control_send(self, title='', control='', control_text='', text=''):
        """
        :description 向指定的控件发送字符串.
        :mode: 0:按特殊字符含义发送(默认); 1:原样发送.
        :return 1:成功; 0:失败(窗口/控件未找到).
        """
        try:
            result = at.control_set_text(title=title, control_text=control_text, control=control, text=text)
            # return self.r.set(data=autoit.control_send(title, control, send_text, mode, text=text))
            return self.r.set(data=result)
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def control_set_text(self, title, text, control, control_text):
        """
        :description 修改指定控件的文本.
        :return 1:成功; 0:失败(窗口/控件未找到).
        """
        try:
            self.activate(title, text)
            return self.r.set(data=at.control_set_text(title, control, control_text, text=text))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data=0)

    def control_tree_view(self, title, text, control, command, extra, buf_size=256):
        """
        :description 发送一个命令到 TreeView32 控件.(子节点不好用*)
        @return:
        "Check", "项目"                                             选中一个项目 (如果项目支持选中,这里指项目带有选择框).
        "Collapse", "项目"                                          折叠一个项目节点,使它隐藏它的子项目.
        "Exists", "项目"         *都返回1*                      如果项目存在返回 1,否则返回 0.
        "Expand", "项目"                                           展开一个项目节点,使它显示它的子项目.
        "GetItemCount", "项目"                                 返回所选项目的子项目数量.
        "GetSelected" [, 使用索引]                             返回当前所选项目的文本参考信息(如果使用索引设置为1将会返回所选项目索引位置).
        "GetText", "项目"                                          返回项目文本.
        "IsChecked"                                                  返回项目选中状态. 1:被选中, 0:未被选中, -1:没要选择框.
        "Select", "项目"                                             选择一个项目.
        "Uncheck", "项目"                                         取消项目选中状态 (如果项目支持选中,这里指项目带有选择框).
        """
        try:
            self.activate(title, text)
            result = at.control_tree_view(title, control, command, text=text, buf_size=buf_size,
                                          extra=extra)
            return self.r.set(data=result)
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='unknown')

    def status_bar_get_text(self, title, text, part=1, buf_size=256):
        """
        :description 获取标准状态栏控件的文本.
        :return 文本内容:成功; 空字符串:失败(无法读取文本).
        """
        try:
            self.activate(title, text)
            result = at.statusbar_get_text(title, text, part, buf_size)
            return self.r.set(data=result)
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='')

    def get_tips(self, tips, x, y):
        """
        :description TrayTip其实就是个特殊的窗口(托盘提示)
        :return 文本内容:成功; 空字符串:失败(无法读取文本).
        """
        try:
            return self.r.set(data=at.tooltip(tips, x, y))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='')

    def get_win_class_list(self, title):
        try:
            return self.r.set(data=at.win_get_class_list(title, buf_size=256))
        except Exception as err:
            return self.r.set(code=405, status=False, message=str(err), data='')


from airtest.core.win.win import Windows as AirTestWindows
from airtest.core.api import Template, loop_find


IMG_ACTIONS = Literal[
    'click',
    'touch',
    'double_click',
    'mouse_move',
    # 'move',
]
SIMPLE_ACTIONS = Literal[
    'click',
    'touch',
    'double_click',
    'mouse_move',

    'uuid',
    'connect',
    'snapshot',
    'keyevent',
    'text',
    'key_press',
    'key_release',

    'mouse_down',
    'mouse_up',
    'set_foreground',

    'get_title',
    'get_pos',

    'get_current_resolution',
    'get_ip_address',
]


class WinAirTestAgent:
    """
    AirTest For WinAgent
    """

    def __init__(self):
        self._dev: typing.Optional[AirTestWindows] = None

    @safe_agent
    def start_app(self, path: Path) -> None:
        """
        打开window程序
        :param path: 应启动的路径
        :return:  None
        """
        if not self._dev:
            self._dev = AirTestWindows()
        self._dev.start_app(str(path))

    @safe_agent
    def connect_app_by_title(self, title: str) -> None:
        """
        连接windows窗口
        :param title: 窗口title
        :return:
        """
        from airtest.core.api import connect_device
        self._dev = connect_device(f'Windows:///?title_re={title}')

    @safe_agent
    def connect_device(self, url: str):
        """
        :param url:
        :return:
        """
        from airtest.core.api import connect_device
        self._dev = connect_device(url)

    @safe_agent
    def screen_shot(self, name=None):
        if not self._dev:
            raise Exception('must be connect or start app!')

        if name is None:
            image_name = time.time()
        else:
            image_name = name
        file = os.getcwd() + "/image.temp/{}.png".format(image_name)
        remote = f"http://{ip_util.get_ip()}:8081/api/common/image?image_id={image_name}"
        self._dev.snapshot(file)
        return remote

    @safe_agent
    def active(self):
        """
        激活窗口
        :return:
        """
        self._dev._app.active()

    def run_dev_action(
            self,
            action: SIMPLE_ACTIONS,
            *args,
            **kwargs
    ) -> typing.Any:
        """
        运行Windows类的方法
        :param action:
        :param args:
        :param kwargs:
        :return: Any
        """
        if not self._dev:
            raise Exception('must be connect or start app!')
        attr = getattr(self._dev, action)
        if isinstance(attr, typing.Callable):
            return attr(*args, **kwargs)
        return attr

    safe_run_dev_action = safe_agent(run_dev_action)

    @safe_agent
    def run_action_by_img_temp(
            self,
            action: IMG_ACTIONS,
            img_path: Path,
            **kwargs
    ):
        """
        通过 图片 匹配进行一些操作
        :param img_path: 图片地址
        :param action:
        :return:
        """
        # 1、判断图片是否存在
        if not img_path.exists():
            raise Exception(f'{img_path} is not exists!')

        # import time
        # from polyv.config import Config
        # screen_img = Config.AIRTEST_SNAPSHOT_DIR / f'{int(time.time())}.png'
        # self._dev.snapshot(str(screen_img))
        # 2、通过Template转换为position
        pos = loop_find(Template(str(img_path), **kwargs))
        # 3、操作actions
        return self.run_dev_action(action, pos)

    @safe_agent
    def assert_exists(self, img_path: Path, msg:str ="", kw: typing.Dict ={}):
        from airtest.core.api import assert_exists
        # 1、判断图片是否存在
        if not img_path.exists():
            raise Exception(f'{img_path} is not exists!')

        assert_exists(Template(str(img_path), **kw), msg)

    @safe_agent
    def assert_not_exists(self, img_path: Path, msg: str ="", kw: typing.Dict ={}):
        from airtest.core.api import assert_not_exists
        # 1、判断图片是否存在
        if not img_path.exists():
            raise Exception(f'{img_path} is not exists!')

        assert_not_exists(Template(str(img_path), **kw), msg)

    @safe_agent
    def close_app(self):
        try:
            if self._dev:
                self._dev.kill()
        except Exception as e:
            raise e
        finally:
            self._dev = None


if __name__ == '__main__':
    m = MouseControl()
    w = WinAgent()
    w.activate()
    m.move(500, 650)
    time.sleep(1)
    pass
