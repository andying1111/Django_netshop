"""
@Author  :  Bobby
@Date    :  26/01/2022 15:02
@Desc    :
"""
import functools
import os
import typing
import urllib.parse

from fastapi import APIRouter, Form
from pydantic import BaseModel

from polyv.common.data_format import DataFormat
from polyv.scripts.intelligent import ImageLocation

cp = os.path.abspath(os.path.dirname(__file__))
image_path = cp[:cp.find("agent-auto-test\\") + len("agent-auto-test\\")] + 'temp\\'

router = APIRouter()
df = DataFormat()
at = ImageLocation()


class DataResponse(BaseModel):
    code: int
    status: bool
    message: typing.Text
    data: typing.Any


def data2resp(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        return DataResponse(
            code=data.code,
            status=data.status,
            message=data.message,
            data=data.data
        )

    return _wrapper


@router.post('/open', name='打开windows应用程序', response_model=DataResponse)
@data2resp
def open(path: str = Form(...)):
    return at.open(path)


@router.post('/close', name='关闭windows应用程序')
def close(app_name: str = Form(...)):
    return at.close(app_name)


@router.post('/click', name='通过图片定位并点击')
def click(image: str = Form(...), index: int = Form(default=0)):
    return at.click(image, index)


@router.post('/AiClick', name='通过画面识别文字所在坐标位置')
def ai_click1(element: str = Form(...), event: str = Form(default='left-click'), index: int = Form(default=0),
              contains: bool = Form(default=False), mobile_id: str = Form(default=None),
              mobile_type: str = Form(default=None), offset: str = Form(default='middle')):
    return at.ai_click(element, event, index, contains, mobile_id, mobile_type, offset)


@router.post('/ai_click', name='智能识别定位')
def ai_click(element: str = Form(...), position: str = Form(default='[0, 10]'), mobile_id: str = Form(default=None),
             platform: str = Form(default='win')):
    element = urllib.parse.unquote(element).replace('&position', '')
    return at.distinguish(element, platform, position, mobile_id)


@router.post('/click_point', name='点击坐标位置')
def ai_click(x: str = Form(default="1"), y: str = Form(default="1")):
    return at.click_point(int(x), int(y))


@router.post('/double_click', name='通过图片定位并双击')
def double_click(image: str = Form(...)):
    return at.double_click(image)


@router.post('/right_click', name='通过图片定位并右击')
def right_click(image: str = Form(...)):
    return at.right_click(image)


@router.post('/send_text', name='输入文本（支持中文）')
def send_text(text: str = Form(...)):
    return at.input(text)


@router.post('/send_text2', name='模拟键盘输入')
def send_text2(text: str = Form(...)):
    return at.input_text2(text)


@router.post('/drags', name='拖拽绘制')
def drags(boxs: str = Form(...), duration: float = Form(default=0.2), button: str = Form(default='left')):
    return at.drags(boxs=boxs, duration=duration, button=button)


@router.post('/move', name='移动鼠标')
def move_to(x: int = Form(...), y: int = Form(...)):
    return at.move_to(x, y)


@router.post('/move_to_image', name='移动鼠标悬浮到图片元素')
def move_to_by_image(image: str = Form(...)):
    return at.move_to_by_image(image)


@router.post('/screenshot_as_base64', name='截屏返回base64格式数据')
def screenshot_as_base64(platform: str = Form(...), alias: str = Form(default=None), device: str = Form(default=None)):
    return at.screenshot_as_base64(platform, alias, device)


@router.post('/press_keyboard', name='模拟用户输入单个键')
def press_keyboard(key: str = Form(...)):
    return at.press_keyboard(key)


@router.post('/press_keyboard2', name='通过模拟键盘输入，只触发单个键')
def press_keyboard2(key: str = Form(...)):
    return at.press_keyboard(key)


@router.post('/press_keyboards', name='通过模拟键盘输入，可以支持组合按键，例如：shift+a [参数字段都是keys，至少2个]')
def press_keyboards(keys: list = Form(...)):
    return at.press_keyboards(*keys)


@router.post('/get_text', name='通过图像识别文字 [chi_sim、eng]')
def get_text(image: str = Form(...), lang: str = Form(...)):
    return at.get_text(image, lang)


@router.post('/get_text2', name='通过图像识别文字[内置识别库]')
def get_text2(image: str = Form(...)):
    return at.get_text2(image)


@router.post('/get_text_by_location', name='识别指定区域的文字')
def get_text2(x: int = Form(...), y: int = Form(...), w: int = Form(...), h: int = Form(...), lang: str = Form(...)):
    return at.get_location_text((x, y, w, h), lang)


@router.post('/screen_shot', name='全屏截屏')
def screenshot():
    return at.screenshot()


@router.post('/screenshot_region', name='区域截屏')
def screenshot(x: int = Form(...), y: int = Form(...), w: int = Form(...), h: int = Form(...)):
    return at.screenshot_region((x, y, w, h))


@router.post('/get_position', name='图像匹配，并返回坐标位置')
def get_position(image: str = Form(...)):
    return at.image_recognition_location(image)


@router.get('/get_mouse_position', name='获取鼠标当前所在坐标位置')
def get_mouse_position():
    return at.get_mouse_position()


@router.post('/exists', name='判断图片是否存在')
def exists(image, time_out=0):
    return at.exists(image, int(time_out))


@router.post('/wait_element_appear', name='等待图片出现')
def wait_by_locator_id(image: str = Form(...), wait_time: int = Form(...)):
    return at.wait_element_appear(image, wait_time)
