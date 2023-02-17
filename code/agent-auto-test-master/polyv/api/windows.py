import os
import typing
import functools

from fastapi import APIRouter, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, FilePath

from polyv.common.data_format import DataFormat
from polyv.scripts.windows import WinAirTestAgent as WinAgent, Literal
from polyv.config import Config

router = APIRouter()
window = WinAgent()


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


@router.post('/start_app', response_model=DataResponse)
@data2resp
def start_app(path: FilePath = Query(..., example=r'C:\PolyvLive64\bin\64bit\polyvlive64.exe')) -> DataFormat:
    """
    启动一个app
    """
    return window.start_app(path)


@router.post('/active', response_model=DataResponse)
@data2resp
def active():
    """
    激活app窗口
    """
    return window.active()


@router.post('/close_app', response_model=DataResponse)
@data2resp
def close_app() -> DataFormat:
    """
    关闭当前app
    """
    return window.close_app()

@router.post('/test_clean', response_model=DataResponse)
@data2resp
def test_clean() -> DataFormat:
    """
    服务端调用，统一函数名
    """
    return window.close_app()


@router.post('/connect_app_by_title')
@data2resp
def connect_app_by_title(title: str = Query(..., example='云直播*')):
    """
    通过 title 连接app窗口, 可用re
    """
    return window.connect_app_by_title(title)


@router.post('/connect_device')
@data2resp
def connect_device(url: str = Query(..., example='Windows:///')):
    return window.connect_device(url)


@router.get('/uuid')
@data2resp
def app_uuid():
    """
    获取窗口的UUID, 即句柄, plolyvclient拿不到
    """
    return window.safe_run_dev_action('uuid')


@router.post('/connect')
@data2resp
def connect_app_by_handle(handle: str = Query(...)):
    """
    通过 窗口句柄 连接app窗口
    """
    return window.safe_run_dev_action('connect', handle=handle)


@router.post('/screen_shot')
@data2resp
def screen_shot(name: str = None):
    return window.screen_shot(name)


@router.post('/keyevent')
@data2resp
def keyevent(keyname: str = Query(..., example='{CAPSLOCK}')):
    """
    执行一个按键响应
    详情参考： https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html
    """
    return window.safe_run_dev_action('keyevent', keyname)


@router.post('/input_text')
@data2resp
def text(text: str = Query(..., example='123123')):
    """
    Input text
    """
    return window.safe_run_dev_action('text', text)


@router.post('/key_press')
@data2resp
def key_press(key: str = Query(...)):
    """
    模拟一个按下按键的事件。
    https://airtest.readthedocs.io/zh_CN/latest/all_module/airtest.core.win.win.html#airtest.core.win.win.Windows.key_press
    """
    return window.safe_run_dev_action('key_press', key)


@router.post('/key_release')
@data2resp
def key_release(key: str = Query(...)):
    """
    模拟一个释放按键的事件。
    https://airtest.readthedocs.io/zh_CN/latest/all_module/airtest.core.win.win.html#airtest.core.win.win.Windows.key_release
    """
    return window.safe_run_dev_action('key_release', key)


@router.post('/mouse_down')
@data2resp
def mouse_down(button: Literal['left', 'middle', 'right'] = Query('left')):
    """
    触发鼠标按下事件
    """
    return window.safe_run_dev_action('mouse_down', button)


@router.post('/mouse_up')
@data2resp
def mouse_up(button: Literal['left', 'middle', 'right'] = Query('left')):
    """
    触发鼠标按下事件
    """
    return window.safe_run_dev_action('mouse_up', button)


# @router.post('/set_foreground')
# @data2resp
# def set_foreground():
#     """
#     Bring the window foreground
#     """
#     return window.safe_run_dev_action('set_foreground')


# @router.get('/title')
# @data2resp
# def get_title():
#     """
#     Get the window title
#     """
#     return window.safe_run_dev_action('get_title')


@router.get('/pos')
@data2resp
def get_pos():
    """
    get pos
    """
    return window.safe_run_dev_action('get_pos')


@router.get('/current_resolution')
@data2resp
def get_current_resolution():
    """
    获取当前分辨率
    """
    return window.safe_run_dev_action('get_current_resolution')


@router.get('/ip_address')
@data2resp
def get_ip_address():
    return window.safe_run_dev_action('get_ip_address')


if not Config.AIRTEST_IMG_DIR.exists():
    os.mkdir(Config.AIRTEST_IMG_DIR)

if not Config.AIRTEST_SNAPSHOT_DIR.exists():
    os.mkdir(Config.AIRTEST_SNAPSHOT_DIR)


@router.get('/images')
@data2resp
def get_airtest_images():
    """
    获取图片列表
    """
    return DataFormat().set(
        data=[
            os.listdir(Config.AIRTEST_IMG_DIR)
        ]
    )


# class TemplateArgs(BaseModel):
#
#     threshold: typing.Optional[float] = 0.7
#     target_pos: typing.Optional[int] = 5
#     record_pos: typing.List[float] = None
#     # resolution: typing.Tuple[int] = ()
#     rgb: typing.Optional[bool] = False
#     scale_max: typing.Optional[float] = 800
#     scale_step: typing.Optional[float] = 0.01
#
#     def get_temp_args(self):
#         d = self.dict()
#         del d['image']
#         return {k: v for k, v in d.items() if v}
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "image": r'denglu.png',
#                 "threshold": 0.9,
#                 "target_pos": 5,
#                 "record_pos": (0.0, 0.516),
#                 "resolution": (320, 450),
#                 "rgb": False,
#                 "scale_max": 800,
#                 "scale_step": 0.02
#             }
#         }


@router.post('/click')
@data2resp
def click(
        image: str = Query(..., example='login.png'),
        threshold: typing.Optional[float] = 0.7,
        target_pos: typing.Optional[int] = 5,
        record_pos: typing.List[float] = None,
        # resolution: typing.Tuple[int] = (),
        
        rgb: typing.Optional[bool] = False,
        scale_max: typing.Optional[float] = 800,
        scale_step: typing.Optional[float] = 0.01
):
    """
    单击图片位置
    """
    return window.run_action_by_img_temp(
        'touch',
        Config.AIRTEST_IMG_DIR / image,
        threshold=threshold,
        target_pos=target_pos,
        record_pos=record_pos,
        # resolution=resolution,
        rgb=rgb,
        scale_max=scale_max,
        scale_step=scale_step
    )


@router.post('/double_click')
@data2resp
def double_click(
        image: str = Query(..., example='login.png'),
        threshold: typing.Optional[float] = 0.7,
        target_pos: typing.Optional[int] = 5,
        record_pos: typing.List[float] = None,
        # resolution: typing.Tuple[int] = (),
        rgb: typing.Optional[bool] = False,
        scale_max: typing.Optional[float] = 800,
        scale_step: typing.Optional[float] = 0.01
):
    """
    双击图片位置
    """
    return window.run_action_by_img_temp(
        'double_click',
        Config.AIRTEST_IMG_DIR / image,
        threshold=threshold,
        target_pos=target_pos,
        record_pos=record_pos,
        # resolution=resolution,
        rgb=rgb,
        scale_max=scale_max,
        scale_step=scale_step
    )


@router.post('/mouse_move')
@data2resp
def mouse_move(
        image: str = Query(..., example='login.png'),
        threshold: typing.Optional[float] = 0.7,
        target_pos: typing.Optional[int] = 5,
        record_pos: typing.List[float] = None,
        # resolution: typing.Tuple[int] = (),
        rgb: typing.Optional[bool] = False,
        scale_max: typing.Optional[float] = 800,
        scale_step: typing.Optional[float] = 0.01
):
    """
    鼠标移动到图片位置
    """
    return window.run_action_by_img_temp(
        'mouse_move',
        Config.AIRTEST_IMG_DIR / image,
        threshold=threshold,
        target_pos=target_pos,
        record_pos=record_pos,
        # resolution=resolution,
        rgb=rgb,
        scale_max=scale_max,
        scale_step=scale_step
    )


# class AssertModel(TemplateArgs):
#     assert_msg: str = ""
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "image": r'denglu.png',
#                 "threshold": 0.9,
#                 "target_pos": 5,
#                 "record_pos": (0.0, 0.516),
#                 "resolution": (320, 450),
#                 "rgb": False,
#                 "scale_max": 800,
#                 "scale_step": 0.02,
#                 "assert_msg": "",
#             }
#         }


@router.post('/assert_exists')
@data2resp
def assert_exists(
        assert_msg: str = Query(...),
        image: str = Query(..., example='login.png'),
        threshold: typing.Optional[float] = 0.7,
        target_pos: typing.Optional[int] = 5,
        record_pos: typing.List[float] = None,
        # resolution: typing.Tuple[int] = (),
        rgb: typing.Optional[bool] = False,
        scale_max: typing.Optional[float] = 800,
        scale_step: typing.Optional[float] = 0.01
):
    """
    图片断言 存在
    """
    return window.assert_exists(
        Config.AIRTEST_IMG_DIR / image,
        msg=assert_msg,
        kw={
            'threshold': threshold,
            'target_pos': target_pos,
            'record_pos': record_pos,
            # 'resolution': resolution,
            'rgb': rgb,
            'scale_max': scale_max,
            'scale_step': scale_step
        }
    )


@router.post('/assert_not_exists')
@data2resp
def assert_not_exists(
        assert_msg: str = Query(...),
        image: str = Query(..., example='login.png'),
        threshold: typing.Optional[float] = 0.7,
        target_pos: typing.Optional[int] = 5,
        record_pos: typing.List[float] = None,
        # resolution: typing.Tuple[int] = (),
        rgb: typing.Optional[bool] = False,
        scale_max: typing.Optional[float] = 800,
        scale_step: typing.Optional[float] = 0.01
):
    """
    图片断言不存在
    """
    return window.assert_not_exists(
        Config.AIRTEST_IMG_DIR / image,
        msg=assert_msg,
        kw={
            'threshold': threshold,
            'target_pos': target_pos,
            'record_pos': record_pos,
            # 'resolution': resolution,
            'rgb': rgb,
            'scale_max': scale_max,
            'scale_step': scale_step
        }
    )


router.mount('/image', StaticFiles(directory=str(Config.AIRTEST_IMG_DIR)))

