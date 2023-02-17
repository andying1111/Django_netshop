# coding=utf-8

from polyv.common.data_format import DataFormat
from polyv.scripts.ios import IOSAgent
from fastapi import APIRouter

router = APIRouter()
df = DataFormat()
ios = IOSAgent()


@router.post('/connect_url', name='通过URL连接设备')
def connect_device_url(address='localhost', port=8100):
    return ios.url_connect(adr=address, port=port)


@router.post('/connect_usb', name='通过USB连接设备')
def connect_device_usb(udid=None, port=8100):
    return ios.usb_connect(udid, port)


@router.post('/disconnect', name='断开设备连接')
def disconnect_device():
    return ios.disconnect()


@router.post('/turn_home', name='返回桌面')
def sys_return_home():
    return ios.home()


@router.post('/lock_iphone', name='锁定屏幕')
def sys_lock_iphone():
    return ios.lock()


@router.post('/unlock_iphone', name='解锁屏幕')
def sys_unlock_iphone():
    return ios.unlock()


@router.post('/screen_shot', name='手机截屏')
def sys_screenshot(filename=None):
    """
    IOS-截图方法
    """
    return ios.screenshot_and_save(filename)


@router.get('/page_source', name='page-source')
def page_source():
    """
    IOS-page-source
    """
    return ios.page_source()


@router.post('/wait', name='睡眠等待')
def sys_time_sleep(timeout):
    """
    睡眠等待（非智能等待）
    """
    return ios.wait(timeout)


@router.post('/open_app', name='打开app')
def open_app(package_bundle_id):
    return ios.open_app(package_bundle_id)


@router.post('/open_browser_app', name='打开浏览器并跳转到相应页面')
def open_browser_with_url(browser_bundle_id, url):
    return ios.open_browser_app_url(browser_bundle_id, url)


@router.post('/close_app', name='关闭app')
def close_app(package_bundle_id):
    return ios.close_app(package_bundle_id)


@router.post('/click_element', name='点击元素')
def click_app_by_element(element, find_type='xpath'):
    return ios.element_click(element, find_type)


@router.post('/click_loc', name='点击坐标')
def click_app_by_loc(x, y):
    return ios.coordinate_click(x, y)


@router.post('/click_hold_element', name='长按点击元素')
def click_hold_app_by_element(element, find_type='xpath', hold_time=1.0):
    return ios.element_click_hold(element=element, find_type=find_type, hold_time=hold_time)


@router.post('/click_hold_loc', name='长按点击坐标')
def click_hold_app_by_loc(x, y, hold_time):
    return ios.coordinate_click_hold(x, y, hold_time)


@router.post('/double_click_loc', name='双击坐标')
def double_click_by_loc(x, y):
    return ios.coordinate_double_click(x, y)


@router.post('/send_text', name='向元素输入文本/字符')
def send_keys_to_element(element, value, find_type='xpath'):
    return ios.element_send_text(element=element, find_type=find_type, value=value)


@router.post('/swipe_element', name='滑动元素')
def swipe_element(element, direction, find_type='xpath'):
    return ios.element_swipe(element=element, find_type=find_type, direction=direction)


@router.post('/turn_page', name='app翻页')
def app_turn_page(direction):
    return ios.app_turn_page(direction=direction)


@router.post('/assert_element_exists', name='断言：元素是否存在')
def app_element_exists(element, timeout, find_type='xpath'):
    return ios.element_exists(element, timeout, find_type)


@router.post('/assert_text_equal', name='断言：元素文本是否一致')
def app_element_text_equal(element, text, find_type='xpath'):
    return ios.element_text_equal_text(element, text, find_type)


@router.post('/assert_alert_exist', name='断言：是否存在系统弹窗')
def checkout_alert_exist():
    """
    断言警告弹窗是否存在
    """
    return ios.checkout_alert_exists()


@router.post('/assert_alert_text', name='断言：系统弹窗文本是否一致')
def checkout_alert_text(text):
    """
    断言警告弹窗文本
    """
    return ios.checkout_alert_text_assert(text)


@router.post('/get_element_attributes', name='获取对应属性值')
def get_element_attributes(element, attributes, find_type='xpath'):
    return ios.get_element_attributes(element=element, attributes=attributes, find_type=find_type)


@router.post('/test_clean', name='清理')
def test_clean():
    pass
