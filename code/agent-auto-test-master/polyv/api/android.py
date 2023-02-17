from polyv.common.data_format import DataFormat
from polyv.scripts.android import AndroidAgent
from fastapi import APIRouter

router = APIRouter()
df = DataFormat()
android = AndroidAgent()


@router.post('/connect', name="链接设备")
def android_connect(device: str = None):
    return android.connect(device)


@router.post('/connect_atx_addr', name="链接设备")
def connect_atx_addr(addr):
    return android.connect_atx_addr(addr)


@router.post('/connect_adb_wifi', name="链接设备")
def android_connect_adb_wifi(wifi_addr: str = None):
    return android.connect_adb_wifi(wifi_addr)


@router.get('/device_info', name='获取设备信息')
def device_info():
    return android.device_info()


@router.get('/device_size', name='获取设备尺寸')
def device_size():
    return android.device_size()


@router.post('/push_file', name='推送文件到设备')
def push_file(src: str, dst: str):
    return android.push_file(src, dst)


@router.post('/pull_file', name='从设备拉取文件')
def pull_file(src: str, dst: str):
    return android.pull_file(src, dst)


@router.post('/install', name="安装app")
def install_app(url: str):
    return android.install_app(url)


@router.post('/uninstall', name='卸载app')
def uninstall_app(package_name: str):
    return android.uninstall_app(package_name)


@router.get('/current_package_name', name='获取当前运行app的包名')
def current_package_name():
    return android.current_package_name()


@router.post('/app_open', name='打开app')
def app_open(package_name: str = None, app_name: str = None, is_clear=True):
    return android.app_open(package_name, app_name, is_clear)


@router.post('/app_stop', name='关闭app')
def app_stop(package_name: str):
    return android.app_stop(package_name)


@router.post('/app_clear', name='清理app缓存')
def app_clear(package_name: str):
    return android.app_clear(package_name)


@router.post('/wait', name='强制等待')
def wait(seconds: int):
    return android.wait(seconds)


@router.post('/swipe_left', name='左划app')
def swipe_left(scale: float = None):
    return android.swipe_left(scale)


@router.post('/swipe_right', name='右划app')
def swipe_right(scale: float = None):
    return android.swipe_right(scale)


@router.post('/swipe_up', name='上划app')
def swipe_up(scale: float = None):
    return android.swipe_up(scale)


@router.post('/swipe_down', name='下划app')
def swipe_down(scale: float = None):
    return android.swipe_down(scale)


@router.post('/click', name='点击元素')
def click(tag, selector, index: int = 0):
    return android.click(tag, selector, index)


@router.post('/double_click', name='双击屏幕')
def double_click(x, y, duration: float = 0.5):
    return android.double_click(x, y, duration)


@router.post('/long_click', name='长按元素')
def long_click(tag, selector, index: int = 0):
    return android.long_click(tag, selector, index)


@router.post('/clear', name='清空文本')
def clear(tag, selector, index: int = 0):
    return android.clear(tag, selector, index)


@router.post('/send_keys', name='输入文本')
def send_keys(tag, selector, content, index: int = 0, is_clear: bool = True):
    return android.send_keys(tag, selector, content, index, is_clear)


@router.post('/screen_on', name='点亮屏幕')
def screen_on():
    return android.screen_on()


@router.post('/screen_off', name='熄灭屏幕')
def screen_off():
    return android.screen_off()


@router.post('/scroll_beginning', name='划至顶部')
def scroll_beginning():
    return android.scroll_beginning()


@router.post('/scroll_end', name='划至底部')
def scroll_end():
    return android.scroll_end()


@router.post('/press_back', name='返回键')
def press_back():
    return android.press_back()


@router.post('/press_enter', name='enter键')
def press_enter():
    return android.press_enter()


@router.post('/press', name='press')
def press(value):
    return android.press(value)


@router.post('/send_action', name='send-action')
def send_action(code):
    return android.send_action(code)


@router.post('/set_ime', name='set-ime')
def set_ime(enable=True):
    return android.set_ime(enable)


@router.get('/get_ele_info', name='set-ime')
def get_ele_info(tag, selector, index: int = 0):
    return android.get_ele_info(tag, selector, index)


@router.post('/exists', name='判断元素存在')
def exists(tag, selector, index: int = 0):
    return android.exists(tag, selector, index)


@router.post('/watch_context', name='监听弹窗处理')
def watch_context(context):
    return android.watch_context(context)


@router.get('/get_text', name='获取元素文本内容')
def get_text(tag, selector, index: int = 0):
    return android.get_text(tag, selector, index)


@router.get('/get_toast', name='获取toast')
def get_toast():
    return android.get_toast()


@router.post('/drag_to', name='拖拽元素至某位置')
def drag_to(source_tag, source_selector, target_x, target_y, index: int = 0):
    return android.drag_to(source_tag, source_selector, target_x, target_y, index)


@router.post('/pinch_in', name='缩小元素')
def pinch_in(tag, selector, index: int = 0):
    return android.pinch_in(tag, selector, index)


@router.post('/pinch_out', name='放大元素')
def pinch_out(tag, selector, index: int = 0):
    return android.pinch_out(tag, selector, index)


@router.post('/screen_shot', name='截屏操作')
def screen_shot(name: str = None):
    return android.screen_shot(name)


@router.post('/assert_text_in', name='判断文本内容在某元素')
def assert_text_in(text, tag, selector, index: int = 0):
    return android.assertTextin(text, tag, selector, index)


@router.post('/assert_text_not_in', name='判断文本内容不在某元素')
def assert_text_not_in(text, tag, selector, index: int = 0):
    return android.assertTextNotin(text, tag, selector, index)


@router.post('/adb_shell', name='针对设备进行adb_shell命令')
def adb_shell(cmd):
    return android.adb_shell(cmd)


@router.post('/switch_webdriver', name='switch_webdriver')
def switch_webdriver(webdriver_version, device_ip=None):
    return android.switch_webdriver(webdriver_version, device_ip)


@router.post('/webview_get_handles', name='switch_webdriver')
def webview_get_handles():
    return android.webview_get_handles()


@router.get('/webview_click', name="webview点击元素")
def webview_click(tag, element, timeout=30, index=0):
    return android.webview_click(tag, element, timeout, index)


@router.get('/webview_loop_wait_element_exist', name="webview循环等待元素存在")
def webview_loop_wait_element_exist(tag, element, timeout:int=30):
    return android.webview_loop_wait_element_exist(tag, element, timeout)


@router.get('/webview_loop_wait_element_not_exist', name="webview循环等待元素存在")
def webview_loop_wait_element_not_exist(tag, element, timeout:int=30):
    return android.webview_loop_wait_element_not_exist(tag, element, timeout)


@router.get('/webview_send_keys', name="webview输入文本")
def webview_send_keys(tag, element, value, timeout=30, index=0):
    return android.webview_send_keys(tag, element, value, timeout, index)


@router.get('/webview_get_attribute', name="get_attribute")
def webview_attribute(tag, element, attribute_name, timeout, index):
    return android.webview_get_attribute(tag, element, attribute_name, timeout, index)


@router.get('/webview_switch_handle', name="webview_switch_handle")
def webview_attribute(window_title, _type='equal'):
    return android.webview_switch_handle(window_title, _type)


@router.post('/webview_element_screen_shot', name='元素截图')
def element_screen_shot(element, tag, timeout=60, name=None, index=0):
    return android.element_screenshot(tag, element, timeout, name, index)


@router.get('/webview_refresh', name='刷新页面')
def webview_refresh():
    return android.webview_refresh()


@router.get('/webview_execute_js', name='执行js')
def webview_execute_js(js_code):
    return android.webview_execute_js(js_code)


@router.get('/webview_delete_all_cookies', name='删除所有的cookies')
def webview_delete_all_cookies():
    return android.webview_delete_all_cookies()


@router.get('/webview_get_elements_num', name='获取元素个数')
def webview_get_elements_num(tag, element, delay):
    return android.webview_get_elements_num(tag, element, delay)


@router.get('/webview_get_element_size', name="webview获取元素尺寸")
def webview_get_element_size(tag, element, timeout=30, index=0):
    return android.webview_get_element_size(tag, element, timeout, index)


@router.get('/webview_drop_element_by_offset', name="拖拽元素")
def webview_drop_element_by_offset(tag, element, timeout=30, index=0, x_offset=0, y_offset=0):
    return android.webview_drop_element_by_offset(tag, element, timeout, index, x_offset, y_offset)


@router.get('/webview_get_current_handle', name="获取current_handle")
def webview_get_current_handle():
    return android.webview_get_current_handle()


@router.get('/webview_get_current_title', name="获取webview_get_current_title")
def webview_get_current_title():
    return android.webview_get_current_title()


@router.get('/webview_get_page_source', name="获取webview_get_page_source")
def webview_get_page_source():
    return android.webview_get_page_source()


@router.get('/webview_get_current_url', name="获取webview_get_current_url")
def webview_get_current_url():
    return android.webview_get_current_url()


@router.get('/webview_switch_to_iframe', name="获取webview_get_current_url")
def webview_switch_to_iframe(tag, element, timeout=30, index=0):
    return android.webview_switch_to_iframe(tag, element, timeout, index)


@router.get('/webview_switch_to_default_content', name="webview_switch_to_default_content")
def webview_switch_to_default_content():
    return android.webview_switch_to_default_content()


@router.post('/test_clean', name='清理')
def test_clean():
    pass
