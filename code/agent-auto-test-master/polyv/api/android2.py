from fastapi import APIRouter

from polyv.common.data_format import DataFormat
from polyv.scripts.android_bak import AndroidAgent

router = APIRouter()
df = DataFormat()
android = AndroidAgent()


@router.post('/connect', name="链接设备")
def android_connect(device: str = None):
    return android.connect(device)


@router.post('/connect_switch_device', name="切换设备")
def android_switch_connect(device: str = None):
    return android.set_device(device)


#
# @router.get('/device_info', name='获取设备信息')
# def device_info():
#     return 'todo'
#
#
# @router.get('/device_size', name='获取设备尺寸')
# def device_size():
#     return 'todo'
#
#
# @router.post('/push_file', name='推送文件到设备')
# def push_file(src: str, dst: str):
#     return 'todo'
#
#
# @router.post('/pull_file', name='从设备拉取文件')
# def pull_file(src: str, dst: str):
#     return 'todo'
#
#
# @router.post('/install', name="安装app")
# def install_app(url: str):
#     return 'todo'
#
#
# @router.post('/uninstall', name='卸载app')
# def uninstall_app(package_name: str):
#     return 'todo'
#
#
# @router.get('/current_package_name', name='获取当前运行app的包名')
# def current_package_name():
#     return 'todo'


@router.post('/app_open', name='打开app')
def app_open(package_name: str = None, is_clear=True):
    return android.open(package_name, is_clear)


@router.post('/app_stop', name='关闭app')
def app_stop(package_name: str):
    return android.close(package_name)


#
# @router.post('/app_clear', name='清理app缓存')
# def app_clear(package_name: str):
#     return 'todo'
#
#
# @router.post('/wait', name='强制等待')
# def wait(seconds: int):
#     return 'todo'
#
#

@router.post('/swipe_right', name='向右滑动')
def swipe_right():
    return android.swipe_right()


@router.post('/swipe_left', name='向左滑动')
def swipe_left():
    return android.swipe_left()


@router.post('/swipe_down', name='向下滑动')
def swipe_down():
    return android.swipe_down()


@router.post('/swipe_up', name='向上滑动')
def swipe_up():
    return android.swipe_up()


@router.post('/click', name='点击元素')
def click(tag, selector, index: int = 0):
    return android.click(tag, selector, index)


#
#
# @router.post('/long_click', name='长按元素')
# def long_click(tag, selector, index: int = 0):
#     return 'todo'
#
#
# @router.post('/clear', name='清空文本')
# def clear(tag, selector, index: int = 0):
#     return 'todo'


@router.post('/send_keys', name='输入文本')
def send_keys(tag, selector, content, index: int = 0, is_clear: bool = True):
    return android.input(tag, selector, index, content)


#
# @router.post('/screen_on', name='点亮屏幕')
# def screen_on():
#     return 'todo'
#
#
# @router.post('/screen_off', name='熄灭屏幕')
# def screen_off():
#     return 'todo'
#
#
# @router.post('/scroll_beginning', name='划至顶部')
# def scroll_beginning():
#     return 'todo'
#
#
# @router.post('/scroll_end', name='划至底部')
# def scroll_end():
#     return 'todo'
#
#
# @router.post('/press_back', name='返回键')
# def press_back():
#     return 'todo'
#
#
# @router.post('/press_enter', name='enter键')
# def press_enter():
#     return 'todo'
#
#
@router.post('/exists', name='判断元素存在')
def exists(tag, selector, index: int = 0):
    return android.exist(tag, selector, index)


#
#
# @router.post('/watch_context', name='监听弹窗处理')
# def watch_context(context):
#     return 'todo'


@router.get('/get_text', name='获取元素文本内容')
def get_text(tag, selector, index: int = 0):
    return android.get_text(tag, selector, index)


#
# @router.get('/get_toast', name='获取toast')
# def get_toast():
#     return 'todo'
#
#
# @router.post('/drag_to', name='拖拽元素至某位置')
# def drag_to(source_tag, source_selector, target_x, target_y, index: int = 0):
#     return 'todo'
#
#
# @router.post('/pinch_in', name='缩小元素')
# def pinch_in(tag, selector, index: int = 0):
#     return 'todo'
#
#
# @router.post('/pinch_out', name='放大元素')
# def pinch_out(tag, selector, index: int = 0):
#     return 'todo'


@router.post('/screen_shot', name='截屏操作')
def screen_shot():
    return android.take_screen_shot()


#
# @router.post('/assert_text_in', name='判断文本内容在某元素')
# def assert_text_in(text, tag, selector, index: int = 0):
#     return 'todo'
#
#
# @router.post('/assert_text_not_in', name='判断文本内容不在某元素')
# def assert_text_not_in(text, tag, selector, index: int = 0):
#     return 'todo'


@router.post('/adb_shell', name='针对设备进行adb_shell命令')
def adb_shell(cmd):
    return DataFormat().set(message=f'执行指令:[ {cmd} ]', data=android.shell(cmd))


@router.post('/compare_image', name='图片对比')
def comparison_image(image1, image2):
    return android.classify_hist_with_split(image1, image2)

@router.post('/swipe_right', name='向右滑动')
def swipe_right():
    return android.swipe_right()


@router.post('/swipe_left', name='向左滑动')
def swipe_left():
    return android.swipe_left()


@router.post('/swipe_down', name='向下滑动')
def swipe_down():
    return android.swipe_down()


@router.post('/swipe_up', name='向上滑动')
def swipe_up():
    return android.swipe_up()

#
# @router.post('/test_clean', name='清理')
# def test_clean():
#     pass
