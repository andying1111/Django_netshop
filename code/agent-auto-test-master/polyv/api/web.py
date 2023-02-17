#!/usr/bin/env python
# coding=utf-8

from fastapi import APIRouter, FastAPI

from polyv.common.data_format import DataFormat
from polyv.scripts.web_driver import WebDriverAgent

router = APIRouter()
df = DataFormat()
web = WebDriverAgent()


@router.post('/new', name='创建浏览器对象')
def new(definition_driver_alias, mobile=False, width=0, height=0, use_interceptor=False, virtual_camera=False):
    return web.new_browser(definition_driver_alias, mobile, width, height, use_interceptor, virtual_camera)


@router.get('/check_running_browser', name='查询正在运行中的浏览器总数')
def check_running_browser():
    return web.check_the_running_browser()


@router.post('/open', name='打开URL')
def open_url(url, alias=None):
    return web.open_url(alias, url)


@router.post('/click', name='点击')
def click(element, tag='text', alias=None, index=0):
    return web.click(alias, tag, element, index)


@router.post('/move_to_element', name='移动鼠标焦点')
def move_to_element(element, tag='text', alias=None, index=0):
    return web.move_to_element(alias, tag, element, index)


@router.post('/scroll_to_element', name='滚动页面到某元素')
def scroll_to_element(element, tag='text', alias=None, index=0):
    return web.scroll_to_element(alias, tag, element, index)


@router.post('/drop_element_by_offset', name='拖拽网页元素')
def drop_element_by_offset(element, x_offset, y_offset=0, tag='text', alias=None, index=0):
    return web.drop_element_by_offset(alias, x_offset, y_offset, tag, element, index)


@router.post('/input', name='输入')
def input_data(element, value, tag='text', alias=None, is_clear: bool = True, index=0):
    return web.input(alias, tag, element, value, is_clear, index)


@router.post('/upload_file', name='上传文件')
def input_data(element, file_name, file_path, tag='text', alias=None, index=0):
    return web.upload_file(alias, tag, element, file_name, file_path, index)


@router.post('/parse_xlsx_sheet', name='解析xlsx文件的sheet表')
def parse_xlsx_sheet(xlsx_name, sheet_name):
    return web.parse_xlsx_sheet(xlsx_name, sheet_name)


@router.post('/un_gz', name='解压.gz')
def web_un_csv_gz(gz_file_name):
    return web.web_un_gz(gz_file_name)


@router.post('/parse_csv', name='解析.csv')
def parse_csv(csv_file_name):
    return web.parse_csv(csv_file_name)


@router.post('/clear', name='清空Input数据')
def clear(element, tag='xpath', alias=None, index=0):
    return web.clear_input_box(alias, tag, element, index)


@router.post('/close', name='关闭当前标签页')
def close_current_tab(alias):
    return web.close(alias)


@router.post('/get_window_position', name='获取浏览器窗口坐标')
def get_window_position(alias):
    return web.get_window_position(alias)


@router.post('/set_window_position', name='设置浏览器窗口坐标')
def get_window_position(alias, x, y):
    return web.set_window_position(alias, x, y)


@router.get('/get_window_size', name='浏览器大小')
def get_window_size(alias):
    return web.get_window_size(alias)


@router.post('/quit', name='杀死当前浏览器')
def all_browser_quit(alias):
    return web.quit(alias)


@router.post('/test_clean', name='清理全部浏览器')
def test_clean():
    return web.quit_all_browser()


@router.post('/refresh', name='刷新页面')
def refresh(alias=None):
    return web.refresh(alias)


@router.post('/set_global_find_tolerance', name='设置全局find参数')
def set_tolerance(customer_tolerance, customer_step_time=0.5):
    return web.set_global_find_tolerance(customer_tolerance, customer_step_time)


@router.post('/assert_text', name='文本断言')
def assert_text(element, assert_text, assert_mode="all", tag="text", alias=None, index=0):
    return web.assert_text(alias, element, assert_text, assert_mode, tag, index)


@router.post('/assert_image', name='图片断言')
def assert_image(image_a, image_b, assert_value=0.0):
    return web.image_fuzzy_matching(image_a, image_b, assert_value)


@router.post('/wait_element', name='等待元素出现')
def wait_element(element, tag, times=5, alias=None, index=0):
    return web.wait_element(alias, tag, element, times, index)


@router.post('/elementexist', name='查询元素是否存在')
def element_exist(element, tag='text', alias=None, index=0, timeout=60):
    return web.elementexist(alias, tag, element, index, timeout=timeout)


@router.post('/isenabled', name='查询元素是否可用')
def is_enabled(element, tag='text', alias=None, index=0):
    return web.is_this_element_enabled(alias, tag, element, index)


@router.post('/isdisplayed', name='查询元素是否显示')
def is_displayed(element, tag='text', alias=None, index=0):
    return web.is_this_element_displayed(alias, tag, element, index)


@router.post('/isselected', name='查询元素是否被选中')
def is_selected(element, tag='text', alias=None, index=0):
    return web.is_this_element_selected(alias, tag, element, index)


@router.get('/gettitle', name='获取当前标签页的标题')
def get_title(alias=None):
    return web.get_this_tab_title(alias)


@router.get('/geturl', name='获取当前标签页的url')
def get_url(alias=None):
    return web.get_current_url(alias)


@router.post('/window_to_max', name='对应窗口最大化')
def goto_window(alias=None):
    return web.window_to_max(alias)


@router.post('/window_to_min', name='对应窗口最小化')
def goto_window(alias=None):
    return web.window_to_min(alias)


@router.get('/get_window_handle', name='获取当前窗口的Handle')
def get_current_windows_handle(alias=None):
    return web.get_current_tab_handle(alias)


@router.get('/get_all_tab_handles', name='获取浏览器所有标签页的Handle')
def get_all_tab_handles(alias=None):
    return web.get_all_tab_handles(alias)


@router.post('/goto_window', name='根据Handle跳转到对应窗口')
def goto_window(handle, alias=None):
    return web.goto_window(alias, handle)


@router.post('/timeout', name='设置全局隐性等待时间')
def set_global_implicity_wait(global_timeout):
    return web.set_global_implicity_wait(global_timeout)


@router.post('/screen_shot', name='网页全屏截图')
def screen_shot(name=None, alias=None):
    return web.screen_shot(alias, name)


@router.post('/screenshot_as_base64', name='网页全屏截图, 返回base64图片数据')
def get_screenshot_as_base64(alias=None):
    return web.get_screenshot_as_base64(alias)


@router.post('/element_screen_shot', name='元素截图')
def element_screen_shot(element, tag, name=None, alias=None, index=0):
    return web.element_screenshot(alias, tag, element, name, index)


@router.get('/getattribute', name='查询HTML属性')
def get_attribute(element, attribute_name, tag='text', alias=None, index=0):
    return web.get_element_attribute(alias, tag, element, attribute_name, index)


@router.get('/get_value_css_property', name='查询CSS属性值')
def get_value_css_property(element, css_property, tag='classname', alias=None, index=0):
    return web.get_element_value_of_css_property(alias, element, css_property, tag, index)


@router.get('/get_element_size', name='查询元素的大小')
def get_element_size(element, tag='text', alias=None, index=0):
    return web.get_element_size(alias, tag, element, index)


@router.get('/get_all_keys', name='查询键盘按键的映射键位信息')
def get_all_keys():
    return web.get_all_keys()


@router.get('/get_element_numbers', name='断言元素数量')
def get_element_numbers(element, assert_number, tag='text', alias=None):
    return web.assert_element_numbers(alias, tag, element, assert_number)


@router.get('/loop_wait_element_exist', name='轮询等待元素存在')
def loop_wait_element_exist(element, timeout: int = 100, tag='text', alias=None):
    return web.loop_wait_element_exist(alias, tag, element, timeout)


@router.get('/loop_wait_element_not_exist', name='轮询等待元素不存在')
def loop_wait_element_not_exist(element, timeout: int = 100, tag='text', alias=None):
    return web.loop_wait_element_not_exist(alias, tag, element, timeout)


@router.get('/get_numbers', name='查询元素数量')
def get_numbers(element, tag='text', alias=None):
    return web.get_element_numbers(alias, tag, element)


@router.post('/presskeyboard', name='键盘单个按键')
def press_keyboard(key, alias=None):
    return web.press(alias, key)


@router.post('/presskeyboardcombination', name='键盘2个按键组合')
def press_keyboard_combination(key1, key2, alias=None):
    return web.press_combination(alias, key1, key2)


@router.get('/alert_accept', name='弹出框点击确认')
def alert_accept(alias=None):
    return web.alert_accept(alias)


@router.get('/alert_dismiss', name='弹出框点击取消')
def alert_dismiss(alias=None):
    return web.alert_dismiss(alias)


@router.get('/alert_get_text', name='获取弹出框的文本信息')
def alert_get_text(alias=None):
    return web.alert_get_text(alias)


@router.get('/tag_name', name='获取标签的类型')
def get_tag_name(element, tag='text', alias=None, index=0):
    return web.get_tag_name(alias, element, tag, index)


# @router.get('/get_current_tab_handle', name='获取浏览器当前Tab页的句柄')
# def get_current_tab_handle(alias=None):
#     return web.get_current_tab_handle(alias)


@router.post('/select_by_visible_text', name='通过下拉框的文本信息进行选择')
def select_by_visible_text(element, text, tag='text', alias=None, index=0):
    return web.select_by_visible_text(alias, element, tag, text, index)


@router.post('/select_by_value', name='通过下拉框的Value属性进行选择')
def select_by_value(element, tag, value, alias=None, index=0):
    return web.select_by_value(alias, element, tag, value, index)


@router.post('/select_by_index', name='通过下拉框的索引进行选择(参数select_index默认取0)')
def select_by_index(element, tag='text', select_index=0, alias=None, index=0):
    return web.select_by_index(alias, element, tag, select_index, index)


@router.post('/goto_default_content', name='切换到默认主文档区域')
def goto_default_content(alias=None):
    return web.goto_default_content(alias)


@router.post('/gotoframe', name='切换到指定的iframe')
def goto_frame(element, tag, alias=None, index=0):
    return web.goto_frame(alias, element, tag, index)


@router.post('/goto_parent_frame', name='切换到父级iframe')
def goto_parent_frame(alias=None, index=0):
    return web.goto_parent_frame(alias, index)


# Mouselkclick-模拟鼠标左键单击(可带页面对象)', 'mouselkclick',
# Mouserkclick-模拟鼠标右键单击(可带页面对象)', 'mouserkclick',
# Mousedclick-模拟鼠标双击(可带页面对象)', 'mousedclick',
# Mouseclickhold-模拟鼠标左键单击后不释放(可带页面对象)', 'mouseclickhold',
# Mousedrag-模拟鼠标拖拽(可带页面对象)', 'mousedrag'
# Mouseto-模拟鼠标移动到指定坐标(可带页面对象)', 'mouseto'
# Mouserelease-模拟鼠标释放(可带页面对象)', 'mouserelease'

# Mousekey(tab)-模拟键盘Tab键', 'presstab',

# Mousekey(space)-模拟键盘Space键', 'pressspace', 
# Mousekey(ctrl)-模拟键盘Ctrl键', 'pressctrl', 
# Mousekey(shift)-模拟键盘Shift键', 'pressshift', 
# Mousekey(enter)-模拟键盘Enter键', 'mousekey(enter)'


@router.post('/execute_js', name='执行js代码')
def execute_js(js_code, async_mode=False, alias=None):
    return web.execute_js(alias, js_code, async_mode)


@router.post('/automatically_drag_the_slider', name='自动拖动滑块')
def automatically_drag_the_slider(element_id, alias=None):
    return web.automatically_drag_the_slider(alias, element_id)


@router.post('/delete_all_cookies', name='清空cookies')
def delete_all_cookies(alias=None):
    return web.delete_all_cookies(alias)


@router.delete('/clear_interceptor', name='清空拦截器配置')
def clear_interceptor():
    return web.clear_interceptor()


@router.post('/set_interceptor', name='设置拦截器配置')
def set_interceptor(section, original_link, target_link):
    return web.set_interceptor(section, original_link, target_link)


@router.get('/get_interceptor_alias_name', name='获取拦截器设置别名列表')
def get_interceptor_alias_name():
    return web.get_interceptor_alias_name()


if __name__ == "__main__":
    app = FastAPI()
    app.include_router(router, prefix="/api/web")
    uvicorn.run(app=app, host="0.0.0.0", port=8081, workers=1)
