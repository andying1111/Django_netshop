#!/usr/bin/evn python
# -*- coding: UTF-8 -*
import pyautogui
import uvicorn
from fastapi import FastAPI

from polyv.common.data_format import DataFormat
from polyv.common.file_util import FileUtils
from polyv.scripts.android import AndroidAgent
from polyv.scripts.web import WebAgent

app = FastAPI()
df = DataFormat()
service = WebAgent()
android = AndroidAgent()


@app.get('/api/status')
def status():
    return service.status()


@app.get("/report")
def see_report(file: str = None):
    return service.get_report(file)


@app.get("/image")
def see_image(image_id: str = None):
    return service.get_image(image_id)


@app.get("/delete/image")
def delete_image(days: int = 7, path: str = None):
    """移除N天以前的图片文件"""
    import os
    if path is None:
        path = os.getcwd() + "/image.temp"
        path = path.replace('agent/api/', '').replace('agent\\api\\', '')
    return FileUtils().remove_files(breday=days, path=path)


""" Web Api  """


# 打开应用(electron)
@app.post('/api/pc/open')
def open_app(app_path: str = None):
    return service.open(app_path)


# 打开浏览器
@app.post('/api/web/open')
def open_url(url: str = None):
    return service.open_url(url)


# 关闭
@app.post('/api/web/close')
def close():
    return service.close()


# 点击元素
@app.post('/api/web/click')
def click(tag: str = None, element: str = None, index: int = None):
    return service.click(tag, element, index)


# 等待元素出现
@app.post('/api/web/wait_element')
def wait(tag: str = None, element: str = None, index: int = -1, times=5):
    return service.wait_element(tag, element, index, times)


# 获取控件文本
@app.get('/api/web/get_text')
def click(tag: str = None, element: str = None, index: int = None):
    return service.get_text(tag, element, index)


# 输入文本
@app.post('/api/web/input_text')
def input_text(tag: str = None, element: str = None, text: str = None, index: int = -1):
    return service.input(tag, element, text, index)


# 判断是否存在
@app.post('/api/web/exist')
def exist(tag: str = None, element: str = None, index: int = -1):
    return service.exist(tag, element, index)


# 切换窗口
@app.post('/api/web/switch_handle')
def switch_handle(index: int = 0):
    return service.switch_handle(index)


# 悬停:鼠标移动到XX元素上
@app.post('/api/web/mouse_to_element')
def move_to_element(tag: str = None, element: str = None, index: int = -1):
    return service.mouse_to_element(tag, element, index)


# 鼠标上次定位位置为起点，鼠标左击或右击坐标
@app.post('/api/web/click_by_offset')
def mouse_offset_click(x: int = 0, y: int = 0, direction: str = 'left'):
    return service.click_offset(x, y, direction)


# 拖拽元素1到元素2位置
@app.post('/api/web/drag_element')
def drag_element(tag1: str = None, source: str = None, tag2: str = None, target: str = None, index1: int = -1,
                 index2: int = -1):
    return service.drag_element(tag1, source, tag2, target, index1, index2)


# 截屏：0=浏览器窗口，1=整个桌面
@app.get('/api/web/screen_shot')
def screen_shot(flog: int = 0, name: str = None):
    return service.screen_shot(flog, name)


@app.post('/api/pc/mouse/move')
def move_point(x: int = 0, y: int = 0, duration: float = 0.0):
    try:
        pyautogui.moveTo(x, y, duration)
        return df.set(data='move to: {},{} ——> success'.format(x, y))
    except Exception as ERR:
        return df.set(code=403, status=False, message=str(ERR), data='API 仅支持Windows系统')


@app.post('/api/pc/mouse/click')
def click_point(x: int = 0, y: int = 0, button: str = 'left', duration: float = 0.0):
    try:
        pyautogui.click(x=x, y=y, button=button, duration=duration)
        return df.set(data='click point: {},{} ——> success'.format(x, y))
    except Exception as ERR:
        return df.set(code=403, status=False, message=str(ERR), data='API 仅支持Windows系统')


@app.post('/api/pc/mouse/doubleClick')
def double_click(x: int = 0, y: int = 0, button: str = 'left', duration: float = 0.0):
    try:
        pyautogui.doubleClick(x=x, y=y, button=button, duration=duration)
        return df.set(data='doubleClick point: {},{} ——> success'.format(x, y))
    except Exception as err:
        return df.set(code=403, status=False, message=str(err))


# 键盘事件
@app.post('/api/pc/keyboard/press')
def press(keys: str = None):
    return service.press(keys)


# 键盘双按键组合事件
@app.post('/api/pc/keyboard/press_combination')
def press_(key1: str = None, key2: str = None):
    return service.press_combination(key1, key2)


#
# """ AutoIt Api """
#
#
# @app.post('/api/pc/autoit/mouse/move')
# def move_to_point(x: int = 0, y: int = 0):
#     try:
#         return mouse.move(x, y)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/mouse/click')
# def click_to_point(x: int = 0, y: int = 0, button: str = 'left', clicks: int = 1, speed: int = -1):
#     try:
#         return mouse.click(x=x, y=y, button=button, clicks=clicks, speed=speed)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/mouse/wheel')
# def autoit_mouse_wheel(direction: str = "up"):
#     try:
#         return mouse.wheel(direction)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/mouse/drag')
# def autoit_mouse_drag(x: int, y: int, x1: int, y1: int):
#     try:
#         return mouse.drag(x, y, x1, y1)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/process/close')
# def autoit_close(process_name: str):
#     try:
#         return process.close(process_name)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/process/exists')
# def autoit_exists(process_name: str):
#     try:
#         return process.exists(process_name)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/activate')
# def autoit_activate(title: str, text: str):
#     try:
#         return win.activate(title=title, text=text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/close')
# def autoit_close(title: str, text: str):
#     try:
#         return win.close(title=title, text=text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.get('/api/pc/autoit/win/exists')
# def autoit_exists(title: str):
#     try:
#         return win.exists(title)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.get('/api/pc/autoit/win/get_pos')
# def autoit_get_pos(title: str, text: str):
#     try:
#         return win.get_pos(title, text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.get('/api/pc/autoit/win/get_process')
# def autoit_get_process(title: str, text: str):
#     try:
#         return win.get_process(title, text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.get('/api/pc/autoit/win/get_text')
# def autoit_get_text(title: str, text: str):
#     try:
#         return win.get_text(title, text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/kill')
# def autoit_win_kill(title: str, text: str):
#     try:
#         return win.kill(title, text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/set')
# def autoit_win_set(title: str, text: str, x: int = 0, y: int = 0, w: int = 0, h: int = 0):
#     try:
#         return win.set(title, text, x, y, w, h)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/set_status')
# def autoit_win_set_state(title: str, text: str, value: int = 1):
#     try:
#         return win.set_state(title, text, value)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/wait')
# def autoit_win_wait(title: str, text: str, times: int = 5):
#     try:
#         return win.wait(title, text, times)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/wait_active')
# def autoit_win_wait_active(title: str, text: str, times: int = 5):
#     try:
#         return win.wait_active(title, text, times)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/wait_not_active')
# def autoit_win_wait_not_active(title: str, text: str, times: int = 5):
#     try:
#         return win.wait_not_active(title, text, times)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_click')
# def autoit_win_control_click(title: str, text: str, control: str, button: str, clicks: int = 1):
#     try:
#         return win.control_click(title, text, control, button, clicks)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_move')
# def autoit_win_control_move(title, text, control):
#     try:
#         return win.control_move(title, text, control)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_disable')
# def autoit_win_control_disable(title: str, text: str, control: str):
#     try:
#         return win.control_disable(title, text, control)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_enable')
# def autoit_win_control_enable(title: str, text: str, control: str):
#     try:
#         return win.control_enable(title, text, control)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_focus')
# def autoit_win_control_focus(title: str, text: str, control: str):
#     try:
#         return win.control_focus(title, text, control)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.get('/api/pc/autoit/win/control_get_text')
# def autoit_win_control_get_text(title: str, text: str, control: str):
#     try:
#         return win.control_get_text(title, text, control)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_send')
# def autoit_win_control_send(title: str = '', control: str = '', control_text: str = '', text: str = ''):
#     try:
#         return win.control_send(title, control, control_text, text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_find')
# def autoit_win_control_find(title: str = '', control: str = '', text: str = ''):
#     try:
#         return win.control_focus(title, control, text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_set_text')
# def autoit_win_control_set_text(title: str, text: str, control: str, control_text: str):
#     try:
#         return win.control_set_text(title, text, control, control_text)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_tree_view')
# def autoit_win_control_tree_view(title: str, text: str, control: str, command: str, extra: str = "", buf_size=256):
#     try:
#         return win.control_tree_view(title, text, control, command, extra, buf_size)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.get('/api/pc/autoit/win/status_bar_get_text')
# def autoit_win_status_bar_get_text(title: str, text: str, part: str = 1, buf_size=256):
#     try:
#         return win.status_bar_get_text(title, text, part, buf_size)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.get('/api/pc/autoit/win/get_tips')
# def autoit_win_get_tips(tips: str, x: int = 0, y: int = 0):
#     try:
#         return win.get_tips(tips, x, y)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_command')
# def autoit_win_control_command(title: str, text: str, control: str, command: str, extra: str = "", buf_size=256):
#     try:
#         return win.control_command(title, text, control, command, extra, buf_size)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# @app.post('/api/pc/autoit/win/control_list_view')
# def autoit_win_control_list_view(title: str, text: str, control: str, command: str, extra1, extra2="", buf_size=256):
#     try:
#         return win.control_list_view(title, text, control, command, extra1, extra2, buf_size)
#     except Exception as err:
#         return rf.set(code=403, status=False, message=str(err), data='API 仅支持Windows系统')
#
#
# """ Android Api """
#
#
# @app.post('/api/android/waitNoExitByClazz')
# def wait_not_by_clazz(clazz, index):
#     return android.wait_not_by_clazz(clazz, index)
#
#
# @app.post('/api/android/waitNoExitByDesc')
# def wait_not_by_desc(desc):
#     return android.wait_not_by_desc(desc)
#
#
# @app.post('/api/android/waitNoExitByText')
# def wait_not_by_text(text):
#     return android.wait_not_by_text(text)
#
#
# @app.post('/api/android/waitNoExitById')
# def wait_not_by_id(ids):
#     return android.wait_not_by_id(ids)
#
#
# @app.post('/api/android/assertByClazz')
# def assert_exit_by_clazz(clazz, index):
#     return android.assert_exit_by_clazz(clazz, index)
#
#
# @app.post('/api/android/assertByDesc')
# def assert_exit_by_desc(desc):
#     return android.assert_exit_by_desc(desc)
#
#
# @app.post('/api/android/assertByText')
# def assert_exit_by_text(text):
#     return android.assert_exit_by_text(text)
#
#
# @app.post('/api/android/assertById')
# def assert_exit_by_id(ids):
#     return android.assert_exit_by_id(ids)
#
#
# @app.post('/api/android/clickPoint')
# def click_point(x: str, y):
#     return android.click_point(x, y),
#
#
# @app.post('/api/android/longClickByClazz')
# def long_click_by_clazz(clazz: str, index):
#     return android.long_click_by_clazz(clazz, index),
#
#
# @app.post('/api/android/longClickByDesc')
# def long_click_by_desc(desc: str):
#     return android.long_click_by_desc(desc)
#
#
# @app.post('/api/android/longClickByText')
# def long_click_by_text(text: str):
#     return android.long_click_by_text(text)
#
#
# @app.post('/api/android/longClickById')
# def long_click_by_id(ids: str):
#     return android.long_click_by_id(ids)
#
#
# @app.post('/api/android/pressMenu')
# def press_menu():
#     return android.press_menu()
#
#
# @app.post('/api/android/pressBack')
# def press_back():
#     return android.press_back()
#
#
# @app.post('/api/android/pressHome')
# def press_home():
#     return android.press_home()
#
#
# @app.post('/api/android/swipeByPoint')
# def swipe_by_point(start_x: int, start_y: int, end_x: int, end_y: int):
#     return android.swipe_by_point(start_x, start_y, end_x, end_y)
#
#
# @app.post('/api/android/swipeRight')
# def swipe_right():
#     return android.swipe_right()
#
#
# @app.post('/api/android/swipeLeft')
# def swipe_left():
#     return android.swipe_left()
#
#
# @app.post('/api/android/swipeDown')
# def swipe_down():
#     return android.swipe_down()
#
#
# @app.post('/api/android/swipeUp')
# def swipe_up():
#     return android.swipe_up()
#
#
# @app.post('/api/android/inputByClazz')
# def input_by_clazz(clazz: str, text: str, index: int):
#     return android.input_by_clazz(clazz, text, index)
#
#
# @app.post('/api/android/inputByPackage')
# def input_by_package(package: str, text: str, index: int):
#     return android.input_by_package(package, text, index)
#
#
# @app.post('/api/android/inputByDesc')
# def input_by_decs(desc: str, text: str):
#     return android.input_by_desc(desc, text)
#
#
# @app.post('/api/android/inputById')
# def input_by_id(ids: str, text: str):
#     return android.input_by_id(ids, text)
#
#
# @app.post('/api/android/inputByText')
# def input_by_text(param: str, text: str):
#     return android.input_by_text(param, text)
#
#
# @app.post('/api/android/clickByPackage')
# def click_by_package(package: str, index: int):
#     return android.click_by_package(package, index)
#
#
# @app.post('/api/android/clickByClazz')
# def click_by_clazz(clazz: str, index: int):
#     return android.click_by_clazz(clazz, index)
#
#
# @app.post('/api/android/clickByDesc')
# def click_by_desc(desc: str):
#     return android.click_by_desc(desc)
#
#
# @app.post('/api/android/clickByTest')
# def click_by_text(text: str):
#     return android.click_by_text(text)
#
#
# @app.post('/api/android/clickById')
# def click_by_id(ids: str):
#     return android.click_by_id(ids)
#
#
# @app.post('/api/android/clickByText')
# def click_by_text(text: str):
#     return android.click_by_text(text)
#
#
# ================================================= Android api
@app.post('/api/android/connect')
def android_connect(device: str):
    return android.connedunct(device)


@app.post('/api/android/control/device')
def android_connect(device: str):
    return android.set_device(device)


@app.post('/api/android/disconnect')
def android_disconnect(device: str):
    return android.disconnect(device)


@app.get('/api/android/get_text')
def android_click(tag: str = 'text', element: str = '', index: int = -1):
    return android.get_text(tag, element, index)


@app.post('/api/android/click')
def android_click(tag: str = 'text', element: str = '', index: int = -1):
    return android.click(tag, element, index)


@app.post('/api/android/input_text')
def android_input(tag: str = 'text', element: str = '', index: int = -1, text=''):
    return android.input(tag, element, index, text)


@app.post('/api/android/open')
def open_app(package, clear):
    return android.open(package, clear)


@app.post('/api/android/close')
def close_app(package):
    return android.close(package)


@app.get('/api/android/take_screen_shot')
def take_screen_shot(tag: bool = False):
    if tag:
        return android.get_action_screen_shot()
    else:
        return android.take_screen_shot()


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8081, workers=1)
    pass
